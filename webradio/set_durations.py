import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
CENTER = 90
SPREAD = 45
STEP = 5


def duration_for(playlist_id, case_id):
    h = int(hashlib.sha256(f"{playlist_id}:{case_id}".encode()).hexdigest(), 16)
    steps = (2 * SPREAD) // STEP + 1
    return CENTER - SPREAD + STEP * (h % steps)


def generated_ids(results_path):
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {g["test_case_id"] for g in data.get("generations", []) if g.get("status") == "generated"}


def main():
    changed = 0
    for cfg_path in sorted(HERE.glob("playlists/*/config.json")):
        pid = cfg_path.parent.name
        if pid == "jingles":
            continue
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        done = generated_ids(cfg_path.parent / "outputs" / "playlist_results.json")
        touched = False
        for case in cfg["test_cases"]:
            if case["id"] in done or case.get("duration_fixed"):
                continue
            new = duration_for(pid, case["id"])
            if case.get("duration") != new:
                case["duration"] = new
                touched = True
        if touched:
            tmp = cfg_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, cfg_path)
            changed += 1
    print(changed, "configuration(s) mise(s) à jour")


if __name__ == "__main__":
    main()
