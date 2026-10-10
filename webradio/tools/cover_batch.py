import argparse
import json
import os
import re
import subprocess
import sys
import time
import zlib
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOGS = HERE / "logs"
STATE = LOGS / "cover_generation_state.json"
LOCK = LOGS / "cover_generation.lock"
STOP = LOGS / "stop_covers.request"
COMFY = "http://127.0.0.1:8189"
COMFY_HOME = Path(r"D:\ServOMorph\ComfyUI-Qwen")
COMFY_LAUNCHER = COMFY_HOME / "lancer.bat"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
LEGACY_PLAYLIST_IDS = {
    "francais_tests-electro": "perso-electro",
    "francais_tests-folk": "perso-folk",
    "francais_tests-rock": "perso-rock",
    "francais_tests-classique": "perso-classique",
    "francais_tests-gregorien": "perso-gregorien",
    "francais_tests-chorale": "perso-chorale",
}


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def valid_png(path):
    try:
        with path.open("rb") as stream:
            header = stream.read(24)
        return len(header) == 24 and header[:8] == PNG_SIGNATURE and header[12:16] == b"IHDR" and header[16:24] == b"\x00\x00\x03\x00\x00\x00\x03\x00"
    except OSError:
        return False


def is_esprit_playlist(playlist):
    playlist_id = str(playlist.get("id", "")).casefold()
    label = str(playlist.get("label", "")).strip().casefold()
    return playlist_id.startswith("esprit-") or label.startswith("esprit ")


def vote_counts(votes, job):
    tracks = votes.get("tracks", {})
    keys = [job["key"]]
    legacy_id = LEGACY_PLAYLIST_IDS.get(job["playlist"])
    if legacy_id:
        keys.append(f"{legacy_id}:{job['test_case_id']}")
    up = down = 0
    for key in keys:
        vote = tracks.get(key, {})
        try:
            up += int(vote.get("up", 0))
            down += int(vote.get("down", 0))
        except (AttributeError, TypeError, ValueError):
            continue
    return up, down


def vote_score(votes, job):
    up, down = vote_counts(votes, job)
    return up - down


def music_generation_running():
    command = "$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|bash' -and $_.CommandLine -match 'run_rotation\\.py|run_queue\\.py|ace_worker\\.py|generate\\.py|run_series\\.sh' }; if ($p) { 'ACTIVE' }"
    result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
    return "ACTIVE" in result.stdout


def comfy_ready():
    try:
        with urllib.request.urlopen(COMFY + "/system_stats", timeout=3):
            return True
    except (OSError, urllib.error.URLError):
        return False


def comfy_process_running():
    command = r"$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'ComfyUI-Qwen.*main\.py --port 8189' }; if ($p) { 'ACTIVE' }"
    result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
    return "ACTIVE" in result.stdout


def ensure_comfy():
    if comfy_ready():
        return
    if os.name != "nt" or not COMFY_LAUNCHER.is_file():
        raise RuntimeError("ComfyUI-Qwen est inaccessible sur le port 8189 et lancer.bat est introuvable.")
    if not comfy_process_running():
        subprocess.Popen(["cmd.exe", "/c", "start", "", str(COMFY_LAUNCHER)], cwd=COMFY_HOME,
                         creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    for _ in range(120):
        if STOP.exists():
            raise InterruptedError("Arrêt demandé pendant le démarrage de ComfyUI.")
        if comfy_ready():
            return
        time.sleep(2)
    raise TimeoutError("ComfyUI-Qwen n'a pas répondu après son démarrage.")


def acquire_lock():
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        old_pid = read_json(LOCK, {}).get("pid")
        try:
            os.kill(int(old_pid), 0)
        except (OSError, TypeError, ValueError):
            LOCK.unlink(missing_ok=True)
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        else:
            raise RuntimeError(f"Une génération de pochettes est déjà en cours (PID {old_pid}).")
    os.write(fd, json.dumps({"pid": os.getpid()}).encode())
    return fd


def load_jobs(playlist_filter=None):
    playlists = read_json(HERE / "playlists.json", [])
    ids = {p["id"] for p in playlists if p.get("role") != "jingle" and not is_esprit_playlist(p)}
    unknown = sorted((playlist_filter or set()) - ids)
    if unknown:
        raise RuntimeError("Identifiant de playlist inconnu : " + ", ".join(unknown))
    entries = []
    for playlist in playlists:
        pid = playlist["id"]
        if playlist.get("role") == "jingle" or is_esprit_playlist(playlist) or (playlist_filter and pid not in playlist_filter):
            continue
        result_path = HERE / playlist["results"]
        data = read_json(result_path, {})
        for track in data.get("generations", []):
            if track.get("status") != "generated" or not track.get("output_file"):
                continue
            source = (HERE / track["output_file"]).resolve()
            try:
                source.relative_to(HERE.resolve())
            except ValueError:
                continue
            target = source.with_suffix(".cover.png")
            title = re.sub(r"^\d+\s*-\s*", "", track.get("name", source.stem))
            entries.append({"playlist": pid, "test_case_id": str(track.get("test_case_id", "")),
                            "key": f"{pid}:{track.get('test_case_id', '')}", "title": title,
                            "style": str(track.get("prompt", "")).strip() or pid,
                            "seed": zlib.crc32(f"{pid}:{track.get('test_case_id', '')}:{title}".encode("utf-8")), "source": source, "target": target})
    return entries


def main():
    parser = argparse.ArgumentParser(description="Génère et reprend les pochettes de morceaux avec ComfyUI-Qwen.")
    parser.add_argument("--playlist", action="append", help="Ne traiter que cet identifiant de playlist (répétable).")
    parser.add_argument("--limit", type=int, help="Limiter le nombre de nouvelles pochettes.")
    parser.add_argument("--status", action="store_true", help="Afficher l'état du dernier batch et les pochettes manquantes.")
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    jobs = load_jobs(set(args.playlist or []))
    missing = [job for job in jobs if not valid_png(job["target"])]
    if args.status:
        previous = read_json(STATE, {})
        votes = read_json(HERE / "votes.json", {})
        counts = [vote_counts(votes, job) for job in missing]
        print(json.dumps({"dernier_batch": previous, "a_generer": len(missing),
                          "pouces_positifs": sum(up > down for up, down in counts),
                          "sans_pouces": sum(up == 0 and down == 0 for up, down in counts),
                          "solde_equilibre": sum(up == down and up > 0 for up, down in counts),
                          "pouces_negatifs_exclus": sum(up < down for up, down in counts)}, ensure_ascii=False, indent=2))
        return 0
    if not missing:
        print("Toutes les pochettes demandées sont déjà présentes.")
        return 0
    fd = acquire_lock()
    STOP.unlink(missing_ok=True)
    state = {"status": "waiting_for_music_queue", "started_at": datetime.now().astimezone().isoformat(),
             "total": len(missing), "done": 0, "attempted": 0, "failed": [],
             "skipped_negative": [], "current": None}
    write_json(STATE, state)
    try:
        while music_generation_running():
            if STOP.exists():
                raise InterruptedError("Arrêt demandé.")
            print("Génération musicale active : attente avant d'utiliser ComfyUI.", flush=True)
            time.sleep(10)
        initial_votes = read_json(HERE / "votes.json", {})
        initial_scores = [vote_score(initial_votes, job) for job in missing]
        if not any(score >= 0 for score in initial_scores):
            state["skipped_negative"] = [
                {"key": job["key"], "playlist": job["playlist"], "title": job["title"]}
                for job, score in zip(missing, initial_scores) if score < 0
            ]
            state["status"] = "completed_with_skips"
            state["current"] = None
            state["finished_at"] = datetime.now().astimezone().isoformat()
            write_json(STATE, state)
            print("Aucun morceau admissible selon les pouces actuels ; ComfyUI n'a pas été démarré.")
            return 0
        ensure_comfy()
        state["status"] = "running"
        write_json(STATE, state)
        attempted = set()
        skipped_negative = {}
        while True:
            if STOP.exists():
                raise InterruptedError("Arrêt demandé.")
            pending = [job for job in missing if job["key"] not in attempted and not valid_png(job["target"])]
            votes = read_json(HERE / "votes.json", {})
            positive = []
            neutral = []
            for job in pending:
                up, down = vote_counts(votes, job)
                score = up - down
                if score > 0:
                    positive.append((score, job))
                elif score == 0:
                    neutral.append((up + down > 0, job))
                else:
                    skipped_negative[job["key"]] = {"key": job["key"], "playlist": job["playlist"],
                                                     "title": job["title"]}
            state["skipped_negative"] = list(skipped_negative.values())
            if not positive and not neutral:
                break
            if args.limit is not None and state["attempted"] >= max(0, args.limit):
                state["status"] = "paused_limit"
                break
            positive.sort(key=lambda item: item[0], reverse=True)
            neutral.sort(key=lambda item: item[0])
            job = positive[0][1] if positive else neutral[0][1]
            attempted.add(job["key"])
            state["attempted"] += 1
            state["current"] = {"playlist": job["playlist"], "title": job["title"]}
            write_json(STATE, state)
            temp = job["target"].with_name(job["target"].stem + ".tmp.png")
            temp.unlink(missing_ok=True)
            print(f"[{state['attempted']}] {job['playlist']} — {job['title']}", flush=True)
            result = subprocess.run([sys.executable, str(HERE / "tools" / "cover_gen.py"), job["title"],
                                     job["style"], str(job["seed"]), str(temp)], cwd=HERE)
            if result.returncode == 0 and valid_png(temp):
                latest_score = vote_score(read_json(HERE / "votes.json", {}), job)
                if latest_score < 0:
                    temp.unlink(missing_ok=True)
                    skipped_negative[job["key"]] = {"key": job["key"], "playlist": job["playlist"],
                                                     "title": job["title"]}
                    state["skipped_negative"] = list(skipped_negative.values())
                else:
                    os.replace(temp, job["target"])
                    state["done"] += 1
            else:
                temp.unlink(missing_ok=True)
                state["failed"].append({"playlist": job["playlist"], "title": job["title"]})
            write_json(STATE, state)
        if state["status"] != "paused_limit":
            state["status"] = "completed_with_errors" if state["failed"] else (
                "completed_with_skips" if state["skipped_negative"] else "completed")
        state["current"] = None
        state["finished_at"] = datetime.now().astimezone().isoformat()
        write_json(STATE, state)
        print(f"Batch terminé : {state['done']} créées, {len(state['skipped_negative'])} exclues (solde négatif), "
              f"{len(state['failed'])} échec(s). État : {state['status']}.")
        return 0 if not state["failed"] else 1
    except InterruptedError as exc:
        state["status"] = "interrupted"
        state["current"] = None
        state["interrupted_at"] = datetime.now().astimezone().isoformat()
        write_json(STATE, state)
        print(str(exc))
        return 130
    finally:
        os.close(fd)
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
