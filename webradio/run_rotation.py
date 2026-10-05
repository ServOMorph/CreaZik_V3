import argparse
import json
import subprocess
import time
from pathlib import Path

import run_queue

HERE = Path(__file__).parent


def worker_running():
    cmd = ("(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and "
           "$_.CommandLine -match 'ace_worker\\.py' }).Count")
    res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
    try:
        return int(res.stdout.strip() or 0) > 0
    except ValueError:
        return False


def load_playlist(pid):
    config = HERE / "playlists" / pid / "config.json"
    with open(config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out_dir = (HERE / cfg["output_dir"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    return config, cfg, out_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    def read_ids():
        return [x for x in (HERE / "series.txt").read_text(encoding="utf-8").split() if x]

    abandoned = set()
    while worker_running():
        time.sleep(3)

    run_queue.log("rotation : une piste par playlist et par tour")
    turn = 0
    while True:
        progressed = False
        turn += 1
        ids = read_ids()
        for pid in ids:
            try:
                config, cfg, out_dir = load_playlist(pid)
            except Exception as exc:
                run_queue.log(f"{pid} : configuration illisible ({exc})")
                continue
            results_path = out_dir / "playlist_results.json"
            status = run_queue.results_status(results_path)
            pending = [c for c in cfg["test_cases"]
                       if status.get(c["id"]) != "generated" and (pid, c["id"]) not in abandoned]
            if not pending:
                continue
            case = pending[0]
            cid = case["id"]
            limit = max(90, int(3 * case.get("duration", 30)))
            done = False
            for attempt in range(1, args.retries + 1):
                run_queue.log(f"{pid} piste {cid} : tentative {attempt}/{args.retries} (limite {limit} s)")
                how = run_queue.run_one(config, cid, limit, out_dir)
                status = run_queue.results_status(results_path).get(cid)
                run_queue.log(f"{pid} piste {cid} : fin ({how}), statut {status}")
                if status == "generated":
                    done = True
                    break
                time.sleep(5)
            if not done:
                abandoned.add((pid, cid))
                run_queue.log(f"{pid} piste {cid} : abandonnée après {args.retries} tentatives")
            progressed = True
        if not progressed:
            break

    if abandoned:
        run_queue.log("pistes abandonnées : " + ", ".join(f"{p}:{c}" for p, c in sorted(abandoned)))
    run_queue.log("rotation terminée")


if __name__ == "__main__":
    main()
