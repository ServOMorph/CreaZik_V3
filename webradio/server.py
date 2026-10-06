import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from radio_engine import RadioEngine

HERE = Path(__file__).parent.resolve()
CRED_FILE = HERE / "admin_credentials.json"
COMMENTS_FILE = HERE / "comments.json"
COOKIE = "creazik_admin"
MAX_BODY = 256 * 1024
PBKDF2_ROUNDS = 200_000
LOGIN_WINDOW_S = 60
LOGIN_MAX_FAILS = 5
COMMENT_WINDOW_S = 60
COMMENT_MAX_PER_WINDOW = 3
COMMENT_MAX_STORED = 1000

ADMIN_POST_TARGETS = {
    "/api/favorites": (HERE / "favorites.json", "list"),
    "/api/radio": (HERE / "radio_settings.json", "dict"),
    "/api/content": (HERE / "radio_content.json", "dict"),
}

STATIC_FILES = {"/listen.html", "/silence.wav", "/listen.css", "/listen.js", "/visuals.js", "/cover-placeholder.png",
                "/traveling-sound.png", "/scenes.js", "/transitions.js", "/motion.js", "/scenes_spec.json", "/radio_content.json",
                "/playlists.json", "/favorites.json", "/radio_settings.json"}
STATIC_PATTERNS = [
    re.compile(r"^/playlists/[\w\-]+/outputs/playlist_results\.json$"),
    re.compile(r"^/playlists/[\w\-]+/outputs/[^/]+\.cover\.png$"),
    re.compile(r"^/playlists/[\w\-]+/outputs/[^/]+\.(?:wav|mp3|flac|ogg)$"),
    re.compile(r"^/playlists/[\w\-]+/outputs/[^/]+\.(?:wav|mp3|flac|ogg)\.viz\.json$"),
    re.compile(r"^/[\w\-]+/(?:outputs/)?[^/]+\.(?:wav|mp3|flac|ogg)\.viz\.json$"),
    re.compile(r"^/radio/[\w\-]+\.json$"),
]
ADMIN_PAGES = {"/radio.html", "/ui.html"}
LOGIN_NEXT = ("/radio.html", "/ui.html", "/listen.html")

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
RESULTS_RE = re.compile(r"^/playlists/[\w\-]+/outputs/playlist_results\.json$")
CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
       "media-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CréaZik IA WebRadio - Connexion admin</title>
<style>
body{font-family:-apple-system,Segoe UI,sans-serif;background:#1e1e2e;color:#e0e0e0;display:flex;
min-height:100vh;align-items:center;justify-content:center;margin:0;padding:16px}
form{background:rgba(255,255,255,.06);border:1px solid #ff6b9d;border-radius:12px;padding:20px;width:100%;max-width:360px}
h1{font-size:1.2em;color:#ff6b9d;margin:0 0 14px}
input{width:100%;box-sizing:border-box;min-height:44px;padding:8px 10px;border-radius:8px;border:1px solid #666;
background:#2d2d44;color:#fff;font-size:1em;margin-bottom:12px}
button{width:100%;min-height:44px;border-radius:8px;border:none;background:#ff6b9d;color:#fff;font-size:1em;font-weight:600}
a{color:#6496ff;font-size:.85em}
.err{color:#f44336;font-size:.85em;margin-bottom:10px}
</style></head><body>
<form method="post" action="/login">
<h1>CréaZik IA WebRadio - Espace admin</h1>
__ERR__
<input type="hidden" name="next" value="__NEXT__">
<input type="text" name="user" placeholder="Identifiant" autocomplete="username" autocapitalize="none" autofocus>
<input type="password" name="password" placeholder="Mot de passe" autocomplete="current-password">
<button type="submit">Se connecter</button>
<p style="margin:12px 0 0"><a href="/ui.html">Retour à l'écoute</a></p>
</form></body></html>"""


def hash_pw(password, salt_hex):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ROUNDS).hex()


def new_credentials(password, default):
    salt = secrets.token_hex(16)
    return {"user": "admin", "salt": salt, "hash": hash_pw(password, salt), "default": default}


def load_credentials():
    if CRED_FILE.exists():
        return json.loads(CRED_FILE.read_text(encoding="utf-8"))
    cred = new_credentials("admin", True)
    CRED_FILE.write_text(json.dumps(cred, indent=2), encoding="utf-8")
    return cred


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.cred = load_credentials()
        self.login_fails = []
        self.comment_times = {}

    def session_value(self):
        return hmac.new(bytes.fromhex(self.cred["hash"]), b"creazik-admin-session-v1", hashlib.sha256).hexdigest()

    def check_login(self, user, password):
        ok_user = hmac.compare_digest(user.encode(), self.cred["user"].encode())
        ok_pw = hmac.compare_digest(hash_pw(password, self.cred["salt"]), self.cred["hash"])
        return ok_user and ok_pw

    def set_password(self, password):
        self.cred = new_credentials(password, False)
        tmp = CRED_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.cred, indent=2), encoding="utf-8")
        os.replace(tmp, CRED_FILE)

    def login_blocked(self):
        now = time.time()
        with self.lock:
            self.login_fails[:] = [t for t in self.login_fails if now - t < LOGIN_WINDOW_S]
            return len(self.login_fails) >= LOGIN_MAX_FAILS

    def register_fail(self):
        with self.lock:
            self.login_fails.append(time.time())

    def comment_allowed(self, ip):
        now = time.time()
        with self.lock:
            times = [t for t in self.comment_times.get(ip, []) if now - t < COMMENT_WINDOW_S]
            if len(times) >= COMMENT_MAX_PER_WINDOW:
                self.comment_times[ip] = times
                return False
            times.append(now)
            self.comment_times[ip] = times
            return True


STATE = State()
ENGINE = RadioEngine(HERE, persist=True)
COMMENTS_LOCK = threading.Lock()

VOTES_FILE = HERE / "votes.json"
VOTES_LOCK = threading.Lock()
VOTE_KEY_RE = re.compile(r"^[\w\-]+:\d{1,4}$")
VOTER_COOKIE = "creazik_voter"
VOTE_WINDOW_S = 60
VOTE_MAX_PER_WINDOW = 600
VOTE_MAX_BATCH = 200
_vote_times = {}


def read_votes():
    try:
        data = json.loads(VOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data.setdefault("tracks", {})
    data.setdefault("voters", {})
    return data


def vote_allowed(ip, cost=1):
    now = time.time()
    with VOTES_LOCK:
        times = [t for t in _vote_times.get(ip, []) if now - t < VOTE_WINDOW_S]
        if len(times) + cost > VOTE_MAX_PER_WINDOW:
            _vote_times[ip] = times
            return False
        times.extend([now] * cost)
        _vote_times[ip] = times
        return True


def _mine_counts(raw):
    if isinstance(raw, dict):
        return {"up": int(raw.get("up", 0)), "down": int(raw.get("down", 0))}
    if raw in ("up", "down"):
        return {"up": 1 if raw == "up" else 0, "down": 1 if raw == "down" else 0}
    return {"up": 0, "down": 0}


def apply_vote(voter, key, vote, count=1):
    with VOTES_LOCK:
        data = read_votes()
        mine_all = data["voters"].setdefault(voter, {})
        mine = _mine_counts(mine_all.get(key))
        entry = data["tracks"].setdefault(key, {"up": 0, "down": 0, "score": 0})
        entry[vote] += count
        mine[vote] += count
        mine_all[key] = mine
        entry["score"] = entry["up"] - entry["down"]
        write_json_atomic(VOTES_FILE, data)
        return entry, mine


def reset_votes(key):
    with VOTES_LOCK:
        data = read_votes()
        data["tracks"][key] = {"up": 0, "down": 0, "score": 0}
        for mine in data["voters"].values():
            mine.pop(key, None)
        write_json_atomic(VOTES_FILE, data)


def read_comments():
    try:
        return json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def write_json_atomic(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def clean_text(s, limit):
    return CTRL_RE.sub("", str(s)).strip()[:limit]


class Handler(SimpleHTTPRequestHandler):
    server_version = "CreaZik"
    sys_version = ""

    def _is_https(self):
        return self.headers.get("X-Forwarded-Proto", "").lower() == "https"

    def _client_ip(self):
        ip = self.client_address[0]
        if ip in ("127.0.0.1", "::1"):
            fwd = self.headers.get("X-Forwarded-For") or self.headers.get("CF-Connecting-IP")
            if fwd:
                return fwd.split(",")[0].strip()
        return ip

    def _is_admin(self):
        for part in self.headers.get("Cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE and hmac.compare_digest(v, STATE.session_value()):
                return True
        return False

    def _is_user_interface(self):
        return getattr(self.server, "interface", "user") == "user"

    def _send_text(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _voter_id(self):
        for part in self.headers.get("Cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == VOTER_COOKIE and re.fullmatch(r"[0-9a-f]{32}", v):
                return v, None
        vid = secrets.token_hex(16)
        secure = "; Secure" if self._is_https() else ""
        return vid, f"{VOTER_COOKIE}={vid}; Path=/; Max-Age={365 * 86400}; HttpOnly; SameSite=Lax{secure}"

    def _send_json(self, code, obj, cookie=None):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _redirect(self, location, extra=None):
        self.send_response(303)
        self.send_header("Location", location)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _login_page(self, err="", nxt="/radio.html", code=200):
        html = LOGIN_PAGE.replace("__ERR__", f'<div class="err">{err}</div>' if err else "").replace("__NEXT__", nxt)
        self._send_text(code, html)

    def _allowed_static(self, path):
        return path in STATIC_FILES or any(p.match(path) for p in STATIC_PATTERNS)

    def _read_json_body(self, limit=MAX_BODY):
        n = int(self.headers.get("Content-Length", "0"))
        if n > limit:
            raise OverflowError
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def do_GET(self):
        self._route(head=False)

    def do_HEAD(self):
        self._route(head=True)

    def _route(self, head):
        parts = urlsplit(self.path)
        path = unquote(parts.path)
        if "\x00" in path or ".." in path.split("/"):
            self.send_error(400)
            return
        if self._is_user_interface() and (path in ADMIN_PAGES or path in ("/login", "/logout")):
            self.send_error(404)
            return
        if path == "/login":
            nxt = parse_qs(parts.query).get("next", ["/radio.html"])[0]
            self._login_page(nxt=nxt if nxt in LOGIN_NEXT else "/radio.html")
            return
        if path == "/logout":
            self._redirect("/ui.html", {"Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict"})
            return
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path == "/api/me":
            admin = self._is_admin() and not self._is_user_interface()
            self._send_json(200, {"admin": admin, "default_password": bool(admin and STATE.cred.get("default"))})
            return
        if path == "/api/radio/state":
            self._send_json(200, ENGINE.snapshot(admin=self._is_admin() and not self._is_user_interface()))
            return
        if path == "/api/radio/dynamics":
            self._send_json(200, ENGINE.dynamics_info())
            return
        if path == "/api/energy":
            self._send_json(200, ENGINE.energy())
            return
        if path == "/api/radio/stats":
            if not self._is_admin():
                self.send_error(401)
                return
            self._send_json(200, ENGINE.stats())
            return
        if path == "/api/radio/library":
            if not self._is_admin():
                self.send_error(401)
                return
            self._send_json(200, ENGINE.library())
            return
        if path == "/api/comments":
            key = parse_qs(parts.query).get("key", [""])[0]
            with COMMENTS_LOCK:
                items = read_comments()
            if key:
                items = [c for c in items if c.get("key") == key]
            self._send_json(200, items[-200:][::-1])
            return
        if path == "/api/votes":
            voter = self._voter_id()
            with VOTES_LOCK:
                data = read_votes()
            mine = {k: _mine_counts(v) for k, v in data["voters"].get(voter[0], {}).items()}
            self._send_json(200, {"tracks": data["tracks"], "mine": mine}, cookie=voter[1])
            return
        if path in ADMIN_PAGES:
            if not self._is_admin():
                self._redirect("/login?next=" + path)
                return
            self.path = path
            self._serve(head)
            return
        if path in ("/", "/index.html"):
            if self._is_user_interface():
                path = "/listen.html"
            else:
                self._redirect("/radio.html")
                return
        path = re.sub(r"^/playlists/perso-(electro|folk|rock|classique|gregorien|chorale)/",
                      r"/playlists/francais_tests-\1/", path)
        if not self._allowed_static(path):
            self.send_error(404)
            return
        if RESULTS_RE.match(path) and not (HERE / path.lstrip("/")).exists():
            self._send_json(200, {"model": "", "generations": []})
            return
        self.path = path
        self._serve(head)

    def do_POST(self):
        path = urlsplit(self.path).path
        if self._is_user_interface() and path not in ("/api/comments", "/api/vote"):
            self.send_error(404)
            return
        if path == "/login":
            self._login()
            return
        if path == "/api/comments":
            self._post_comment()
            return
        if path == "/api/vote":
            self._post_vote()
            return
        if not self._is_admin():
            self.send_error(401)
            return
        if not self.headers.get("Content-Type", "").lower().startswith("application/json"):
            self.send_error(415)
            return
        try:
            if path in ADMIN_POST_TARGETS:
                file, kind = ADMIN_POST_TARGETS[path]
                data = self._read_json_body()
                if kind == "list" and not (isinstance(data, list) and all(isinstance(x, str) for x in data)):
                    raise ValueError("liste de chaînes attendue")
                if kind == "dict" and not isinstance(data, dict):
                    raise ValueError("objet attendu")
                write_json_atomic(file, data)
                self.send_response(204)
                self.end_headers()
            elif path == "/api/radio/action":
                body = self._read_json_body(4096)
                ok = ENGINE.action(str(body.get("action", "")), body)
                self._send_json(200 if ok else 400, ENGINE.snapshot(admin=True))
            elif path == "/api/votes/reset":
                key = str(self._read_json_body(2048).get("key", ""))
                if not VOTE_KEY_RE.match(key):
                    raise ValueError("clé invalide")
                reset_votes(key)
                self.send_response(204)
                self.end_headers()
            elif path == "/api/comments/delete":
                cid = str(self._read_json_body(4096).get("id", ""))
                with COMMENTS_LOCK:
                    items = [c for c in read_comments() if c.get("id") != cid]
                    write_json_atomic(COMMENTS_FILE, items)
                self.send_response(204)
                self.end_headers()
            elif path == "/api/admin/password":
                body = self._read_json_body(4096)
                old, new = str(body.get("old", "")), str(body.get("new", ""))
                if not STATE.check_login(STATE.cred["user"], old):
                    self._send_json(403, {"error": "ancien mot de passe incorrect"})
                    return
                if len(new) < 8:
                    self._send_json(400, {"error": "8 caractères minimum"})
                    return
                STATE.set_password(new)
                secure = "; Secure" if self._is_https() else ""
                cookie = f"{COOKIE}={STATE.session_value()}; Path=/; Max-Age={30 * 86400}; HttpOnly; SameSite=Strict{secure}"
                self.send_response(204)
                self.send_header("Set-Cookie", cookie)
                self.end_headers()
            else:
                self.send_error(404)
        except OverflowError:
            self.send_error(413)
        except Exception as e:
            self.send_error(400, str(e)[:80])

    def _post_vote(self):
        try:
            body = self._read_json_body(2048)
            key = str(body.get("key", ""))
            vote = str(body.get("vote", ""))
            count = int(body.get("count", 1))
        except Exception:
            self.send_error(400)
            return
        if not VOTE_KEY_RE.match(key) or vote not in ("up", "down") or not 1 <= count <= VOTE_MAX_BATCH:
            self._send_json(400, {"error": "vote invalide"})
            return
        if not vote_allowed(self._client_ip(), count):
            self._send_json(429, {"error": "trop de votes, réessaie dans une minute"})
            return
        playlist_id = key.split(":")[0]
        try:
            known = {b["id"] for b in json.loads((HERE / "playlists.json").read_text(encoding="utf-8"))}
        except Exception:
            known = set()
        if playlist_id not in known:
            self._send_json(400, {"error": "morceau inconnu"})
            return
        voter, cookie = self._voter_id()
        entry, mine = apply_vote(voter, key, vote, count)
        self._send_json(200, {"key": key, "up": entry["up"], "down": entry["down"], "score": entry["score"],
                              "mine": mine}, cookie=cookie)

    def _post_comment(self):
        ip = self._client_ip()
        if not STATE.comment_allowed(ip):
            self._send_json(429, {"error": "trop de commentaires, réessaie dans une minute"})
            return
        try:
            body = self._read_json_body(8192)
        except Exception:
            self.send_error(400)
            return
        name = clean_text(body.get("name", ""), 30) or "Anonyme"
        text = clean_text(body.get("text", ""), 500)
        track = clean_text(body.get("track", ""), 120)
        key = str(body.get("key", ""))
        if key and not VOTE_KEY_RE.match(key):
            key = ""
        if not text:
            self._send_json(400, {"error": "commentaire vide"})
            return
        item = {"id": secrets.token_hex(4), "name": name, "text": text, "track": track, "key": key,
                "ts": datetime.now().isoformat(timespec="seconds")}
        with COMMENTS_LOCK:
            items = read_comments()
            items.append(item)
            write_json_atomic(COMMENTS_FILE, items[-COMMENT_MAX_STORED:])
        self._send_json(201, item)

    def _login(self):
        if STATE.login_blocked():
            self._login_page("Trop de tentatives, réessaie dans une minute.", code=429)
            return
        try:
            n = min(int(self.headers.get("Content-Length", "0")), 4096)
            form = parse_qs(self.rfile.read(n).decode("utf-8"))
            user = form.get("user", [""])[0]
            password = form.get("password", [""])[0]
            nxt = form.get("next", ["/radio.html"])[0]
        except Exception:
            user = password = ""
            nxt = "/radio.html"
        if nxt not in LOGIN_NEXT:
            nxt = "/radio.html"
        if STATE.check_login(user, password):
            secure = "; Secure" if self._is_https() else ""
            cookie = f"{COOKIE}={STATE.session_value()}; Path=/; Max-Age={30 * 86400}; HttpOnly; SameSite=Strict{secure}"
            self._redirect(nxt, {"Set-Cookie": cookie})
        else:
            STATE.register_fail()
            self._login_page("Identifiant ou mot de passe invalide.", nxt=nxt, code=401)

    def _serve(self, head):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            self.send_error(404)
            return
        if not rng:
            return super().do_HEAD() if head else super().do_GET()

        size = os.path.getsize(path)
        m = RANGE_RE.match(rng)
        if not m:
            return super().do_HEAD() if head else super().do_GET()
        start, end = m.groups()
        if start == "":
            n = int(end or 0)
            start, end = max(size - n, 0), size - 1
        else:
            start = int(start)
            end = int(end) if end else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        if head:
            return
        try:
            with open(path, "rb") as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()

    def log_message(self, fmt, *a):
        sys.stderr.write(f"[{datetime.now():%H:%M:%S}] {fmt % a}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1", help="127.0.0.1 par défaut (tunnel local) ; 0.0.0.0 pour le réseau local")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--admin-port", type=int, default=5001)
    p.add_argument("--no-browser", action="store_true")
    a = p.parse_args()

    os.chdir(HERE)
    threading.Thread(target=ENGINE.run, daemon=True).start()
    httpd = ThreadingHTTPServer((a.host, a.port), Handler)
    httpd.daemon_threads = True
    httpd.interface = "user"
    admin_httpd = ThreadingHTTPServer((a.host, a.admin_port), Handler)
    admin_httpd.daemon_threads = True
    admin_httpd.interface = "admin"
    url = f"http://localhost:{a.port}/"
    admin_url = f"http://localhost:{a.admin_port}/radio.html"
    print(f"Interface auditeur : {url} (écoute sur {a.host})")
    print(f"Interface admin : {admin_url} (locale uniquement)")
    if STATE.cred.get("default"):
        print("ATTENTION : mot de passe admin par défaut (admin/admin). Change-le dans la page Gestion WebRadio.")
    if not a.no_browser:
        threading.Timer(1, lambda: webbrowser.open(url)).start()
    threading.Thread(target=admin_httpd.serve_forever, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    finally:
        admin_httpd.shutdown()
        admin_httpd.server_close()
