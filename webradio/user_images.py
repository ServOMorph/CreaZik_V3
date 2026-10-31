import json
import os
import re
import secrets
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE / "tools"))
import cover_batch
import cover_gen
import gpu

DIR = HERE / "user_images"
ID_RE = re.compile(r"^[0-9a-f]{32}$")
CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
PROMPT_MAX = 300
SIZE = 768
TIMEOUT_S = 600
MUSIC_POLL_S = 10
RETENTION_S = 7 * 24 * 60 * 60
PURGE_INTERVAL_S = 60 * 60
NEGATIVE = "flou, deformation, visages deformes, mains deformees, basse qualite, filigrane, logo"
ERRORS = {
    "comfy": "Le générateur d'images est indisponible pour le moment. Réessayez plus tard.",
    "timeout": "La création de l'image a pris trop de temps. Réessayez.",
    "failed": "La création de l'image a échoué. Réessayez avec une autre description.",
}


def clean_prompt(value):
    if not isinstance(value, str):
        return None
    text = " ".join(CTRL_RE.sub(" ", value).split())
    if not text or len(text) > PROMPT_MAX:
        return None
    return text


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


class ImageQueue:
    def __init__(self, folder=DIR, generate=None, music_busy=None, ensure_comfy=None, free_comfy=None, gpu_lock=None):
        self.dir = Path(folder)
        self.gpu = gpu_lock or gpu.LOCK
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.jobs = {}
        self.order = []
        self.last_purge = None
        self.generate = generate or self._generate
        self.music_busy = music_busy or gpu.rotation_running
        self.ensure_comfy = ensure_comfy or (lambda: cover_batch.ensure_comfy(stop_file=None))
        self.free_comfy = free_comfy or gpu.free_comfy
        self.dir.mkdir(parents=True, exist_ok=True)
        self._load()

    def _path(self, job_id, ext):
        return self.dir / f"{job_id}.{ext}"

    def _save(self, job):
        tmp = self._path(job["id"], "json.tmp")
        tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self._path(job["id"], "json"))

    def _load(self):
        pending = []
        for f in self.dir.glob("*.json"):
            if not ID_RE.match(f.stem):
                continue
            try:
                job = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if job.get("status") in ("queued", "running"):
                job["status"] = "queued"
                job.pop("waiting_music", None)
                pending.append(job)
            self.jobs[f.stem] = job
        self.order = [j["id"] for j in sorted(pending, key=lambda j: j.get("created_at", ""))]

    def submit(self, prompt):
        job_id = secrets.token_hex(16)
        job = {"id": job_id, "prompt": prompt, "status": "queued", "created_at": now_iso()}
        with self.lock:
            self._save(job)
            self.jobs[job_id] = job
            self.order.append(job_id)
        self.wake.set()
        return job_id

    def status(self, job_id):
        if not ID_RE.match(job_id or ""):
            return None
        with self.lock:
            job = self.jobs.get(job_id)
            if job is None:
                return None
            out = {"id": job_id, "status": job["status"]}
            if job["status"] == "queued":
                out["position"] = self.order.index(job_id) + 1 if job_id in self.order else 1
                out["ahead"] = out["position"] - 1 + sum(1 for j in self.jobs.values() if j["status"] == "running")
                out["waiting_music"] = bool(job.get("waiting_music"))
            elif job["status"] == "running":
                out["started_at"] = job.get("started_at")
            elif job["status"] == "ready":
                out["image"] = f"/user_images/{job_id}.png"
            elif job["status"] == "error":
                out["error"] = job.get("error") or ERRORS["failed"]
            return out

    def _generate(self, prompt, out, seed):
        cover_gen.generate(prompt, str(out), seed=seed, size=SIZE, negative=NEGATIVE, prefix="creazik_user_image", timeout=TIMEOUT_S)

    def _next(self):
        with self.lock:
            return self.jobs.get(self.order[0]) if self.order else None

    def _set(self, job, **fields):
        with self.lock:
            job.update(fields)
            self._save(job)

    def _set_safe(self, job, **fields):
        with self.lock:
            job.update(fields)
            try:
                self._save(job)
            except OSError as e:
                sys.stderr.write(f"[{datetime.now():%H:%M:%S}] image {job['id'][:8]} : sauvegarde impossible : {e}\n")

    def _purge(self):
        now = time.monotonic()
        if self.last_purge is not None and now - self.last_purge < PURGE_INTERVAL_S:
            return
        self.last_purge = now
        cutoff = time.time() - RETENTION_S
        with self.lock:
            ids = {p.stem for p in self.dir.iterdir() if p.suffix in (".png", ".json") and ID_RE.fullmatch(p.stem)}
            for job_id in ids:
                job = self.jobs.get(job_id)
                if job and job.get("status") in ("queued", "running"):
                    continue
                paths = [self._path(job_id, ext) for ext in ("png", "json")]
                try:
                    existing = [p for p in paths if p.exists()]
                    if any(p.stat().st_mtime >= cutoff for p in existing):
                        continue
                    for p in existing:
                        p.unlink()
                    self.jobs.pop(job_id, None)
                except OSError as e:
                    sys.stderr.write(f"[{datetime.now():%H:%M:%S}] image {job_id[:8]} : purge impossible : {e}\n")

    def run_once(self):
        self._purge()
        job = self._next()
        if job is None:
            return False
        with self.gpu:
            busy = self.music_busy()
            if not busy:
                self._process(job)
                if self._next() is None:
                    self.free_comfy()
        if busy:
            if not job.get("waiting_music"):
                self._set_safe(job, waiting_music=True)
            self.wake.wait(MUSIC_POLL_S)
            self.wake.clear()
        return True

    def _process(self, job):
        seed = secrets.randbelow(2 ** 32)
        with self.lock:
            if job["id"] in self.order:
                self.order.remove(job["id"])
            job.pop("waiting_music", None)
            job.update(status="running", started_at=now_iso(), seed=seed)
        t0 = time.time()
        png = self._path(job["id"], "png")
        tmp = self._path(job["id"], "tmp.png")
        try:
            with self.lock:
                self._save(job)
            try:
                self.ensure_comfy()
            except Exception as e:
                raise ConnectionError(str(e)) from e
            self.generate(job["prompt"], tmp, seed)
            data = tmp.read_bytes()
            if data[:8] != cover_batch.PNG_SIGNATURE:
                raise RuntimeError("fichier produit invalide")
            os.replace(tmp, png)
            self._set(job, status="ready", finished_at=now_iso(), duration_s=round(time.time() - t0, 1),
                      model=cover_gen.MODEL, size=f"{SIZE}x{SIZE}", steps=20, negative=NEGATIVE)
        except Exception as e:
            kind = "timeout" if isinstance(e, TimeoutError) else ("comfy" if isinstance(e, (ConnectionError, OSError)) else "failed")
            self._set_safe(job, status="error", error=ERRORS[kind], detail=f"{type(e).__name__}: {e}"[:300],
                           finished_at=now_iso(), duration_s=round(time.time() - t0, 1), model=cover_gen.MODEL)
            sys.stderr.write(f"[{datetime.now():%H:%M:%S}] image {job['id'][:8]} : échec {type(e).__name__}: {str(e)[:120]}\n")
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    def run(self):
        while True:
            try:
                if gpu.paused():
                    self.wake.wait(30)
                    self.wake.clear()
                    continue
                if not self.run_once():
                    self.wake.wait(30)
                    self.wake.clear()
            except Exception as e:
                sys.stderr.write(f"[{datetime.now():%H:%M:%S}] file d'images : {type(e).__name__}: {e}\n")
                time.sleep(5)
