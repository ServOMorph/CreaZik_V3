import json
import os
import re
import secrets
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).parent.resolve()
ANNONCE = HERE / "tools" / "annonce.py"
TEXT_MAX = 300
QUEUE_MAX = 5
KEEP_DONE = 20
ENGINES = {
    "kokoro": {"label": "Rapide (Kokoro)", "env": "CREAZIK_KOKORO_PYTHON",
               "python": r"D:\ServOMorph\TTS_Local\kokoro\.venv\Scripts\python.exe", "timeout": 600},
    "chatterbox": {"label": "Voix CréaZik (Chatterbox)", "env": "CREAZIK_CHATTERBOX_PYTHON",
                   "python": r"D:\ServOMorph\TTS_Local\chatterbox\.venv\Scripts\python.exe", "timeout": 2400},
}
CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
PHONETIC = [
    (re.compile(r"S[ée]r[ée]n\s?IA\s+Tech\b", re.I), "Sérénia Tèk"),
    (re.compile(r"S[ée]r[ée]nIA\b"), "Sérénia"),
    (re.compile(r"Cr[ée]a\s?Zi[kc]\b", re.I), "Créa Zique"),
    (re.compile(r"\bWeb\s?Radio\b", re.I), "Ouèbe Radio"),
    (re.compile(r"\bIA\b"), "I A"),
]


def phonetic(text):
    for rx, repl in PHONETIC:
        text = rx.sub(repl, text)
    return text


def clean_text(value):
    if not isinstance(value, str):
        return None
    text = " ".join(CTRL_RE.sub(" ", value).split())
    if not text or len(text) > TEXT_MAX:
        return None
    return text


def dry_run_forced():
    return os.environ.get("CREAZIK_JINGLE_DRY_RUN", "") not in ("", "0")


def python_for(engine):
    spec = ENGINES[engine]
    return os.environ.get(spec["env"]) or spec["python"]


class JingleQueue:
    def __init__(self, runner=None):
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.jobs = {}
        self.order = []
        self.runner = runner or self._run_subprocess

    def submit(self, text, engine, dry_run=False):
        with self.lock:
            waiting = sum(1 for j in self.jobs.values() if j["status"] in ("queued", "running"))
            if waiting >= QUEUE_MAX:
                return None
            jid = secrets.token_hex(16)
            self.jobs[jid] = {"id": jid, "status": "queued", "text": text, "spoken": phonetic(text), "engine": engine,
                              "engine_label": ENGINES[engine]["label"], "dry_run": bool(dry_run or dry_run_forced()),
                              "created": time.time(), "started": None, "finished": None, "elapsed_s": None,
                              "duration_s": None, "key": None, "broadcast": False, "error": None}
            self.order.append(jid)
            done = [j for j in self.order if self.jobs[j]["status"] in ("ready", "error")]
            for old in done[:-KEEP_DONE]:
                self.order.remove(old)
                self.jobs.pop(old, None)
        self.wake.set()
        return jid

    def status(self, jid):
        with self.lock:
            job = self.jobs.get(jid)
            if job is None:
                return None
            out = dict(job)
            if out["status"] == "queued":
                out["ahead"] = sum(1 for j in self.order if self.jobs[j]["status"] in ("queued", "running")
                                   and self.jobs[j]["created"] < job["created"])
            return out

    def _next(self):
        with self.lock:
            for jid in self.order:
                if self.jobs[jid]["status"] == "queued":
                    self.jobs[jid]["status"] = "running"
                    self.jobs[jid]["started"] = time.time()
                    return jid, dict(self.jobs[jid])
        return None, None

    def process_one(self):
        jid, job = self._next()
        if jid is None:
            return False
        try:
            if job["dry_run"]:
                result = {"key": None, "duration_s": None, "broadcast": False}
            else:
                result = self.runner(job)
            update = {"status": "ready", "key": result.get("key"), "duration_s": result.get("duration_s"),
                      "broadcast": bool(result.get("broadcast"))}
        except Exception as e:
            update = {"status": "error", "error": str(e)[:300] or "échec de la synthèse"}
        with self.lock:
            j = self.jobs.get(jid)
            if j is not None:
                j.update(update)
                j["finished"] = time.time()
                j["elapsed_s"] = round(j["finished"] - j["started"], 1)
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] jingle texte {jid[:8]} : {update['status']}"
                         f"{' (essai)' if job['dry_run'] else ''}\n")
        return True

    def _run_subprocess(self, job):
        py = python_for(job["engine"])
        if not Path(py).is_file():
            raise RuntimeError(f"interpréteur introuvable pour {job['engine']}")
        env = dict(os.environ, CUDA_VISIBLE_DEVICES="", PYTHONIOENCODING="utf-8")
        cmd = [py, str(ANNONCE), job["spoken"], "--affiche", job["text"], "--moteur", job["engine"], "--json"]
        proc = subprocess.run(cmd, cwd=str(HERE), env=env, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=ENGINES[job["engine"]]["timeout"])
        line = next((l for l in reversed(proc.stdout.splitlines()) if l.startswith("{")), "")
        if proc.returncode != 0 or not line:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:] or ["sortie vide"]
            raise RuntimeError(f"synthèse en échec (code {proc.returncode}) : {tail[0][:200]}")
        data = json.loads(line)
        return {"key": data.get("key"), "duration_s": data.get("duration_s"), "broadcast": bool(data.get("broadcast"))}

    def run(self):
        while True:
            if not self.process_one():
                self.wake.wait(5)
                self.wake.clear()
