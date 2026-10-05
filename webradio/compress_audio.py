import argparse
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
    return sum(1 for wav in targets() if convert(wav))


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
