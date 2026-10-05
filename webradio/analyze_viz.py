import argparse
import json
import struct
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
HOP_S = 0.1
N_BANDS = 16
FFT = 4096
F_MIN = 40.0
F_MAX = 16000.0


def read_wav(path):
    data = Path(path).read_bytes()
    pos = 12
    fmt = None
    raw = b""
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = pos + 8
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", data[body:body + 16])
        elif cid == b"data":
            size = min(size, len(data) - body)
            raw = data[body:body + size]
            break
        pos = body + size + (size & 1)
    if fmt is None or not raw:
        raise ValueError("wav illisible")
    tag, ch, sr, _, _, bits = fmt
    if tag == 3 and bits == 32:
        arr = np.frombuffer(raw[:len(raw) // 4 * 4], dtype="<f4")
    elif tag == 1 and bits == 16:
        arr = np.frombuffer(raw[:len(raw) // 2 * 2], dtype="<i2").astype(np.float32) / 32768.0
    else:
        raise ValueError(f"format non géré : tag={tag} bits={bits}")
    arr = arr[:len(arr) // ch * ch].reshape(-1, ch).mean(axis=1)
    return arr, sr


def analyze(path):
    x, sr = read_wav(path)
    hop = int(sr * HOP_S)
    n_frames = max(1, len(x) // hop)
    pad = np.pad(x, (FFT // 2, FFT))
    win = np.hanning(FFT).astype(np.float32)
    idx = np.arange(FFT)[None, :] + (np.arange(n_frames) * hop)[:, None]
    spec = np.abs(np.fft.rfft(pad[idx] * win, axis=1)) ** 2
    freqs = np.fft.rfftfreq(FFT, 1.0 / sr)
    edges = np.geomspace(F_MIN, min(F_MAX, sr / 2 - 1), N_BANDS + 1)
    out = np.zeros((n_frames, N_BANDS), dtype=np.float32)
    for b in range(N_BANDS):
        m = (freqs >= edges[b]) & (freqs < edges[b + 1])
        if m.any():
            out[:, b] = spec[:, m].mean(axis=1)
    db = 10.0 * np.log10(out + 1e-12)
    lo, hi = np.percentile(db, 5), np.percentile(db, 99.5)
    norm = np.clip((db - lo) / max(hi - lo, 1e-6), 0.0, 1.0) * 255.0
    return {"hop": HOP_S, "bands": N_BANDS, "d": [int(v) for v in norm.round().flatten()]}


def targets():
    for wav in HERE.glob("**/*.wav"):
        parts = wav.relative_to(HERE).parts
        if any(p.startswith("_") for p in parts):
            continue
        yield wav


def run_once():
    done = 0
    for wav in targets():
        viz = wav.with_name(wav.name + ".viz.json")
        if viz.exists() and viz.stat().st_mtime >= wav.stat().st_mtime:
            continue
        if time.time() - wav.stat().st_mtime < 5:
            continue
        try:
            res = analyze(wav)
        except Exception as e:
            print(f"échec {wav.name} : {e}", flush=True)
            continue
        tmp = viz.with_suffix(".tmp")
        tmp.write_text(json.dumps(res, separators=(",", ":")), encoding="utf-8")
        tmp.replace(viz)
        done += 1
        print(f"analysé {wav.relative_to(HERE)}", flush=True)
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="relance toutes les 60 s")
    a = ap.parse_args()
    if a.watch:
        while True:
            run_once()
            time.sleep(60)
    else:
        print(run_once(), "fichier(s) analysé(s)")
