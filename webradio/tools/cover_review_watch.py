import argparse
import os
import subprocess
import sys
import time
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "tools"))

import covers_review  # noqa: E402
import cover_batch  # noqa: E402

LOGS = HERE / "logs"
LOCK = LOGS / "cover_review_watch.lock"
STOP = LOGS / "stop_cover_review.request"


def redo_seed(key, title, attempt):
    return zlib.crc32(f"{key}:{title}:redo{attempt}".encode("utf-8"))


def pending_redos(state_path):
    state = covers_review.read_state(state_path)["items"]
    return [k for k, v in state.items() if v.get("status") == "redo" and int(v.get("redo_count", 0)) < covers_review.MAX_REDO]


def generate_cover(job, seed, temp):
    result = subprocess.run([sys.executable, str(HERE / "tools" / "cover_gen.py"), job["title"], job["style"], str(seed), str(temp)], cwd=HERE)
    return result.returncode == 0 and cover_batch.valid_png(temp)


def process_key(key, jobs, state_path, generator=generate_cover):
    saved = covers_review.read_state(state_path)["items"].get(key, {})
    count = int(saved.get("redo_count", 0))
    job = jobs.get(key)
    if job is None:
        covers_review.update_item(key, {"status": "abandoned", "note": "playlist exclue de la generation de pochettes"}, state_path)
        return "abandoned"
    attempt = count + 1
    seed = redo_seed(key, job["title"], attempt)
    temp = job["target"].with_name(job["target"].stem + ".review.tmp.png")
    temp.unlink(missing_ok=True)
    if generator(job, seed, temp):
        os.replace(temp, job["target"])
        history = list(saved.get("seeds", [])) + [seed]
        covers_review.update_item(key, {"status": "pending", "redo_count": attempt, "seeds": history, "fails": 0, "note": ""}, state_path)
        return "regenerated"
    temp.unlink(missing_ok=True)
    fails = int(saved.get("fails", 0)) + 1
    if fails >= covers_review.MAX_FAILS:
        covers_review.update_item(key, {"status": "error", "fails": fails, "note": "echec de generation repete"}, state_path)
        return "error"
    covers_review.update_item(key, {"fails": fails}, state_path)
    return "failed"


def acquire_lock():
    LOGS.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        old = cover_batch.read_json(LOCK, {}).get("pid")
        try:
            os.kill(int(old), 0)
        except (OSError, TypeError, ValueError):
            LOCK.unlink(missing_ok=True)
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        else:
            raise RuntimeError(f"Le suivi des pochettes tourne deja (PID {old}).")
    os.write(fd, ('{"pid": %d}' % os.getpid()).encode())
    return fd


def main():
    ap = argparse.ArgumentParser(description="Relance la generation des pochettes marquees 'A refaire' dans la section Pochettes.")
    ap.add_argument("--interval", type=int, default=10, help="secondes entre deux lectures de l'etat")
    ap.add_argument("--once", action="store_true", help="traiter les demandes presentes puis s'arreter")
    ap.add_argument("--state", default=str(covers_review.STATE_FILE))
    args = ap.parse_args()
    state_path = Path(args.state)
    fd = acquire_lock()
    STOP.unlink(missing_ok=True)
    comfy_ok = False
    try:
        while not STOP.exists():
            keys = pending_redos(state_path)
            if keys:
                while cover_batch.music_generation_running():
                    if STOP.exists():
                        return 0
                    print("Generation musicale active : attente.", flush=True)
                    time.sleep(10)
                if not comfy_ok:
                    cover_batch.ensure_comfy()
                    comfy_ok = True
                jobs = {j["key"]: j for j in cover_batch.load_jobs()}
                for key in keys:
                    if STOP.exists():
                        break
                    print(f"regeneration {key}", flush=True)
                    print(process_key(key, jobs, state_path), flush=True)
            if args.once:
                return 0
            time.sleep(args.interval)
        return 0
    finally:
        os.close(fd)
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
