"""Client du portail VertIA : même ligne de commande et mêmes sorties que l'ancien worker ACE-Step local."""
import argparse
import hashlib
import json
import os
import random
import re
import struct
import subprocess
import time
import urllib.request
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

OUT = os.path.join(ROOT, cfg["output_dir"])
OUT_REL = os.path.normpath(cfg["output_dir"]).replace(os.sep, "/")
os.makedirs(OUT, exist_ok=True)

VERTIA = os.environ.get("VERTIA_DIR", r"D:\ServOMorph\VertIA_v3")
VERTIA_PY = os.path.join(VERTIA, ".venv", "Scripts", "python.exe")
VERTIA_GEN = os.path.join(VERTIA, "vertia_gen.py")
VERTIA_PORT = os.environ.get("VERTIA_PORT", "4310")
SESSION = "creazik"
TIMEOUT_S = int(os.environ.get("CREAZIK_VERTIA_TIMEOUT", "3600"))
FFMPEG_AUDIO = r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe"
SECTION_SECONDS = 14.5
MODEL = "ACE-Step 1.5 turbo" + (" + LM 0.6B" if args.lm else "")

only = {s for s in args.only.split(",") if s}
cases = [c for c in cfg["test_cases"] if not only or c["id"] in only]

results = {
    "timestamp": datetime.now().isoformat(),
    "mode": "real",
    "playlist": cfg.get("playlist_name", ""),
    "model": MODEL,
    "generations": [],
}
results_path = os.path.join(OUT, "playlist_results.json")


def write_json(path, data):
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temporary_path, path)


def save():
    write_json(results_path, results)


def vertia(*cli, timeout=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run([VERTIA_PY, VERTIA_GEN, *cli], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=timeout,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    ident = next((l[3:] for l in proc.stderr.splitlines() if l.startswith("id=")), "")
    return proc.returncode, proc.stdout.splitlines(), ident, proc.stderr.strip()


def upload(path):
    vertia("capacites", timeout=900)
    ext = os.path.splitext(path)[1].lstrip(".")
    with open(path, "rb") as f:
        req = urllib.request.Request(f"http://127.0.0.1:{VERTIA_PORT}/api/v1/inbox?extension={ext}", data=f.read(),
                                     headers={"Content-Type": "application/octet-stream"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["nom"]


def wav_info(path):
    with open(path, "rb") as f:
        head = f.read(12)
        if head[:4] != b"RIFF" or head[8:] != b"WAVE":
            raise ValueError("WAV RIFF attendu")
        fmt = None
        while chunk := f.read(8):
            name, size = chunk[:4], struct.unpack("<I", chunk[4:])[0]
            if name == b"fmt ":
                fmt = struct.unpack("<HHIIHH", f.read(16))
                f.seek(size - 16 + size % 2, 1)
            elif name == b"data" and fmt:
                channels, rate, align = fmt[1], fmt[2], fmt[4]
                frames = size // align
                return {"sample_rate": rate, "channels": channels, "frames": frames, "duration_seconds": frames / rate}
            else:
                f.seek(size + size % 2, 1)
    raise ValueError("bloc fmt ou data absent")


def write_generation_trace(entry, case, request, meta):
    audio_path = os.path.join(ROOT, entry["output_file"])
    relative_base = os.path.splitext(entry["output_file"])[0]
    metadata_rel = f"{relative_base}.metadata.json"
    metadata_path = os.path.join(ROOT, metadata_rel)
    output = {"path": entry["output_file"], "format": os.path.splitext(audio_path)[1].lstrip(".")}
    if os.path.isfile(audio_path):
        output["size_bytes"] = os.path.getsize(audio_path)
        with open(audio_path, "rb") as audio_file:
            output["sha256"] = hashlib.file_digest(audio_file, "sha256").hexdigest()
        try:
            output.update(wav_info(audio_path))
        except Exception as error:
            output["audio_probe_error"] = str(error)
    params = meta.get("params") or {}
    metadata = {
        "generated_at": entry.get("generated_at"), "model_name": results["model"],
        "model_version": "ACE-Step 1.5 / acestep-v15-turbo" + (" + acestep-5Hz-lm-0.6B" if args.lm else ""),
        "model_revision": meta.get("model_revision", "non disponible"), "runtime": meta.get("runtime", {}),
        "vertia": {"session": SESSION, "demande_id": entry.get("vertia_id"), "capacite": "musique.generer"},
        "test_case_id": case["id"], "title": case.get("name", ""),
        "prompt": params.get("caption", case["prompt"]), "lyrics": params.get("lyrics", request.get("paroles", "")),
        "input_files": [case["lyrics_file"]] if case.get("lyrics_file") else [],
        "case_config": case,
        "generation_config": {
            "params": params, "runner": meta.get("generation_config", {}), "vertia_request": request,
            "worker": {"steps": args.steps, "lm_enabled": args.lm, "batch_size": 1,
                       "audio_format": "wav", "random_seed": False, "elapsed_seconds": entry.get("elapsed_s")},
        },
        "output": output, "status": entry.get("status"), "error": entry.get("error"),
        "listening_review": {"status": "pending"},
    }
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    write_json(metadata_path, metadata)
    entry["metadata_file"] = metadata_rel.replace(os.sep, "/")

    manifest_path = os.path.join(OUT, "generation_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
    except (OSError, json.JSONDecodeError):
        manifest = {"playlist": cfg.get("playlist_name", ""), "model": results["model"], "tracks": []}
    manifest["updated_at"] = entry.get("generated_at") or datetime.now().astimezone().isoformat(timespec="seconds")
    manifest["model_revision"] = metadata["model_revision"]
    manifest["tracks"] = [track for track in manifest.get("tracks", [])
                          if track.get("output_file") != entry["output_file"]]
    manifest["tracks"].append({"test_case_id": case["id"], "name": case.get("name", ""),
                               "output_file": entry["output_file"], "metadata_file": entry["metadata_file"],
                               "generated_at": entry.get("generated_at"), "status": entry.get("status"),
                               "error": entry.get("error")})
    write_json(manifest_path, manifest)


def fit_lyrics(text, duration):
    sections = [p for p in re.split(r"(?m)^(?=\[)", text) if p.strip()]
    if len(sections) <= 3:
        return text
    target = max(3, min(len(sections), round(duration / SECTION_SECONDS)))
    if target >= len(sections):
        return text
    kept = sections[:target - 1] + [sections[-1]]
    return "\n".join(p.strip("\n") + "\n" for p in kept)


def prepare_audio(path, start=None, dur=None):
    """Convertit un fichier audio partage (mp3, mp4...) en WAV 48 kHz, decoupe si demande."""
    src = os.path.abspath(path)
    if not os.path.isfile(src):
        raise SystemExit(f"audio partage introuvable : {src}")
    refs = os.path.abspath(os.path.join(OUT, "..", "refs"))
    os.makedirs(refs, exist_ok=True)
    tag = hashlib.sha1(f"{src}|{start}|{dur}|{os.path.getmtime(src)}".encode()).hexdigest()[:10]
    dst = os.path.join(refs, f"{os.path.splitext(os.path.basename(src))[0][:40]}_{tag}.wav")
    if not os.path.isfile(dst):
        cmd = [FFMPEG_AUDIO, "-y", "-loglevel", "error"]
        if start:
            cmd += ["-ss", str(start)]
        if dur:
            cmd += ["-t", str(dur)]
        cmd += ["-i", src, "-vn", "-ac", "2", "-ar", "48000", dst]
        subprocess.run(cmd, check=True)
    return dst


def load_lyrics(case):
    if case.get("lyrics_file"):
        with open(os.path.join(ROOT, case["lyrics_file"]), "r", encoding="utf-8") as f:
            text = f.read()
        if case.get("fit_lyrics", True):
            return fit_lyrics(text, case["duration"])
        return text
    return case.get("lyrics", "")


def effective_seed(case):
    seed = case.get("seed")
    if isinstance(seed, int) and 0 <= seed < 2 ** 32:
        return seed
    return random.SystemRandom().randint(0, 2 ** 32 - 1)


def build_request(case, seed):
    instrumental = case["type"] == "instrumental"
    request = {
        "paroles": "" if instrumental else load_lyrics(case), "instrumental": instrumental,
        "langue": case.get("language", "en"), "duree": case["duration"], "seed": seed,
        "etapes": args.steps, "lm": args.lm, "ajuster_paroles": False,
    }
    if case.get("task_type"):
        request["tache"] = str(case["task_type"])
    for key, name in (("reference_audio", "reference"), ("src_audio", "source")):
        if case.get(key):
            request[name] = upload(prepare_audio(case[key], case.get("audio_start_s"), case.get("audio_duration_s")))
    if case.get("cover_noise_strength") is not None:
        request["force_cover"] = float(case["cover_noise_strength"])
    if case.get("audio_cover_strength") is not None:
        request["force_audio"] = float(case["audio_cover_strength"])
    if case.get("bpm"):
        request["bpm"] = int(case["bpm"])
    if case.get("keyscale"):
        request["tonalite"] = str(case["keyscale"])
    if case.get("timesignature"):
        request["mesure"] = str(case["timesignature"])
    return request


def generate(case, entry):
    request = build_request(case, entry["seed"])
    cli = ["musique", "--session", SESSION, "--prompt", case["prompt"], "--essais", "1",
           "--timeout", str(TIMEOUT_S), "--param"]
    cli += [f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in request.items()]
    code, paths, ident, err = vertia(*cli, timeout=TIMEOUT_S + 120)
    entry["vertia_id"] = ident
    wav = next((p for p in paths if p.lower().endswith(".wav")), "")
    if code != 0 or not wav or not os.path.isfile(wav):
        raise RuntimeError(f"portail VertIA code {code} : {err[-300:]}")
    meta = {}
    meta_path = next((p for p in paths if p.lower().endswith(".json")), "")
    if meta_path:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    with open(wav, "rb") as src, open(os.path.join(ROOT, entry["output_file"]), "wb") as dst:
        dst.write(src.read())
    if ident:
        vertia("retour", ident, "valide", timeout=120)
    return request, meta


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
    attempt_at = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f")
    attempt_seed = effective_seed(case)
    entry = {
        "test_case_id": case["id"],
        "name": case["name"],
        "prompt": case["prompt"],
        "type": case["type"],
        "duration": case["duration"],
        "output_file": f"{OUT_REL}/{int(case['id']):02d}_{slug}_{attempt_at}_s{attempt_seed}.wav",
        "seed": attempt_seed,
        "seed_source": "config" if attempt_seed == case.get("seed") else "tiree_par_worker",
        "status": "pending",
    }
    all_entries.append(entry)
    if case["id"] in selected:
        entries.append(entry)
results["generations"] = all_entries
save()

for i, (case, entry) in enumerate(zip(cases, entries), 1):
    entry["status"] = "running"
    save()
    print(f"[{i}/{len(cases)}] {case['name']} ({case['type']})", flush=True)
    t0 = time.time()
    request, meta = {}, {}
    try:
        request, meta = generate(case, entry)
        entry["status"] = "generated"
        entry["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        entry["model"] = results["model"]
        for key in ("energy_wh_est", "gpu_util_avg_pct"):
            if meta.get(key) is not None:
                entry[key] = meta[key]
    except Exception as e:
        entry["status"] = "failed"
        entry["error"] = str(e)[:300]
    entry["elapsed_s"] = round(time.time() - t0, 1)
    entry.setdefault("generated_at", datetime.now().astimezone().isoformat(timespec="seconds"))
    write_generation_trace(entry, case, request, meta)
    print(f"    -> {entry['status']} en {entry['elapsed_s']}s {entry.get('error', '')}", flush=True)
    save()

print("Terminé.", flush=True)
