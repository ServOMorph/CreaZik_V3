import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_FILE = HERE / "covers_review_state.json"
MAX_REDO = 3
MAX_FAILS = 3
STATUSES = ("pending", "validated", "redo", "abandoned", "error")
LOCK_STALE_S = 30


def _read(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    if not isinstance(data.get("items"), dict):
        data["items"] = {}
    return data


def _write(path, data):
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for _ in range(40):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.1)
    os.replace(tmp, path)


@contextmanager
def state_lock(path=STATE_FILE, timeout=10.0):
    lock = Path(path).with_suffix(".lock")
    t0 = time.time()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE_S:
                    lock.unlink(missing_ok=True)
                    continue
            except OSError:
                continue
            if time.time() - t0 > timeout:
                raise TimeoutError("verrou de l'état des pochettes indisponible")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def read_state(path=STATE_FILE):
    return _read(path)


def update_item(key, changes, path=STATE_FILE):
    with state_lock(path):
        data = _read(path)
        item = data["items"].setdefault(key, {})
        item.update(changes)
        _write(path, data)
        return dict(item)


def cover_file(track):
    return (HERE / track["file"]).with_suffix(".cover.png")


def _key_order(key):
    playlist, _, ident = key.partition(":")
    try:
        return (playlist, 0, int(ident), "")
    except ValueError:
        return (playlist, 1, 0, ident)


def list_review(tracks, path=STATE_FILE):
    state = _read(path)["items"]
    items = []
    for key in sorted(tracks, key=_key_order):
        track = tracks[key]
        if track.get("jingle"):
            continue
        png = cover_file(track)
        try:
            mtime = png.stat().st_mtime_ns
        except OSError:
            continue
        saved = state.get(key, {})
        status = saved.get("status", "pending")
        if status not in STATUSES:
            status = "pending"
        rel = png.relative_to(HERE).as_posix()
        items.append({"key": key, "title": track.get("name", ""), "playlist": track.get("playlist", ""),
                      "playlist_label": track.get("playlist_label", ""), "status": status,
                      "redo_count": int(saved.get("redo_count", 0)), "max_redo": MAX_REDO,
                      "url": f"/{rel}?v={mtime}", "note": saved.get("note", "")})
    counts = {s: 0 for s in STATUSES}
    for it in items:
        counts[it["status"]] += 1
    return {"items": items, "counts": counts, "total": len(items)}


def apply_verdict(key, verdict, tracks, path=STATE_FILE):
    if key not in tracks or tracks[key].get("jingle"):
        return None
    if verdict not in ("validated", "redo"):
        return None
    with state_lock(path):
        data = _read(path)
        item = data["items"].setdefault(key, {})
        if verdict == "validated":
            item["status"] = "validated"
        elif int(item.get("redo_count", 0)) >= MAX_REDO:
            item["status"] = "abandoned"
            item["note"] = f"{MAX_REDO} regenerations deja faites, pochette conservee"
        else:
            item["status"] = "redo"
            item.pop("note", None)
        item["verdict_at"] = int(time.time())
        _write(path, data)
        return item["status"]
