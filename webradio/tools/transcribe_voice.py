import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from transformers import pipeline

ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    return re.sub(r"[^a-zà-ÿ0-9 ]+", "", s.lower()).split()


def load16k(path):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    mono = data.mean(axis=1)
    n = int(len(mono) * 16000 / sr)
    return np.interp(np.linspace(0, len(mono) - 1, n), np.arange(len(mono)), mono).astype(np.float32)


def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / max(1, len(r))


def main():
    folder = Path(sys.argv[1])
    texts = json.loads((ROOT / "voice_jingles.json").read_text(encoding="utf-8"))["texts"]
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=-1)
    rows = []
    for i, ref in enumerate(texts, 1):
        wav = folder / f"{i:02d}_voix.wav"
        if not wav.exists():
            continue
        hyp = asr({"raw": load16k(wav), "sampling_rate": 16000}, generate_kwargs={"language": "fr", "task": "transcribe"})["text"]
        w = wer(ref, hyp)
        rows.append(w)
        print(f"{i:02d} erreur mots {w * 100:4.0f} % | {hyp.strip()}")
    if rows:
        print(f"moyenne : {sum(rows) / len(rows) * 100:.0f} % d'erreurs de mots sur {len(rows)} jingles")


if __name__ == "__main__":
    main()
