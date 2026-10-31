import argparse
import http.client
import json
import os
import sys
import time
from urllib.parse import urlencode, urlsplit

USER = "admin"
ENV = "CREAZIK_ADMIN_PASSWORD"


class Client:
    def __init__(self, base):
        u = urlsplit(base)
        self.host, self.port = u.hostname, u.port or (443 if u.scheme == "https" else 80)
        self.https = u.scheme == "https"
        self.jar = {}

    def req(self, method, path, body=None, ctype=None, headers=None):
        cls = http.client.HTTPSConnection if self.https else http.client.HTTPConnection
        conn = cls(self.host, self.port, timeout=20)
        h = dict(headers or {})
        if self.jar:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.jar.items())
        if ctype:
            h["Content-Type"] = ctype
        conn.request(method, path, body=body.encode("utf-8") if isinstance(body, str) else body, headers=h)
        r = conn.getresponse()
        data = r.read()
        for c in r.msg.get_all("Set-Cookie") or []:
            k, _, rest = c.partition("=")
            v = rest.split(";")[0]
            if v and "Max-Age=0" not in c:
                self.jar[k] = v
            else:
                self.jar.pop(k, None)
        conn.close()
        return r.status, r.getheader("Location"), data

    def json(self, path):
        st, _, data = self.req("GET", path)
        try:
            return st, json.loads(data)
        except ValueError:
            return st, None


class Report:
    def __init__(self):
        self.fails = 0

    def check(self, label, ok, detail=""):
        print(("OK     " if ok else "ECHEC  ") + label + (f" ({detail})" if detail and not ok else ""))
        if not ok:
            self.fails += 1
        return ok


def main():
    p = argparse.ArgumentParser(description="Contrôles HTTP de bout en bout de la session admin (UI unique, plugins admin, jingle texte en mode d'essai).")
    p.add_argument("--base", default="http://localhost:5000", help="URL du serveur (défaut : http://localhost:5000)")
    a = p.parse_args()
    password = os.environ.get(ENV)
    if not password:
        print(f"Variable d'environnement {ENV} absente : rien n'est lancé.")
        return 2
    rep = Report()

    anon = Client(a.base)
    st, s = anon.json("/api/session")
    rep.check("anonyme : /api/session rôle anon sans plugin admin",
              st == 200 and s and s.get("role") == "anon" and all(x.get("scope") == "user" for x in s.get("plugins", [])), str(st))
    st, idx = anon.json("/plugins/index.json")
    rep.check("anonyme : manifeste filtré (plugins user seulement)", st == 200 and idx and {x["scope"] for x in idx} == {"user"}, str(st))
    for path in ("/plugins/programmation.js", "/plugins/admin.css", "/plugins/jingle_texte.js"):
        rep.check(f"anonyme : {path} refusé", anon.req("GET", path)[0] == 404)
    for path in ("/listen.html", "/suivi.html"):
        st, loc, _ = anon.req("GET", path)
        rep.check(f"redirection {path} -> /", st == 303 and loc == "/", f"{st} {loc}")
    rep.check("anonyme : POST /api/admin/jingle refusé (401)",
              anon.req("POST", "/api/admin/jingle", json.dumps({"text": "x", "dry_run": True}), "application/json")[0] == 401)

    adm = Client(a.base)
    st, loc, _ = adm.req("POST", "/login", urlencode({"user": USER, "password": password}), "application/x-www-form-urlencoded")
    if not rep.check("connexion admin (303 vers /, cookie creazik_admin)", st == 303 and loc == "/" and "creazik_admin" in adm.jar, f"{st} {loc}"):
        print("Arrêt : connexion admin impossible.")
        return 1
    st, s = adm.json("/api/session")
    ids = [x["id"] for x in (s or {}).get("plugins", [])]
    st_idx, full = adm.json("/plugins/index.json")
    admin_ids = [x["id"] for x in (full or []) if x.get("scope") == "admin"]
    rep.check("admin : /api/session rôle admin, profil admin", st == 200 and s.get("role") == "admin" and s["profile"]["id"] == "admin", str(st))
    rep.check("admin : tous les plugins admin du manifeste", st_idx == 200 and admin_ids and all(i in ids for i in admin_ids), ",".join(admin_ids))
    rep.check("admin : plugin image présent", "image" in ids)
    files = sorted({f for x in (full or []) if x.get("scope") == "admin" for f in (x.get("file"), x.get("css")) if f})
    bad = [f for f in files if adm.req("GET", "/plugins/" + f)[0] != 200]
    rep.check(f"admin : {len(files)} fichiers de plugins admin servis", not bad, ",".join(bad))
    st, state = adm.json("/api/radio/state")
    rep.check("admin : /api/radio/state contient played et queue", st == 200 and "played" in state and "queue" in state, str(st))
    for path in ("/api/tests", "/api/covers/review", "/api/suivi", "/api/radio/library", "/api/votes"):
        rep.check(f"admin : GET {path}", adm.req("GET", path)[0] == 200)
    rep.check("admin : /radio.html servi (embarqué par le plugin Gestion)", adm.req("GET", "/radio.html")[0] == 200)
    st, _, body = adm.req("GET", "/")
    rep.check("admin : / sert la page unique", st == 200 and b'data-plugin-slot="player"' in body, str(st))

    post = lambda payload: adm.req("POST", "/api/admin/jingle", json.dumps(payload), "application/json")
    rep.check("jingle : moteur inconnu refusé (400)", post({"text": "Bonjour", "engine": "inconnu", "dry_run": True})[0] == 400)
    rep.check("jingle : texte de 301 caractères refusé (400)", post({"text": "x" * 301, "dry_run": True})[0] == 400)
    rep.check("jingle : type non JSON refusé (415)",
              adm.req("POST", "/api/admin/jingle", json.dumps({"text": "x"}), "text/plain")[0] == 415)
    st, _, body = post({"text": "Essai automatique CréaZik IA WebRadio", "engine": "kokoro", "dry_run": True})
    job = json.loads(body) if st == 201 else {}
    if rep.check("jingle : demande d'essai acceptée (201, dry_run)", st == 201 and job.get("dry_run") is True, str(st)):
        rep.check("jingle : graphie phonétique appliquée", job.get("spoken") == "Essai automatique Créa Zique I A Ouèbe Radio", job.get("spoken", ""))
        final = {}
        for _ in range(40):
            st, final = adm.json("/api/admin/jingle/" + job["id"])
            if final and final.get("status") in ("ready", "error"):
                break
            time.sleep(0.5)
        rep.check("jingle : essai terminé sans diffusion", final and final.get("status") == "ready" and final.get("broadcast") is False,
                  json.dumps(final, ensure_ascii=False)[:200])
    adm.req("GET", "/logout")
    rep.check("déconnexion : cookie admin effacé", "creazik_admin" not in adm.jar)
    print(f"{rep.fails} échec(s)")
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
