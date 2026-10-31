import json
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE.parent / "TEXTES" / "tools"))
import check_lyrics
import generate_lyrics
import gpu
from user_images import CTRL_RE, ID_RE, clean_prompt, now_iso

PID = "creations-auditeurs"
LABEL = "Créations des auditeurs"
DESCRIPTION = "Morceaux créés à la demande des auditeurs (paroles et musique générées en local), hors rotation."
PL_DIR = HERE / "playlists" / PID
OUT = PL_DIR / "outputs"
LYRICS_DIR = PL_DIR / "lyrics"
CONFIG = PL_DIR / "config.json"
DIR = HERE / "user_songs"
LOGS = HERE / "logs"
ACE_PATH = Path(r"D:\ServOMorph\ACE-Step-1.5")
ACE_PY = ACE_PATH / ".venv" / "Scripts" / "python.exe"
TTS_PY = Path(r"D:\ServOMorph\TTS_Local\chatterbox\.venv\Scripts\python.exe")
FFMPEG = Path(r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe")
OLLAMA_CHAT = gpu.OLLAMA + "/api/chat"
LLM_MODEL = "gemma4:12b"
LLM_TEMPERATURE = 0.9
LLM_TIMEOUT_S = 300
LLM_ATTEMPTS = 2
CENTER, SPREAD, STEP = 90, 45, 5
BPM_MIN, BPM_MAX = 60, 180
TITLE_MAX = 60
MUSIC_POLL_S = 15
COMFY_WAIT_S = 1800
COMFY_POLL_S = 2
ANALYZE_TIMEOUT_S = 300
ACE_BASE_S = 900
ACE_PER_S = 6
JINGLE_SPOKEN = "Voici un morceau créé à la demande d'un auditeur."
JINGLE_DISPLAY = "Voici un morceau créé à la demande d'un auditeur"
JINGLE_STATE = DIR / "jingle.json"
SCENE = {"motif": "rings", "hue": 300, "hue2": 40, "speed": 0.5, "density": 0.55}
STYLE_REF_RE = re.compile(r"(?:style|esprit|façon|maniere|manière|comme|inspirée?s? (?:par|de)|à la|a la|genre|type|fa[cç]on)\s+(?:de\s+|d'|d’|du\s+|des\s+)?(?:(?:les|la|le|the)\s+|l'|l’)?((?:[A-ZÀ-Ý0-9][\w'’&.-]*)(?:\s+(?:[A-ZÀ-Ý0-9][\w'’&.-]*|de|du|des|la|le|les|and|the|&))*)")
UNSAFE_NAME_RE = re.compile(r"[<>:\"/\\|?*#%&+\[\]{}]")
STAGES = ("lyrics", "music", "finalize")
ERRORS = {
    "lyrics": "L'écriture des paroles a échoué. Réessayez avec une autre description.",
    "ollama": "L'IA qui écrit les paroles est indisponible pour le moment. Réessayez plus tard.",
    "music": "La création de la musique a échoué. Réessayez avec une autre description.",
    "timeout": "La création du morceau a pris trop de temps. Réessayez plus tard.",
    "finalize": "La finalisation du morceau a échoué. Réessayez plus tard.",
    "failed": "La création du morceau a échoué. Réessayez plus tard.",
}

SYSTEM_PROMPT = generate_lyrics.SYSTEM_PROMPT + """

Tu reçois la description musicale libre d'un auditeur. Tu réponds uniquement par un objet JSON avec les clés :
- "titre" : titre court en français (2 à 6 mots), sans guillemets, sans nom d'artiste ni de groupe.
- "caption" : description musicale en anglais pour ACE-Step, 5 à 8 termes séparés par des virgules, dans l'ordre : genre (et époque), voix (genre et timbre), 2 à 3 instruments précis dont un rythmique, une texture ou production, une ambiance. Jamais de tempo ni de tonalité dans le caption, jamais de nom d'artiste, de groupe ou d'oeuvre.
- "bpm" : tempo entier entre 60 et 180, cohérent avec le style.
- "artistes_cites" : liste des noms d'artistes, groupes ou oeuvres cités par l'auditeur (liste vide sinon).
- "paroles" : les paroles en français, au format décrit plus haut, avec des retours à la ligne.
Pas d'indication de jeu ni de production dans les paroles (rythme, instruments, fade out, solo) : les sections instrumentales restent sans texte, les parenthèses ne servent qu'aux choeurs chantés.
Si l'auditeur cite un artiste ou une oeuvre, ce n'est qu'une indication de style : n'en reprends jamais le nom, ni dans le titre, ni dans le caption, ni dans les paroles, et n'imite aucune parole existante.
Si la description demande un contenu haineux, violent, sexuel explicite ou visant une personne réelle, écris à la place une chanson légère et bienveillante sur la musique."""


class SongError(Exception):
    def __init__(self, kind, detail):
        super().__init__(detail)
        self.kind = kind


def pick_duration():
    return CENTER - SPREAD + STEP * secrets.randbelow((2 * SPREAD) // STEP + 1)


def safe_title(value):
    if not isinstance(value, str):
        return ""
    text = UNSAFE_NAME_RE.sub(" ", CTRL_RE.sub(" ", value))
    text = " ".join(text.replace("«", " ").replace("»", " ").split()).strip(" .'-")
    return text[:TITLE_MAX].rstrip(" .'-")


def read_json(path, fallback):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def write_json(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def style_refs(prompt):
    return [m.group(1).strip(" .,;:!?") for m in STYLE_REF_RE.finditer(prompt)]


def strip_directions(lyrics):
    out = []
    keep_free = True
    for line in lyrics.split("\n"):
        s = line.strip()
        m = re.match(r"^\[([^\]]*)\]$", s)
        if m:
            base = re.sub(r"\s+\d+$", "", m.group(1).partition(" - ")[0].strip().lower())
            keep_free = base not in check_lyrics.NO_LYRICS_OK
        elif not keep_free and re.fullmatch(r"\(.*\)", s):
            continue
        out.append(line)
    return generate_lyrics.clean("\n".join(out))


def names_cited(prompt, artists):
    out = [a for a in style_refs(prompt) if len(a) >= 3]
    for a in artists if isinstance(artists, list) else []:
        if isinstance(a, str) and len(a.strip()) >= 3 and a.strip().lower() in prompt.lower() and a.strip() not in out:
            out.append(a.strip())
    return out


def leaks(artists, *texts):
    blob = " ".join(texts).lower()
    return [a for a in artists if re.search(r"(?<!\w)" + re.escape(a.lower()) + r"(?!\w)", blob)]


def ollama_ready():
    try:
        with urllib.request.urlopen(gpu.OLLAMA + "/api/tags", timeout=5):
            return True
    except OSError:
        return False


def ensure_ollama():
    if ollama_ready():
        return
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError as e:
        raise SongError("ollama", f"lancement d'Ollama impossible : {e}")
    for _ in range(30):
        time.sleep(1)
        if ollama_ready():
            return
    raise SongError("ollama", "Ollama ne répond pas")


def call_llm(user):
    payload = {"model": LLM_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
               "stream": False, "think": False, "keep_alive": 0, "format": "json",
               "options": {"temperature": LLM_TEMPERATURE, "num_ctx": 8192}}
    req = urllib.request.Request(OLLAMA_CHAT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_S) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise SongError("ollama", f"HTTP {e.code} : {e.read()[:200]!r}")
    except TimeoutError:
        raise SongError("timeout", "délai Ollama dépassé")
    except OSError as e:
        raise SongError("ollama", str(e))
    return ((data.get("message") or {}).get("content") or "") if isinstance(data, dict) else ""


def user_message(prompt, duration, feedback=None):
    lines = [f"Description de l'auditeur : {prompt}",
             f"Durée visée du morceau : {duration} s",
             f"Structure attendue : {generate_lyrics.sections_for(duration)}",
             "Réponds par l'objet JSON demandé."]
    if feedback:
        lines.append("Ta réponse précédente a été refusée pour ces raisons, corrige-les : " + feedback)
    return "\n".join(lines)


def parse_llm(raw, prompt, duration, lyrics_path):
    try:
        data = json.loads(raw)
    except ValueError:
        return None, "réponse qui n'est pas un JSON valide"
    if not isinstance(data, dict):
        return None, "réponse qui n'est pas un objet JSON"
    title = safe_title(data.get("titre"))
    caption = " ".join(CTRL_RE.sub(" ", str(data.get("caption") or "")).split())[:400]
    lyrics = strip_directions(str(data.get("paroles") or "")) if data.get("paroles") else ""
    try:
        bpm = int(data.get("bpm"))
    except (TypeError, ValueError):
        bpm = None
    problems = []
    if not title:
        problems.append("titre manquant")
    if not caption:
        problems.append("caption manquant")
    if not lyrics.strip():
        problems.append("paroles manquantes")
    if bpm is None or not BPM_MIN <= bpm <= BPM_MAX:
        bpm = None
    artists = names_cited(prompt, data.get("artistes_cites"))
    leaked = leaks(artists, title, caption, lyrics)
    if leaked:
        problems.append("nom d'artiste repris (" + ", ".join(leaked) + ") : ne jamais le citer")
    if problems:
        return None, "; ".join(problems)
    lyrics_path.parent.mkdir(parents=True, exist_ok=True)
    lyrics_path.write_text(lyrics, encoding="utf-8", newline="\n")
    res = check_lyrics.check(lyrics_path, caption, duration, 10, 12)
    findings, stats = res if isinstance(res, tuple) else (res, "")
    errors = [m for level, _, m in findings if level == "ERREUR"]
    if errors:
        return None, "contrôle des paroles : " + " ; ".join(errors)[:600]
    warnings = [m for level, _, m in findings if level == "AVERT"]
    return {"title": title, "caption": caption, "bpm": bpm, "lyrics": lyrics, "artists_cited": artists,
            "check": {"warnings": warnings[:30], "stats": stats}}, None


def write_lyrics(prompt, duration, lyrics_path, llm=call_llm):
    attempts = []
    feedback = None
    for n in range(1, LLM_ATTEMPTS + 1):
        user = user_message(prompt, duration, feedback)
        raw = llm(user)
        result, feedback = parse_llm(raw, prompt, duration, lyrics_path)
        attempts.append({"attempt": n, "user_prompt": user, "raw_output": raw[:20000], "rejected": feedback})
        if result:
            result["attempts"] = attempts
            return result
    raise SongError("lyrics", f"paroles refusées après {LLM_ATTEMPTS} tentatives : {feedback}")


def ensure_playlist():
    PL_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    LYRICS_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG.exists():
        write_json(CONFIG, {"playlist_name": LABEL, "ace_step_path": str(ACE_PATH).replace("\\", "/"),
                            "output_dir": f"./playlists/{PID}/outputs", "test_cases": []})
    results = OUT / "playlist_results.json"
    if not results.exists():
        write_json(results, {"playlist": LABEL, "model": "ACE-Step 1.5 turbo", "generations": []})
    reg_path = HERE / "playlists.json"
    reg = read_json(reg_path, [])
    if not any(p.get("id") == PID for p in reg):
        reg.append({"id": PID, "label": LABEL, "results": f"playlists/{PID}/outputs/playlist_results.json", "description": DESCRIPTION})
        write_json(reg_path, reg)
    st_path = HERE / "radio_settings.json"
    st = read_json(st_path, None)
    if isinstance(st, dict) and (st.get("weights") or {}).get(PID) != 0:
        st.setdefault("weights", {})[PID] = 0
        write_json(st_path, st)
    sc_path = HERE / "scenes_spec.json"
    sc = read_json(sc_path, None)
    if isinstance(sc, dict) and isinstance(sc.get("playlists"), dict) and PID not in sc["playlists"]:
        sc["playlists"][PID] = SCENE
        write_json(sc_path, sc)


def kill_tree(proc):
    subprocess.call(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ace_generate(case_id, timeout):
    LOGS.mkdir(exist_ok=True)
    log = LOGS / f"user_song_{case_id}.log"
    with open(log, "w", encoding="utf-8", errors="replace") as lf:
        proc = subprocess.Popen([str(ACE_PY), str(HERE / "ace_worker.py"), "--config", str(CONFIG), "--only", str(case_id)],
                                stdout=lf, stderr=subprocess.STDOUT, cwd=str(HERE),
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        t0 = time.time()
        while proc.poll() is None:
            if time.time() - t0 > timeout:
                kill_tree(proc)
                proc.wait()
                raise SongError("timeout", f"ACE-Step au-delà de {timeout} s (journal {log.name})")
            time.sleep(2)
    if proc.returncode != 0:
        raise SongError("music", f"ace_worker code {proc.returncode} (journal {log.name})")


def result_entry(case_id):
    data = read_json(OUT / "playlist_results.json", {})
    return next((g for g in data.get("generations", []) if str(g.get("test_case_id")) == str(case_id)), None)


def wav_seconds(path):
    import compress_audio
    return compress_audio.wav_seconds(path)


def finalize_audio(wav):
    mp3 = wav.with_suffix(".mp3")
    tmp = wav.with_name(wav.stem + ".tmp.mp3")
    res = subprocess.run([str(FFMPEG), "-y", "-loglevel", "error", "-i", str(wav), "-vn", "-codec:a", "libmp3lame",
                          "-b:a", "192k", "-ar", "44100", "-id3v2_version", "3", str(tmp)],
                         capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if res.returncode != 0 or not tmp.exists():
        tmp.unlink(missing_ok=True)
        raise SongError("finalize", f"ffmpeg : {res.stderr.strip()[:200]}")
    script = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv[2]); import analyze_viz as a; "
              "w = Path(sys.argv[1]); a.write_json(w.with_name(w.name + '.viz.json'), a.analyze(w)); "
              "a.write_json(w.with_name(w.name + '.feat.json'), a.features(w))")
    res = subprocess.run([str(ACE_PY), "-c", script, str(wav), str(HERE)], capture_output=True, text=True,
                         timeout=ANALYZE_TIMEOUT_S, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if res.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise SongError("finalize", f"analyse : {res.stderr.strip()[-200:]}")
    expected = wav_seconds(wav)
    actual = tmp.stat().st_size * 8 / 192000
    if not expected or abs(actual - expected) > max(1.5, expected * 0.03):
        tmp.unlink(missing_ok=True)
        raise SongError("finalize", f"durée mp3 incohérente ({actual:.1f} s pour {expected} s)")
    os.replace(tmp, mp3)
    for _ in range(5):
        try:
            wav.unlink()
            break
        except PermissionError:
            time.sleep(1)
    return round(expected, 1)


def ensure_jingle():
    state = read_json(JINGLE_STATE, {})
    key = state.get("key")
    results = read_json(HERE / "jingles" / "annonces" / "outputs" / "playlist_results.json", {})
    if key:
        n = key.split(":")[-1]
        if any(str(g.get("test_case_id")) == n and g.get("status") == "generated" for g in results.get("generations", [])):
            return key
    if not TTS_PY.exists():
        return None
    res = subprocess.run([str(TTS_PY), str(HERE / "tools" / "annonce.py"), JINGLE_SPOKEN, "--affiche", JINGLE_DISPLAY, "--sans-diffusion"],
                         capture_output=True, text=True, cwd=str(HERE), timeout=900, encoding="utf-8", errors="replace",
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    m = re.search(r"annonce (jingles-annonces:\d+)", res.stdout or "")
    if not m:
        sys.stderr.write(f"[{datetime.now():%H:%M:%S}] jingle des créations : échec {(res.stderr or '')[-200:]}\n")
        return None
    DIR.mkdir(parents=True, exist_ok=True)
    write_json(JINGLE_STATE, {"key": m.group(1), "spoken": JINGLE_SPOKEN, "created_at": now_iso()})
    return m.group(1)


def wait_comfy_idle(limit_s=COMFY_WAIT_S):
    t0 = time.time()
    while gpu.comfy_queue_size() > 0:
        if time.time() - t0 > limit_s:
            raise SongError("timeout", "file ComfyUI occupée")
        time.sleep(COMFY_POLL_S)
    gpu.free_comfy()
    gpu.free_ollama()
    return round(time.time() - t0, 1)


class SongQueue:
    def __init__(self, folder=DIR, schedule=None, music_busy=None, gpu_lock=None, lyrics=None, music=None, finalize=None,
                 prepare=None, before_music=None):
        self.dir = Path(folder)
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.gpu = gpu_lock or gpu.LOCK
        self.jobs = {}
        self.order = []
        self.schedule = schedule or (lambda key: False)
        self.music_busy = music_busy or (lambda: gpu.rotation_running() or gpu.own_worker_running())
        self.lyrics = lyrics or self._lyrics
        self.music = music or self._music
        self.finalize = finalize or self._finalize
        self.prepare = prepare or ensure_playlist
        self.before_music = before_music or wait_comfy_idle
        self.dir.mkdir(parents=True, exist_ok=True)
        self._load()

    def _path(self, job_id):
        return self.dir / f"{job_id}.json"

    def _save(self, job):
        write_json(self._path(job["id"]), job)

    def _load(self):
        pending = []
        for f in self.dir.glob("*.json"):
            if not ID_RE.match(f.stem):
                continue
            job = read_json(f, None)
            if not isinstance(job, dict):
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
                out["stage"] = job.get("stage", "lyrics")
                out["started_at"] = job.get("started_at")
            elif job["status"] == "ready":
                out.update(title=job.get("title", ""), key=job.get("key"), scheduled=bool(job.get("scheduled")),
                           duration=job.get("duration_s"))
            elif job["status"] == "error":
                out["error"] = job.get("error") or ERRORS["failed"]
            return out

    def _next(self):
        with self.lock:
            return self.jobs.get(self.order[0]) if self.order else None

    def _set(self, job, **fields):
        with self.lock:
            job.update(fields)
            try:
                self._save(job)
            except OSError as e:
                sys.stderr.write(f"[{datetime.now():%H:%M:%S}] morceau {job['id'][:8]} : sauvegarde impossible : {e}\n")

    def run_once(self):
        job = self._next()
        if job is None:
            return False
        with self.gpu:
            busy = self.music_busy()
            if not busy:
                self._process(job)
        if busy:
            if not job.get("waiting_music"):
                self._set(job, waiting_music=True)
            self.wake.wait(MUSIC_POLL_S)
            self.wake.clear()
        return True

    def _lyrics(self, job):
        waited = wait_comfy_idle()
        ensure_ollama()
        try:
            res = write_lyrics(job["prompt"], job["duration"], LYRICS_DIR / f"{job['id']}.txt")
            res["comfy_wait_s"] = waited
            return res
        finally:
            gpu.free_ollama()

    def _music(self, job):
        with self.lock:
            cfg = read_json(CONFIG, None)
            if not isinstance(cfg, dict):
                raise SongError("music", "config.json illisible")
            cases = cfg.setdefault("test_cases", [])
            case = next((c for c in cases if c.get("request_id") == job["id"]), None)
            if case is None:
                case_id = str(max([int(c["id"]) for c in cases if str(c.get("id", "")).isdigit()] + [0]) + 1)
                case = {"id": case_id, "name": job["title"], "prompt": job["caption"], "type": "vocal",
                        "duration": job["duration"], "duration_fixed": True,
                        "lyrics_file": f"playlists/{PID}/lyrics/{job['id']}.txt", "language": "fr",
                        "seed": job["seed"], "request_id": job["id"]}
                if job.get("bpm"):
                    case["bpm"] = job["bpm"]
                cases.append(case)
                write_json(CONFIG, cfg)
        job["case_id"] = case["id"]
        entry = result_entry(case["id"])
        if not (entry and entry.get("status") == "generated" and (HERE / entry["output_file"]).exists()):
            job["timings"]["music_wait_s"] = self.before_music()
            ace_generate(case["id"], ACE_BASE_S + ACE_PER_S * job["duration"])
            entry = result_entry(case["id"])
        if not entry or entry.get("status") != "generated":
            raise SongError("music", (entry or {}).get("error") or "aucun morceau produit")
        return entry

    def _finalize(self, job, entry):
        wav = HERE / entry["output_file"]
        mp3 = wav.with_suffix(".mp3")
        if wav.exists():
            duration = finalize_audio(wav)
        elif mp3.exists():
            duration = entry.get("duration")
        else:
            raise SongError("finalize", "fichier audio introuvable")
        meta_path = HERE / entry.get("metadata_file", "")
        meta = read_json(meta_path, None) if entry.get("metadata_file") else None
        if isinstance(meta, dict):
            meta["user_request"] = {"request_id": job["id"], "user_prompt": job["prompt"], "requested_at": job["created_at"],
                                    "lyrics_model": LLM_MODEL, "lyrics_model_runtime": "Ollama local",
                                    "lyrics_temperature": LLM_TEMPERATURE, "lyrics_system_prompt": SYSTEM_PROMPT,
                                    "lyrics_attempts": job.get("lyrics_attempts"), "lyrics_check": job.get("lyrics_check"),
                                    "artists_cited": job.get("artists_cited"), "bpm": job.get("bpm")}
            meta["audio_mp3"] = str(mp3.relative_to(HERE)).replace("\\", "/")
            write_json(meta_path, meta)
        key = f"{PID}:{job['case_id']}"
        return key, duration

    def _process(self, job):
        with self.lock:
            if job["id"] in self.order:
                self.order.remove(job["id"])
            job.pop("waiting_music", None)
            job.update(status="running", started_at=now_iso(), stage=job.get("stage") or "lyrics")
            job.setdefault("timings", {})
            job.setdefault("seed", secrets.randbelow(2 ** 32))
            job.setdefault("duration", pick_duration())
        t_all = time.time()
        stage = "lyrics"
        try:
            with self.lock:
                self._save(job)
            self.prepare()
            if not job.get("lyrics"):
                t0 = time.time()
                res = self.lyrics(job)
                self._set(job, title=res["title"], caption=res["caption"], bpm=res.get("bpm"), lyrics=res["lyrics"],
                          artists_cited=res.get("artists_cited", []), lyrics_attempts=res.get("attempts"),
                          lyrics_check=res.get("check"), lyrics_model=LLM_MODEL, stage="music",
                          timings=dict(job["timings"], lyrics_s=round(time.time() - t0, 1), lyrics_wait_s=res.get("comfy_wait_s")))
            stage = "music"
            self._set(job, stage="music")
            t0 = time.time()
            entry = self.music(job)
            self._set(job, stage="finalize", output_file=entry.get("output_file"), metadata_file=entry.get("metadata_file"),
                      ace_elapsed_s=entry.get("elapsed_s"), timings=dict(job["timings"], music_s=round(time.time() - t0, 1)))
            stage = "finalize"
            t0 = time.time()
            key, duration = self.finalize(job, entry)
            scheduled = bool(self.schedule(key))
            self._set(job, status="ready", key=key, duration_s=duration, scheduled=scheduled, finished_at=now_iso(),
                      timings=dict(job["timings"], finalize_s=round(time.time() - t0, 1), total_s=round(time.time() - t_all, 1)))
        except Exception as e:
            kind = e.kind if isinstance(e, SongError) else (stage if stage in ERRORS else "failed")
            self._set(job, status="error", error=ERRORS.get(kind, ERRORS["failed"]), error_stage=stage,
                      detail=f"{type(e).__name__}: {e}"[:400], finished_at=now_iso(),
                      timings=dict(job.get("timings") or {}, total_s=round(time.time() - t_all, 1)))
            sys.stderr.write(f"[{datetime.now():%H:%M:%S}] morceau {job['id'][:8]} : échec ({stage}) {type(e).__name__}: {str(e)[:160]}\n")

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
                sys.stderr.write(f"[{datetime.now():%H:%M:%S}] file de morceaux : {type(e).__name__}: {e}\n")
                time.sleep(5)
