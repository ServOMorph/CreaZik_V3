import json
import os
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import user_images  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def make(tmp_path, gen=None, busy=None, comfy=None):
    return user_images.ImageQueue(tmp_path, generate=gen or (lambda p, out, s: Path(out).write_bytes(PNG)),
                                  music_busy=busy or (lambda: False), ensure_comfy=comfy or (lambda: None),
                                  free_comfy=lambda: None)


def test_clean_prompt():
    assert user_images.clean_prompt("  un  chat\x00 bleu ") == "un chat bleu"
    assert user_images.clean_prompt("") is None
    assert user_images.clean_prompt("x" * 301) is None
    assert user_images.clean_prompt("x" * 300) == "x" * 300
    assert user_images.clean_prompt(42) is None


def test_queue_positions_and_ready(tmp_path):
    q = make(tmp_path)
    a = q.submit("a")
    b = q.submit("b")
    assert q.status(a)["position"] == 1 and q.status(b)["position"] == 2
    assert q.run_once()
    st = q.status(a)
    assert st["status"] == "ready" and st["image"] == f"/user_images/{a}.png"
    assert (tmp_path / f"{a}.png").read_bytes() == PNG
    trace = json.loads((tmp_path / f"{a}.json").read_text(encoding="utf-8"))
    assert trace["prompt"] == "a" and isinstance(trace["seed"], int) and trace["model"] and "duration_s" in trace
    assert q.status(b)["position"] == 1


def test_unknown_or_invalid_id(tmp_path):
    q = make(tmp_path)
    assert q.status("0" * 32) is None
    assert q.status("../x") is None


def test_error_then_queue_continues(tmp_path):
    calls = []

    def gen(prompt, out, seed):
        calls.append(prompt)
        if prompt == "bad":
            raise TimeoutError("trop long")
        Path(out).write_bytes(PNG)

    q = make(tmp_path, gen=gen)
    a = q.submit("bad")
    b = q.submit("good")
    q.run_once()
    q.run_once()
    assert q.status(a)["status"] == "error" and "trop de temps" in q.status(a)["error"]
    assert q.status(b)["status"] == "ready"
    assert not (tmp_path / f"{a}.png").exists()


def test_comfy_unavailable(tmp_path):
    def comfy():
        raise RuntimeError("port 8189 fermé")

    q = make(tmp_path, comfy=comfy)
    a = q.submit("x")
    q.run_once()
    assert q.status(a)["status"] == "error" and "indisponible" in q.status(a)["error"]


def test_waits_for_music(tmp_path, monkeypatch):
    monkeypatch.setattr(user_images, "MUSIC_POLL_S", 0)
    q = make(tmp_path, busy=lambda: True)
    a = q.submit("x")
    q.run_once()
    st = q.status(a)
    assert st["status"] == "queued" and st["waiting_music"]


def test_reload_requeues_running(tmp_path):
    q = make(tmp_path)
    a = q.submit("x")
    job = q.jobs[a]
    job["status"] = "running"
    q._save(job)
    q2 = make(tmp_path)
    assert q2.status(a)["status"] == "queued"
    q2.run_once()
    assert q2.status(a)["status"] == "ready"


def test_gpu_lock_covers_check_and_generation(tmp_path):
    lock = threading.Lock()
    seen = []

    def busy():
        seen.append(("busy", lock.locked()))
        return False

    def gen(prompt, out, seed):
        seen.append(("gen", lock.locked()))
        Path(out).write_bytes(PNG)

    def free():
        seen.append(("free", lock.locked()))

    q = user_images.ImageQueue(tmp_path, generate=gen, music_busy=busy, ensure_comfy=lambda: None, free_comfy=free, gpu_lock=lock)
    q.submit("x")
    q.run_once()
    assert seen == [("busy", True), ("gen", True), ("free", True)]
    assert not lock.locked()


def test_save_failure_ends_in_error(tmp_path, monkeypatch):
    q = make(tmp_path)
    a = q.submit("x")
    real = q._save

    def save(job):
        if job.get("status") == "running":
            raise OSError("disque plein")
        real(job)

    monkeypatch.setattr(q, "_save", save)
    q.run_once()
    st = q.status(a)
    assert st["status"] == "error" and a not in q.order
    assert json.loads((tmp_path / f"{a}.json").read_text(encoding="utf-8"))["status"] == "error"


def test_purge_expired_images_preserves_active_and_recent(tmp_path, monkeypatch):
    q = make(tmp_path)
    now = 2_000_000_000
    clock = [0]
    monkeypatch.setattr(user_images.time, "time", lambda: now)
    monkeypatch.setattr(user_images.time, "monotonic", lambda: clock[0])
    ids = {}
    for name, status, age in (("old", "ready", 8), ("error", "error", 8), ("recent", "ready", 6),
                              ("queued", "queued", 8), ("running", "running", 8), ("mixed", "ready", 8)):
        job_id = q.submit(name)
        ids[name] = job_id
        q.jobs[job_id]["status"] = status
        q._save(q.jobs[job_id])
        if status != "queued":
            q.order.remove(job_id)
        for ext in ("png", "json"):
            path = q._path(job_id, ext)
            if ext == "png":
                path.write_bytes(PNG)
            stamp = now - age * 86400
            os.utime(path, (stamp, stamp))
    mixed = q._path(ids["mixed"], "png")
    os.utime(mixed, (now, now))
    orphan = tmp_path / ("f" * 32 + ".png")
    orphan.write_bytes(PNG)
    os.utime(orphan, (now - 8 * 86400, now - 8 * 86400))
    unrelated = tmp_path / "reference.png"
    unrelated.write_bytes(PNG)
    os.utime(unrelated, (now - 8 * 86400, now - 8 * 86400))
    monkeypatch.setattr(q, "_next", lambda: None)
    assert not q.run_once()
    for name in ("old", "error"):
        assert q.status(ids[name]) is None
        assert not any(q._path(ids[name], ext).exists() for ext in ("png", "json"))
    assert not orphan.exists() and unrelated.exists()
    for name in ("recent", "queued", "running", "mixed"):
        assert all(q._path(ids[name], ext).exists() for ext in ("png", "json"))
        assert q.status(ids[name])["status"] == q.jobs[ids[name]]["status"]
    assert q.order == [ids["queued"]]
    for ext in ("png", "json"):
        os.utime(q._path(ids["recent"], ext), (now - 8 * 86400, now - 8 * 86400))
    clock[0] = user_images.PURGE_INTERVAL_S - 1
    q.run_once()
    assert q.status(ids["recent"]) is not None
    clock[0] += 1
    q.run_once()
    assert q.status(ids["recent"]) is None
