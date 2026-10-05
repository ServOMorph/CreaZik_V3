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

ONSET_HOP_S = 0.02
ONSET_FFT = 1024
BPM_MIN = 55.0
BPM_MAX = 200.0
BPM_PRIOR_CENTER = 115.0
BPM_PRIOR_OCTAVES = 0.9


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
    elif tag == 1 and bits == 8:
        arr = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"format non géré : tag={tag} bits={bits}")
    arr = arr[:len(arr) // ch * ch].reshape(-1, ch).mean(axis=1)
    return arr, sr


def analyze(path):
    x, sr = read_wav(path)
    return spectral_profile(x, sr)


def spectral_profile(x, sr):
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


def onset_envelope(x, sr):
    hop = max(1, int(sr * ONSET_HOP_S))
    n_frames = max(2, (len(x) - ONSET_FFT) // hop)
    idx = np.arange(ONSET_FFT)[None, :] + (np.arange(n_frames) * hop)[:, None]
    win = np.hanning(ONSET_FFT).astype(np.float32)
    mag = np.abs(np.fft.rfft(x[idx] * win, axis=1))
    comp = np.log1p(20.0 * mag)
    flux = np.maximum(0.0, comp[1:] - comp[:-1]).sum(axis=1)
    return flux, hop / sr, mag


def estimate_bpm(flux, frame_s):
    env = flux - flux.mean()
    if len(env) < 64 or not np.any(env):
        return None, 0.0
    n = len(env)
    size = 1 << (2 * n - 1).bit_length()
    f = np.fft.rfft(env, size)
    ac = np.fft.irfft(f * np.conj(f))[:n]
    ac = ac / (ac[0] + 1e-9)
    lags = np.arange(n) * frame_s
    bpms = np.zeros(n)
    bpms[1:] = 60.0 / lags[1:]
    valid = (bpms >= BPM_MIN) & (bpms <= BPM_MAX)
    if not valid.any():
        return None, 0.0
    prior = np.exp(-0.5 * (np.log2(np.maximum(bpms, 1e-6) / BPM_PRIOR_CENTER) / BPM_PRIOR_OCTAVES) ** 2)
    score = np.where(valid, ac * prior, -np.inf)
    k = int(np.argmax(score))
    if 1 <= k < n - 1:
        a, b, c = ac[k - 1], ac[k], ac[k + 1]
        denom = a - 2 * b + c
        shift = 0.5 * (a - c) / denom if abs(denom) > 1e-9 else 0.0
        lag = (k + float(np.clip(shift, -0.5, 0.5))) * frame_s
    else:
        lag = k * frame_s
    bpm = 60.0 / lag
    confidence = float(max(0.0, ac[k]))
    return float(bpm), confidence


def features(path):
    x, sr = read_wav(path)
    flux, frame_s, mag = onset_envelope(x, sr)
    bpm, conf = estimate_bpm(flux, frame_s)
    freqs = np.fft.rfftfreq(ONSET_FFT, 1.0 / sr)
    energy_per_frame = mag.sum(axis=1) + 1e-9
    centroid = float(np.mean((mag * freqs[None, :]).sum(axis=1) / energy_per_frame))
    rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)
    block = max(1, int(sr * 0.5))
    n_blocks = len(x) // block
    if n_blocks >= 2:
        r = np.sqrt((x[:n_blocks * block].reshape(n_blocks, block) ** 2).mean(axis=1)) + 1e-9
        dyn = float(np.std(20 * np.log10(r)))
    else:
        dyn = 0.0
    return {"bpm": None if bpm is None else round(bpm, 1), "bpm_confidence": round(conf, 2),
            "onset": round(float(flux.mean()), 3), "centroid_hz": round(centroid, 1),
            "rms_db": round(20 * np.log10(rms), 2), "dynamic_db": round(dyn, 2),
            "duration_s": round(len(x) / sr, 2)}


def targets():
    for wav in HERE.glob("**/*.wav"):
        parts = wav.relative_to(HERE).parts
        if any(p.startswith("_") for p in parts):
            continue
        yield wav


def stale(out, wav):
    return not out.exists() or out.stat().st_mtime < wav.stat().st_mtime


def write_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)


def run_once():
    done = 0
    for wav in targets():
        if time.time() - wav.stat().st_mtime < 5:
            continue
        viz = wav.with_name(wav.name + ".viz.json")
        feat = wav.with_name(wav.name + ".feat.json")
        try:
            if stale(viz, wav):
                write_json(viz, analyze(wav))
                done += 1
                print(f"profil {wav.relative_to(HERE)}", flush=True)
            if stale(feat, wav):
                write_json(feat, features(wav))
                done += 1
                print(f"caractéristiques {wav.relative_to(HERE)}", flush=True)
        except Exception as e:
            print(f"échec {wav.name} : {e}", flush=True)
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
        print(run_once(), "fichier(s) produit(s)")
