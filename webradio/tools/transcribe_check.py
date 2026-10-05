import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from transformers import pipeline

torch.set_num_threads(4)
ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    return re.sub(r"[^a-zà-ÿ0-9 ]+", "", s.lower())


def load(path):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    mono = data.mean(axis=1)
    if sr % 16000 == 0:
        k = sr // 16000
        mono = np.convolve(mono, np.ones(k, dtype=np.float32) / k, mode="same")[::k]
    else:
        n = int(len(mono) * 16000 / sr)
        mono = np.interp(np.linspace(0, len(mono) - 1, n), np.arange(len(mono)), mono).astype(np.float32)
    return mono.astype(np.float32)


def main():
    playlist, case_id, lang = sys.argv[1], sys.argv[2], sys.argv[3]
    cfg = json.loads((ROOT / "playlists" / playlist / "config.json").read_text(encoding="utf-8"))
    case = next(c for c in cfg["test_cases"] if c["id"] == case_id)
    res = json.loads((ROOT / "playlists" / playlist / "outputs" / "playlist_results.json").read_text(encoding="utf-8"))
    gen = next(g for g in res["generations"] if g["test_case_id"] == case_id)
    audio = load(ROOT / gen["output_file"])
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=-1)
    t0 = time.time()
    out = asr({"raw": audio, "sampling_rate": 16000}, chunk_length_s=30, return_timestamps=True,
              generate_kwargs={"language": lang, "task": "transcribe"})
    print(f"{playlist}:{case_id} {gen['name']} | duree audio {len(audio) / 16000:.1f} s | transcription {time.time() - t0:.0f} s")
    lyric_lines = [l.strip() for l in (ROOT / case["lyrics_file"]).read_text(encoding="utf-8").splitlines()
                   if l.strip() and not l.startswith("[")]
    print("lignes de paroles prevues :", len(lyric_lines))
    last_end = 0.0
    for ch in out["chunks"]:
        ts = ch["timestamp"]
        print(f"  {ts[0]:6.1f}-{(ts[1] if ts[1] is not None else float('nan')):6.1f} {ch['text'].strip()}")
        if ts[1]:
            last_end = max(last_end, ts[1])
    heard = norm(" ".join(c["text"] for c in out["chunks"]))
    found = [l for l in lyric_lines if len(norm(l)) > 6 and norm(l)[:18] in heard]
    print(f"lignes retrouvees (approximatif) : {len(found)}/{len(lyric_lines)} | derniere parole entendue a {last_end:.1f} s")
    final_line = lyric_lines[-1]
    print("derniere ligne prevue retrouvee :", norm(final_line)[:18] in heard)


if __name__ == "__main__":
    main()
