import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline

torch.set_num_threads(4)

ROOT = Path(__file__).resolve().parent.parent
PLAYLIST = "jingles-voix"
OUT_DIR = ROOT / "playlists" / PLAYLIST / "outputs"
RATE = 24000
MODEL = "Kokoro-82M (voix locale)"


def fade(wav, seconds):
    n = int(seconds * RATE)
    if len(wav) > 2 * n:
        ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
        wav[:n] *= ramp
        wav[-n:] *= ramp[::-1]
    return wav


def main():
    cfg = json.loads((ROOT / "voice_jingles.json").read_text(encoding="utf-8"))
    texts = cfg["texts"]
    only = {int(x) for x in sys.argv[1:]} if len(sys.argv) > 1 else set()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pipe = KPipeline(lang_code="f", device="cpu")
    results_path = OUT_DIR / "playlist_results.json"
    results = {"playlist": "Jingles parlés", "model": MODEL, "generations": []}
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
    by_id = {g["test_case_id"]: g for g in results["generations"]}
    cases = []
    for i, text in enumerate(texts, 1):
        name = f"Jingle voix {i:02d}"
        rel = f"playlists/{PLAYLIST}/outputs/{i:02d}_voix.wav"
        cases.append({"id": str(i), "name": name, "prompt": text, "type": "voice", "duration": 0})
        if only and i not in only:
            continue
        t0 = time.time()
        chunks = [np.asarray(a, dtype=np.float32) for _, _, a in pipe(text, voice=cfg["voice"], speed=cfg["speed"])]
        wav = np.concatenate(chunks)
        peak = float(np.max(np.abs(wav))) or 1.0
        wav = fade(wav * (0.89 / peak), 0.06)
        wav = np.concatenate([np.zeros(int(0.15 * RATE), dtype=np.float32), wav, np.zeros(int(0.3 * RATE), dtype=np.float32)])
        sf.write(str(ROOT / rel), wav, RATE, subtype="FLOAT")
        dur = len(wav) / RATE
        by_id[str(i)] = {"test_case_id": str(i), "name": name, "prompt": text, "type": "voice",
                         "duration": round(dur, 1), "output_file": rel, "status": "generated",
                         "generated_at": datetime.now().isoformat(), "model": MODEL,
                         "elapsed_s": round(time.time() - t0, 1)}
        print(f"{name} : {dur:.1f} s en {time.time() - t0:.1f} s", flush=True)
    results["generations"] = [by_id[k] for k in sorted(by_id, key=int)]
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    cfg_out = {"playlist_name": "Jingles parlés", "engine": "kokoro", "output_dir": f"./playlists/{PLAYLIST}/outputs",
               "voice": cfg["voice"], "test_cases": cases}
    (ROOT / "playlists" / PLAYLIST / "config.json").write_text(json.dumps(cfg_out, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
