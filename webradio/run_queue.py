import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def kill_tree(proc):
    subprocess.call(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def results_status(results_path):
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            return {g["test_case_id"]: g["status"] for g in json.load(f).get("generations", [])}
    except Exception:
        return {}


def run_one(config, case_id, timeout, log_dir):
    log_file = log_dir / f"queue_track_{case_id}.log"
    with open(log_file, "w", encoding="utf-8", errors="replace") as lf:
        proc = subprocess.Popen(
            [sys.executable, str(HERE / "generate.py"), str(config), "--only", case_id],
            stdout=lf, stderr=subprocess.STDOUT)
        t0 = time.time()
        while proc.poll() is None:
            if time.time() - t0 > timeout:
                log(f"piste {case_id} : timeout {timeout}s, arrêt du processus")
                kill_tree(proc)
                proc.wait()
                return "timeout"
            time.sleep(2)
    return "exit" if proc.returncode == 0 else f"code {proc.returncode}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--timeout", type=int, default=0,
                    help="secondes par piste ; 0 = automatique (3 x durée de la piste, minimum 90 s)")
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    config = Path(args.config).resolve()
    with open(config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out_dir = (HERE / cfg["output_dir"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "playlist_results.json"

    ids = [c["id"] for c in cfg["test_cases"]]
    durations = {c["id"]: c.get("duration", 30) for c in cfg["test_cases"]}
    failed_final = []
    for cid in ids:
        if results_status(results_path).get(cid) == "generated":
            log(f"piste {cid} : déjà générée, ignorée")
            continue
        for attempt in range(1, args.retries + 1):
            limit = args.timeout or max(90, int(3 * durations[cid]))
            log(f"piste {cid} : tentative {attempt}/{args.retries} (limite {limit} s)")
            how = run_one(config, cid, limit, out_dir)
            status = results_status(results_path).get(cid)
            log(f"piste {cid} : fin ({how}), statut {status}")
            if status == "generated":
                break
            time.sleep(5)
        else:
            failed_final.append(cid)

    if failed_final:
        log(f"échecs définitifs : {', '.join(failed_final)}")
        sys.exit(1)
    log("file terminée, toutes les pistes générées")


if __name__ == "__main__":
    main()
