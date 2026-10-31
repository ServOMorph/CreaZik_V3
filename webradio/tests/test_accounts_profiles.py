import http.client
import json
import re
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import accounts

PLUGINS_DIR = ROOT / "plugins"
PROFILES_DIR = ROOT / "profiles"
ADMIN_PLUGINS = ["view-as", "commandes-globales", "programmation", "dynamique", "outils-radio", "jingle-texte", "tests",
                 "pochettes", "gestion", "suivi"]
USER_FILES = ("styles.js", "image.js", "song.js", "sponsor.js")
ADMIN_FILES = ("view_as.js", "view_as.css", "admin.css", "commandes_globales.js", "programmation.js", "dynamique.js",
               "outils_radio.js", "jingle_texte.js", "tests.js", "pochettes.js", "gestion.js", "suivi.js")


@pytest.fixture
def acc_file(tmp_path, monkeypatch):
    path = tmp_path / "user_accounts.json"
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", path)
    return path


def test_hash_and_check(acc_file):
    uid = accounts.add_account("Olive", "Olive", "traveling-sound")
    assert uid == "olive"
    raw = acc_file.read_text(encoding="utf-8")
    data = json.loads(raw)["users"]["olive"]
    assert data["id"] == "Olive" and data["profile"] == "traveling-sound"
    assert '"Olive"' not in raw.replace('"id": "Olive"', "")
    assert data["hash"] == accounts.hash_pw("Olive", data["salt"])
    assert len(data["salt"]) == 32


def test_case_rules(acc_file):
    accounts.add_account("Olive", "Olive", "traveling-sound")
    assert accounts.check_account("OLIVE", "Olive") == "olive"
    assert accounts.check_account(" olive ", "Olive") == "olive"
    assert accounts.check_account("olive", "olive") is None
    assert accounts.check_account("olive", "OLIVE") is None
    assert accounts.check_account("inconnu", "Olive") is None


def test_add_account_refusals(acc_file):
    with pytest.raises(ValueError):
        accounts.add_account("Admin", "x", "classique")
    with pytest.raises(ValueError):
        accounts.add_account("a b", "x", "classique")
    with pytest.raises(ValueError):
        accounts.add_account("bob", "", "classique")
    with pytest.raises(ValueError):
        accounts.add_account("bob", "x", "inexistant")
    assert not acc_file.exists()


def test_session_token():
    secret = bytes(32)
    tok = accounts.make_session("Olive", secret, now=1000, ttl=60)
    assert accounts.read_session(tok, secret, now=1059) == "olive"
    assert accounts.read_session(tok, secret, now=1061) is None
    assert accounts.read_session(tok, b"\x01" * 32, now=1000) is None
    uid, exp, sig = tok.split(".")
    assert accounts.read_session(f"admin.{exp}.{sig}", secret, now=1000) is None
    assert accounts.read_session("", secret) is None
    assert accounts.read_session(None, secret) is None


def test_secret_file(tmp_path):
    path = tmp_path / "secret.key"
    first = accounts.load_secret(path)
    assert len(first) == 32 and accounts.load_secret(path) == first


def test_manifest_valid():
    plugins = accounts.load_plugins()
    assert accounts.validate_plugins(plugins, PLUGINS_DIR) == []
    ids = [p["id"] for p in plugins]
    assert {"styles", "image", "song", "sponsor"} <= set(ids)
    assert [p["id"] for p in plugins if p["scope"] == "admin"] == ADMIN_PLUGINS
    assert all(p["slot"] == "card" for p in plugins if p["scope"] == "admin" and p["id"] not in ("view-as", "commandes-globales"))
    assert accounts.admin_only_files(plugins) == set(ADMIN_FILES)


def test_manifest_rejects_bad_entries():
    bad = [{"id": "x", "title": "X", "scope": "root", "file": "../x.js"}, {"id": "x", "title": "", "scope": "user", "file": "x.js"}]
    errors = accounts.validate_plugins(bad)
    assert any("portée" in e for e in errors) and any("file" in e for e in errors)
    assert any("double" in e for e in errors) and any("titre" in e for e in errors)


def test_profiles_valid():
    ids = {p["id"] for p in accounts.load_plugins()}
    profiles = accounts.list_profiles()
    assert set(profiles) >= {"classique", "traveling-sound"}
    for p in profiles.values():
        assert accounts.validate_profile(p, ids) == []
    ts, cl = profiles["traveling-sound"], profiles["classique"]
    assert ts["plugins"] == ["styles", "image", "song", "sponsor"]
    assert ts["sponsor"]["url"].startswith("https://sites.google.com/view/traveling-sound-webradio")
    assert set(ts["ad_groups"]) == {"serenia", "traveling_sound", "radio", "messages"}
    assert ts["jingle_categories"] == ["traveling-sound"]
    assert cl["plugins"] == ["styles"] and cl["sponsor"] is None
    assert set(cl["ad_groups"]) == {"serenia", "radio"} and cl["jingle_categories"] == []
    for f in PROFILES_DIR.glob("*.json"):
        assert not re.search(r"hash|salt|password|secret", f.read_text(encoding="utf-8"), re.I)


def test_load_profile_rejects_traversal():
    assert accounts.load_profile("../admin_credentials") is None
    assert accounts.load_profile("Classique") is None


def test_build_session_roles():
    anon = accounts.build_session("anon", None)
    assert anon["profile"]["id"] == "classique" and [p["id"] for p in anon["plugins"]] == ["styles"]
    assert "profiles" not in anon and anon["view_as"] is None
    user = accounts.build_session("user", "Olive", profile_id="traveling-sound", view_as="classique")
    assert user["profile"]["id"] == "traveling-sound" and user["view_as"] is None
    assert [p["id"] for p in user["plugins"]] == ["styles", "image", "song", "sponsor"]
    assert all(p["scope"] == "user" for p in user["plugins"])
    lost = accounts.build_session("user", "x", profile_id="supprime")
    assert lost["profile"]["id"] == "classique"
    admin = accounts.build_session("admin", "admin")
    assert admin["profile"]["jingle_categories"] is None
    assert [p["id"] for p in admin["plugins"]] == ["styles", "image", "song", "sponsor"] + ADMIN_PLUGINS
    assert {p["id"] for p in admin["profiles"]} >= {"classique", "traveling-sound"}
    view = accounts.build_session("admin", "admin", view_as="classique")
    assert view["view_as"] == "classique" and [p["id"] for p in view["plugins"]] == ["styles"] + ADMIN_PLUGINS
    assert accounts.build_session("admin", "admin", view_as="nope")["view_as"] is None


class _FakeEngine:
    def __init__(self, *a, **k):
        self.lock = threading.RLock()
        self.db = None

    def snapshot(self, admin=False):
        return {"admin": admin}


@pytest.fixture(scope="module")
def srv(tmp_path_factory):
    import radio_engine
    original = radio_engine.RadioEngine
    radio_engine.RadioEngine = _FakeEngine
    sys.modules.pop("server", None)
    try:
        import server
    finally:
        radio_engine.RadioEngine = original
    tmp = tmp_path_factory.mktemp("srv")
    saved = (accounts.ACCOUNTS_FILE, server.STATE.cred, server.STATE.session_secret)
    accounts.ACCOUNTS_FILE = tmp / "user_accounts.json"
    server.STATE.cred = server.new_credentials("motdepasse-admin", False)
    server.STATE.session_secret = bytes(range(32))
    accounts.add_account("Olive", "Olive", "traveling-sound")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    httpd.interface = "user"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield server, httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()
    accounts.ACCOUNTS_FILE, server.STATE.cred, server.STATE.session_secret = saved


def _req(port, method, path, body=None, cookies=None, ctype=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    headers = {}
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    if ctype:
        headers["Content-Type"] = ctype
    conn.request(method, path, body=body, headers=headers)
    r = conn.getresponse()
    data = r.read()
    out = (r.status, r.getheader("Location"), r.msg.get_all("Set-Cookie") or [], data)
    conn.close()
    return out


def _login(port, user, password):
    server_module = sys.modules["server"]
    server_module.STATE.login_fails.clear()
    status, loc, set_cookies, _ = _req(port, "POST", "/login", urlencode({"user": user, "password": password}),
                                       ctype="application/x-www-form-urlencoded")
    jar = {}
    for c in set_cookies:
        k, _, rest = c.partition("=")
        v = rest.split(";")[0]
        if v:
            jar[k] = v
    return status, loc, jar


def _session(port, jar):
    return json.loads(_req(port, "GET", "/api/session", cookies=jar)[3])


ADMIN_GETS = ["/api/radio/stats", "/api/radio/library", "/api/tests", "/api/covers/review", "/api/catalog/overrides",
              "/api/radio/analytics", "/api/suivi"]


def test_http_anon(srv):
    _, port = srv
    s = _session(port, {})
    assert s["role"] == "anon" and s["profile"]["id"] == "classique" and "profiles" not in s
    assert _req(port, "GET", "/api/me")[3] == b'{"admin": false, "default_password": false}'


def test_http_profile_login_and_no_admin(srv):
    _, port = srv
    status, loc, jar = _login(port, "OLIVE", "Olive")
    assert status == 303 and loc == "/" and "creazik_session" in jar and "creazik_admin" not in jar
    s = _session(port, jar)
    assert s["role"] == "user" and s["user"] == "Olive" and s["profile"]["id"] == "traveling-sound"
    assert "profiles" not in s and all(p["scope"] == "user" for p in s["plugins"])
    for path in ADMIN_GETS:
        assert _req(port, "GET", path, cookies=jar)[0] == 401, path
    assert json.loads(_req(port, "GET", "/api/me", cookies=jar)[3])["admin"] is False
    assert _req(port, "GET", "/api/radio/state", cookies=jar)[3] == b'{"admin": false}'
    st, loc2, _, _ = _req(port, "GET", "/radio.html", cookies=jar)
    assert st == 303 and loc2.startswith("/login")
    for path in ("/api/radio/action", "/api/catalog", "/api/radio", "/api/content", "/api/admin/password", "/api/session/view-as"):
        assert _req(port, "POST", path, b"{}", cookies=jar, ctype="application/json")[0] == 401, path
    forged = dict(jar, creazik_view_as="classique")
    assert _session(port, forged)["profile"]["id"] == "traveling-sound"


def test_http_bad_password(srv):
    _, port = srv
    for user, pw in (("olive", "olive"), ("Olive", "OLIVE"), ("admin", "Olive"), ("inconnu", "x")):
        status, _, jar = _login(port, user, pw)
        assert status == 401 and not jar


def test_http_admin_and_view_as(srv):
    _, port = srv
    status, loc, jar = _login(port, "ADMIN", "motdepasse-admin")
    assert status == 303 and loc == "/" and "creazik_admin" in jar
    s = _session(port, jar)
    assert s["role"] == "admin" and s["profile"]["id"] == "admin" and s["view_as"] is None
    assert _req(port, "GET", "/api/tests", cookies=jar)[0] == 200
    st, _, cookies, body = _req(port, "POST", "/api/session/view-as", json.dumps({"profile": "traveling-sound"}),
                                cookies=jar, ctype="application/json")
    assert st == 200 and json.loads(body)["view_as"] == "traveling-sound"
    assert any(c.startswith("creazik_view_as=traveling-sound") for c in cookies)
    s2 = _session(port, dict(jar, creazik_view_as="traveling-sound"))
    assert s2["profile"]["id"] == "traveling-sound" and s2["role"] == "admin"
    assert [p["id"] for p in s2["plugins"]][-len(ADMIN_PLUGINS):] == ADMIN_PLUGINS
    st, _, _, _ = _req(port, "POST", "/api/session/view-as", json.dumps({"profile": "../x"}), cookies=jar, ctype="application/json")
    assert st == 400
    st, _, cookies, body = _req(port, "POST", "/api/session/view-as", json.dumps({"profile": ""}), cookies=jar, ctype="application/json")
    assert st == 200 and json.loads(body)["view_as"] is None and any("Max-Age=0" in c for c in cookies)
    assert _req(port, "POST", "/api/session/view-as", json.dumps({"profile": "classique"}))[0] == 401


def test_http_admin_next_and_logout(srv):
    _, port = srv
    status, loc, _ = _login(port, "admin", "motdepasse-admin")
    assert loc == "/"
    srv[0].STATE.login_fails.clear()
    body = urlencode({"user": "admin", "password": "motdepasse-admin", "next": "/radio.html"})
    st, loc, _, _ = _req(port, "POST", "/login", body, ctype="application/x-www-form-urlencoded")
    assert st == 303 and loc == "/radio.html"
    srv[0].STATE.login_fails.clear()
    body = urlencode({"user": "Olive", "password": "Olive", "next": "/radio.html"})
    st, loc, _, _ = _req(port, "POST", "/login", body, ctype="application/x-www-form-urlencoded")
    assert st == 303 and loc == "/"
    st, loc, cookies, _ = _req(port, "GET", "/logout")
    assert st == 303 and loc == "/"
    names = {c.split("=")[0] for c in cookies if "Max-Age=0" in c}
    assert names == {"creazik_admin", "creazik_session", "creazik_view_as"}


def test_http_login_rate_limit(srv):
    server, port = srv
    server.STATE.login_fails.clear()
    for _ in range(server.LOGIN_MAX_FAILS):
        _req(port, "POST", "/login", urlencode({"user": "x", "password": "y"}), ctype="application/x-www-form-urlencoded")
    st = _req(port, "POST", "/login", urlencode({"user": "Olive", "password": "Olive"}), ctype="application/x-www-form-urlencoded")[0]
    assert st == 429
    server.STATE.login_fails.clear()


def test_http_plugin_static(srv, monkeypatch):
    _, port = srv
    monkeypatch.chdir(ROOT)
    _, _, olive = _login(port, "Olive", "Olive")
    _, _, admin = _login(port, "admin", "motdepasse-admin")
    for jar in ({}, olive):
        st, _, _, body = _req(port, "GET", "/plugins/index.json", cookies=jar)
        assert st == 200 and {p["scope"] for p in json.loads(body)} == {"user"}
        for f in USER_FILES:
            assert _req(port, "GET", "/plugins/" + f, cookies=jar)[0] == 200, f
        for f in ADMIN_FILES:
            assert _req(port, "GET", "/plugins/" + f, cookies=jar)[0] == 404, f
    st, _, _, body = _req(port, "GET", "/plugins/index.json", cookies=admin)
    assert st == 200 and [p["id"] for p in json.loads(body) if p["scope"] == "admin"] == ADMIN_PLUGINS
    for f in USER_FILES + ADMIN_FILES:
        assert _req(port, "GET", "/plugins/" + f, cookies=admin)[0] == 200, f
    assert _req(port, "GET", "/profiles/classique.json")[0] == 404
    assert _req(port, "GET", "/user_accounts.json")[0] == 404
    assert _req(port, "GET", "/session_secret.key")[0] == 404


def test_profile_may_list_admin_plugin(tmp_path):
    for f in PROFILES_DIR.glob("*.json"):
        (tmp_path / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    prof = json.loads((tmp_path / "classique.json").read_text(encoding="utf-8"))
    prof["plugins"] = ["tests", "styles"]
    (tmp_path / "classique.json").write_text(json.dumps(prof), encoding="utf-8")
    ids = {p["id"] for p in accounts.load_plugins()}
    assert accounts.validate_profile(prof, ids) == []
    anon = accounts.build_session("anon", None, profiles_dir=tmp_path)
    assert [p["id"] for p in anon["plugins"]] == ["styles"]
    user = accounts.build_session("user", "x", profile_id="classique", profiles_dir=tmp_path)
    assert [p["id"] for p in user["plugins"]] == ["styles"]
    view = accounts.build_session("admin", "admin", view_as="classique", profiles_dir=tmp_path)
    got = [p["id"] for p in view["plugins"]]
    assert got[:2] == ["tests", "styles"] and got.count("tests") == 1 and set(ADMIN_PLUGINS) <= set(got)


def test_http_redirects_and_home(srv, monkeypatch):
    _, port = srv
    monkeypatch.chdir(ROOT)
    _, _, admin = _login(port, "admin", "motdepasse-admin")
    for jar in ({}, admin):
        for path in ("/listen.html", "/suivi.html", "/index.html"):
            st, loc, _, _ = _req(port, "GET", path, cookies=jar)
            assert st == 303 and loc == "/", path
        st, _, _, body = _req(port, "GET", "/", cookies=jar)
        assert st == 200 and b'data-plugin-slot="player"' in body
        assert b"testsPanel" not in body and b"progPanel" not in body and b"adminFrame" not in body
    st, loc, _, _ = _req(port, "GET", "/radio.html")
    assert st == 303 and loc.startswith("/login")
    assert _req(port, "GET", "/radio.html", cookies=admin)[0] == 200
    srv[0].STATE.login_fails.clear()
    body = urlencode({"user": "admin", "password": "motdepasse-admin", "next": "/listen.html"})
    st, loc, _, _ = _req(port, "POST", "/login", body, ctype="application/x-www-form-urlencoded")
    assert st == 303 and loc == "/"


JINGLE_ID = "0" * 32


def test_http_jingle_refused_without_admin(srv):
    _, port = srv
    _, _, olive = _login(port, "Olive", "Olive")
    for jar in ({}, olive):
        body = json.dumps({"text": "Bonjour", "engine": "kokoro", "dry_run": True})
        assert _req(port, "POST", "/api/admin/jingle", body, cookies=jar, ctype="application/json")[0] == 401
        assert _req(port, "GET", "/api/admin/jingle/" + JINGLE_ID, cookies=jar)[0] == 401
        s = _session(port, jar)
        assert all(p["scope"] == "user" for p in s["plugins"])


def test_http_jingle_validation_and_dry_run(srv):
    server, port = srv
    _, _, admin = _login(port, "admin", "motdepasse-admin")
    calls = []
    server.JINGLES.runner = lambda job: calls.append(job) or {"key": "x:1", "duration_s": 1.0, "broadcast": True}

    def post(body, ctype="application/json"):
        return _req(port, "POST", "/api/admin/jingle", body, cookies=admin, ctype=ctype)

    assert post(json.dumps({"text": "Bonjour"}), ctype="text/plain")[0] == 415
    assert post("{pas du json")[0] == 400
    assert post(json.dumps(["Bonjour"]))[0] == 400
    assert post(json.dumps({"text": "   "}))[0] == 400
    assert post(json.dumps({"text": 12}))[0] == 400
    assert post(json.dumps({"text": "x" * 301}))[0] == 400
    assert post(json.dumps({"text": "Bonjour", "engine": "espeak"}))[0] == 400
    st, _, _, body = post(json.dumps({"text": "Bienvenue sur CréaZik IA WebRadio", "engine": "kokoro", "dry_run": True}))
    job = json.loads(body)
    assert st == 201 and job["status"] == "queued" and job["dry_run"] is True
    assert job["text"] == "Bienvenue sur CréaZik IA WebRadio"
    assert job["spoken"] == "Bienvenue sur Créa Zique I A Ouèbe Radio"
    assert server.JINGLES.process_one()
    st, _, _, body = _req(port, "GET", "/api/admin/jingle/" + job["id"], cookies=admin)
    done = json.loads(body)
    assert st == 200 and done["status"] == "ready" and done["broadcast"] is False and calls == []
    assert _req(port, "GET", "/api/admin/jingle/" + JINGLE_ID, cookies=admin)[0] == 404
    st, _, _, body = post(json.dumps({"text": "x" * 300, "engine": "chatterbox"}))
    assert st == 201
    assert server.JINGLES.process_one()
    done = json.loads(_req(port, "GET", "/api/admin/jingle/" + json.loads(body)["id"], cookies=admin)[3])
    assert done["status"] == "ready" and done["broadcast"] is True and calls[0]["engine"] == "chatterbox"
