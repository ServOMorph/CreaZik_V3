import argparse
import gc
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--config", required=True)
parser.add_argument("--only", default="")
parser.add_argument("--lm", action="store_true")
parser.add_argument("--steps", type=int, default=8)
args = parser.parse_args()

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(args.config, "r", encoding="utf-8") as f:
    cfg = json.load(f)

ACE = os.path.abspath(cfg["ace_step_path"])
OUT = os.path.join(ROOT, cfg["output_dir"])
OUT_REL = os.path.normpath(cfg["output_dir"]).replace(os.sep, "/")
os.makedirs(OUT, exist_ok=True)
os.chdir(ACE)
sys.path.insert(0, ACE)
for v in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    os.environ.pop(v, None)

import torch
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

only = {s for s in args.only.split(",") if s}
cases = [c for c in cfg["test_cases"] if not only or c["id"] in only]

dit = AceStepHandler()
msg, ok = dit.initialize_service(
    project_root=ACE, config_path="acestep-v15-turbo", device="auto", offload_to_cpu=True
)
if not ok:
    sys.exit(f"DiT init failed: {msg}")

llm = LLMHandler()
if args.lm:
    msg, ok = llm.initialize(
        checkpoint_dir=os.path.join(ACE, "checkpoints"),
        lm_model_path="acestep-5Hz-lm-0.6B",
        backend="pt",
        device="auto",
        offload_to_cpu=True,
        dtype=None,
    )
    if not ok:
        sys.exit(f"LLM init failed: {msg}")

results = {
    "timestamp": datetime.now().isoformat(),
    "mode": "real",
    "playlist": cfg.get("playlist_name", ""),
    "model": "ACE-Step 1.5 turbo" + (" + LM 0.6B" if args.lm else ""),
    "generations": [],
}
results_path = os.path.join(OUT, "playlist_results.json")


def save():
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


SECTION_SECONDS = 14.5


IDLE_W = 10.0


class GpuPowerMeter:
    def __init__(self, interval=0.5):
        self.interval = interval
        self.samples = []
        self._stop = threading.Event()
        self._thread = None

    def _read(self):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,power.limit", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5)
            util, limit = [float(x) for x in out.stdout.strip().splitlines()[0].split(",")]
            self.limit_w = limit
            return IDLE_W + (limit - IDLE_W) * util / 100.0, util
        except Exception:
            return None

    def _run(self):
        last = time.time()
        while not self._stop.is_set():
            reading = self._read()
            now = time.time()
            if reading is not None:
                self.samples.append((reading[0], now - last, reading[1]))
            last = now
            self._stop.wait(self.interval)

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        total_s = sum(dt for _, dt, _ in self.samples)
        if not self.samples or total_s <= 0:
            return None
        wh = sum(w * dt for w, dt, _ in self.samples) / 3600.0
        return {"energy_wh_est": round(wh, 3),
                "gpu_util_avg_pct": round(sum(u * dt for _, dt, u in self.samples) / total_s, 1)}


def fit_lyrics(text, duration):
    sections = [p for p in re.split(r"(?m)^(?=\[)", text) if p.strip()]
    if len(sections) <= 3:
        return text
    target = max(3, min(len(sections), round(duration / SECTION_SECONDS)))
    if target >= len(sections):
        return text
    kept = sections[:target - 1] + [sections[-1]]
    return "\n".join(p.strip("\n") + "\n" for p in kept)


def load_lyrics(case):
    if case.get("lyrics_file"):
        with open(os.path.join(ROOT, case["lyrics_file"]), "r", encoding="utf-8") as f:
            text = f.read()
        if case.get("fit_lyrics", True):
            return fit_lyrics(text, case["duration"])
        return text
    return case.get("lyrics", "")


previous = {}
if os.path.exists(results_path):
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            previous = {g["test_case_id"]: g for g in json.load(f).get("generations", [])}
    except Exception:
        previous = {}

selected = {c["id"] for c in cases}
all_entries = []
entries = []
for case in cfg["test_cases"]:
    if case["id"] not in selected and case["id"] in previous:
        all_entries.append(previous[case["id"]])
        continue
    slug = case["name"].replace(" ", "_").replace("/", "-")
    entry = {
        "test_case_id": case["id"],
        "name": case["name"],
        "prompt": case["prompt"],
        "type": case["type"],
        "duration": case["duration"],
        "output_file": f"{OUT_REL}/{int(case['id']):02d}_{slug}.wav",
        "status": "pending",
    }
    all_entries.append(entry)
    if case["id"] in selected:
        entries.append(entry)
results["generations"] = all_entries
save()

for i, (case, entry) in enumerate(zip(cases, entries), 1):
    rel = entry["output_file"]
    entry["status"] = "running"
    save()
    print(f"[{i}/{len(cases)}] {case['name']} ({case['type']})", flush=True)

    instrumental = case["type"] == "instrumental"
    params = GenerationParams(
        task_type="text2music",
        thinking=args.lm,
        caption=case["prompt"],
        lyrics="[Instrumental]" if instrumental else load_lyrics(case),
        instrumental=instrumental,
        vocal_language=case.get("language", "en"),
        duration=case["duration"],
        inference_steps=args.steps,
        guidance_scale=1.0,
        seed=case.get("seed", -1),
    )
    t0 = time.time()
    meter = GpuPowerMeter()
    meter.start()
    try:
        res = generate_music(
            dit, llm, params=params,
            config=GenerationConfig(batch_size=1, audio_format="wav"),
            save_dir=os.path.join(ACE, "output", "creazik"),
        )
        path = res.audios[0]["path"] if res.success and res.audios else ""
        if path and os.path.exists(path):
            shutil.copyfile(path, os.path.join(ROOT, rel))
            entry["status"] = "generated"
            entry["generated_at"] = datetime.now().isoformat()
            entry["model"] = results["model"]
        else:
            entry["status"] = "failed"
            entry["error"] = res.status_message or "aucun fichier produit"
    except Exception as e:
        entry["status"] = "failed"
        entry["error"] = str(e)[:300]
    measure = meter.stop()
    if measure:
        entry.update(measure)
    gc.collect()
    torch.cuda.empty_cache()
    entry["elapsed_s"] = round(time.time() - t0, 1)
    print(f"    -> {entry['status']} en {entry['elapsed_s']}s {entry.get('error', '')}", flush=True)
    save()

print("Terminé.", flush=True)
