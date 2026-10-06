import argparse
import struct
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).parent
FFMPEG = Path(r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe")
BITRATE = "192k"


def targets():
    for wav in HERE.glob("playlists/*/outputs/*.wav"):
        if any(p.startswith("_") for p in wav.relative_to(HERE).parts):
            continue
        yield wav


def wav_seconds(path):
    with open(path, "rb") as f:
        head = f.read(65536)
    pos = 12
    byte_rate = None
    while pos + 8 <= len(head):
        cid = head[pos:pos + 4]
        size = struct.unpack("<I", head[pos + 4:pos + 8])[0]
        if cid == b"fmt ":
            byte_rate = struct.unpack("<I", head[pos + 16:pos + 20])[0]
        elif cid == b"data" and byte_rate:
            return (path.stat().st_size - (pos + 8)) / byte_rate
        pos += 8 + size + (size & 1)
    return None


def purge(wav):
    mp3 = wav.with_suffix(".mp3")
    if not mp3.exists() or mp3.stat().st_mtime < wav.stat().st_mtime:
        return False
    if time.time() - wav.stat().st_mtime < 60:
        return False
    for suffix in (".viz.json", ".feat.json"):
        side = wav.with_name(wav.name + suffix)
        if not side.exists() or side.stat().st_mtime < wav.stat().st_mtime:
            return False
    expected = wav_seconds(wav)
    actual = mp3.stat().st_size * 8 / (int(BITRATE[:-1]) * 1000)
    if not expected or abs(actual - expected) > max(1.5, expected * 0.03):
        print(f"conservé {wav.name} : durée mp3 incohérente ({actual:.1f} s pour {expected} s)", flush=True)
        return False
    try:
        wav.unlink()
    except PermissionError:
        return False
    print(f"wav supprimé {wav.relative_to(HERE)}", flush=True)
    return True


def convert(wav):
    mp3 = wav.with_suffix(".mp3")
    if mp3.exists() and mp3.stat().st_mtime >= wav.stat().st_mtime:
        return False
    if time.time() - wav.stat().st_mtime < 5:
        return False
    tmp = mp3.with_name(mp3.stem + ".tmp.mp3")
    cmd = [str(FFMPEG), "-y", "-loglevel", "error", "-i", str(wav), "-vn", "-codec:a", "libmp3lame",
           "-b:a", BITRATE, "-ar", "44100", "-id3v2_version", "3", str(tmp)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not tmp.exists():
        print(f"echec {wav.name} : {res.stderr.strip()[:200]}", flush=True)
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(mp3)
    print(f"converti {wav.relative_to(HERE)} -> {mp3.stat().st_size // 1024} Ko", flush=True)
    return True


def run_once():
    done = 0
    for wav in list(targets()):
        if convert(wav):
            done += 1
        if purge(wav):
            done += 1
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="relance toutes les 60 s")
    a = ap.parse_args()
    if not FFMPEG.exists():
        raise SystemExit(f"ffmpeg introuvable : {FFMPEG}")
    if a.watch:
        while True:
            run_once()
            time.sleep(20)
    else:
        print(run_once(), "fichier(s) converti(s)")
