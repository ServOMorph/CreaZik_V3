import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
PBKDF2_ROUNDS = 200_000
ACCOUNTS_FILE = HERE / "user_accounts.json"
SECRET_FILE = HERE / "session_secret.key"
PROFILES_DIR = HERE / "profiles"
PLUGINS_INDEX = HERE / "plugins" / "index.json"
DEFAULT_PROFILE = "classique"
SESSION_TTL_S = 30 * 86400
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.\-]{0,31}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,31}$")
PLUGIN_FILE_RE = re.compile(r"^[\w\-]+\.(?:js|css)$")
AD_GROUPS = ("serenia", "radio", "traveling_sound", "messages")
SCOPES = ("user", "admin")
SLOTS = ("card", "footer", "top", "player")
RESERVED_IDS = {"admin", "anon", "anonyme"}
_LOCK = threading.Lock()
_DUMMY_SALT = secrets.token_hex(16)


def hash_pw(password, salt_hex):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ROUNDS).hex()


def norm_id(user):
    return str(user or "").strip().lower()


def _read_json(path, fallback):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def _write_json(path, data):
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_accounts(path=None):
    path = path or ACCOUNTS_FILE
    data = _read_json(path, {})
    if not isinstance(data, dict) or not isinstance(data.get("users"), dict):
        data = {"users": {}}
    return data


def add_account(user, password, profile, path=None, profiles_dir=None):
    uid = norm_id(user)
    if not ID_RE.match(uid):
        raise ValueError("identifiant invalide (lettres, chiffres, . _ -, 32 caractères au plus)")
    if uid in RESERVED_IDS:
        raise ValueError("identifiant réservé")
    if not password:
        raise ValueError("mot de passe vide")
    if load_profile(profile, profiles_dir) is None:
        raise ValueError(f"profil inconnu : {profile}")
    path = path or ACCOUNTS_FILE
    salt = secrets.token_hex(16)
    with _LOCK:
        data = load_accounts(path)
        data["users"][uid] = {"id": str(user).strip(), "salt": salt, "hash": hash_pw(password, salt), "profile": profile,
                              "created": datetime.now().astimezone().isoformat(timespec="seconds")}
        _write_json(path, data)
    return uid


def get_account(uid, path=None):
    acc = load_accounts(path)["users"].get(norm_id(uid))
    return acc if isinstance(acc, dict) else None


def check_account(user, password, path=None):
    uid = norm_id(user)
    acc = get_account(uid, path)
    if acc is None:
        hash_pw(str(password), _DUMMY_SALT)
        return None
    if hmac.compare_digest(hash_pw(str(password), acc["salt"]), acc["hash"]):
        return uid
    return None


def load_secret(path=None):
    path = Path(path or SECRET_FILE)
    with _LOCK:
        try:
            raw = path.read_text(encoding="utf-8").strip()
            if re.fullmatch(r"[0-9a-f]{64}", raw):
                return bytes.fromhex(raw)
        except OSError:
            pass
        raw = secrets.token_hex(32)
        path.write_text(raw, encoding="utf-8")
        return bytes.fromhex(raw)


def _sign(secret, payload):
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def make_session(uid, secret, now=None, ttl=SESSION_TTL_S):
    exp = int((now if now is not None else time.time()) + ttl)
    payload = f"{norm_id(uid)}.{exp}"
    return f"{payload}.{_sign(secret, payload)}"


def read_session(value, secret, now=None):
    m = re.fullmatch(r"([a-z0-9][a-z0-9_.\-]{0,31})\.(\d{1,12})\.([0-9a-f]{64})", str(value or ""))
    if not m:
        return None
    uid, exp, sig = m.groups()
    if not hmac.compare_digest(sig, _sign(secret, f"{uid}.{exp}")):
        return None
    if int(exp) < (now if now is not None else time.time()):
        return None
    return uid


def load_plugins(path=None):
    data = _read_json(path or PLUGINS_INDEX, [])
    return data if isinstance(data, list) else []


def validate_plugins(plugins, plugins_dir=None):
    errors = []
    seen = set()
    for i, p in enumerate(plugins):
        if not isinstance(p, dict):
            errors.append(f"entrée {i} : objet attendu")
            continue
        pid = p.get("id")
        if not isinstance(pid, str) or not SLUG_RE.match(pid):
            errors.append(f"entrée {i} : id invalide")
        elif pid in seen:
            errors.append(f"{pid} : id en double")
        seen.add(pid)
        if not isinstance(p.get("title"), str) or not p["title"].strip():
            errors.append(f"{pid} : titre manquant")
        if p.get("scope") not in SCOPES:
            errors.append(f"{pid} : portée invalide")
        if p.get("slot", "card") not in SLOTS:
            errors.append(f"{pid} : emplacement invalide")
        for field in ("file", "css"):
            value = p.get(field)
            if field == "css" and value in (None, ""):
                continue
            if not isinstance(value, str) or not PLUGIN_FILE_RE.match(value):
                errors.append(f"{pid} : {field} invalide")
            elif plugins_dir is not None and not (Path(plugins_dir) / value).is_file():
                errors.append(f"{pid} : fichier {value} absent")
    return errors


def admin_only_files(plugins):
    def files(scope):
        return {f for p in plugins if isinstance(p, dict) and p.get("scope") == scope
                for f in (p.get("file"), p.get("css")) if isinstance(f, str) and f}
    return files("admin") - files("user")


def load_profile(pid, profiles_dir=None):
    if not isinstance(pid, str) or not SLUG_RE.match(pid):
        return None
    data = _read_json(Path(profiles_dir or PROFILES_DIR) / f"{pid}.json", None)
    if not isinstance(data, dict) or data.get("id") != pid:
        return None
    return data


def list_profiles(profiles_dir=None):
    profiles_dir = profiles_dir or PROFILES_DIR
    out = {}
    for f in sorted(Path(profiles_dir).glob("*.json")):
        p = load_profile(f.stem, profiles_dir)
        if p is not None:
            out[p["id"]] = p
    return out


def validate_profile(profile, plugin_ids):
    errors = []
    pid = profile.get("id") if isinstance(profile, dict) else None
    if not isinstance(pid, str) or not SLUG_RE.match(pid):
        return ["id invalide"]
    if not isinstance(profile.get("label"), str) or not profile["label"].strip():
        errors.append(f"{pid} : label manquant")
    plugins = profile.get("plugins")
    if not isinstance(plugins, list) or len(set(plugins)) != len(plugins or []):
        errors.append(f"{pid} : plugins doit être une liste sans doublon")
    else:
        errors.extend(f"{pid} : plugin inconnu {x}" for x in plugins if x not in plugin_ids)
    sponsor = profile.get("sponsor")
    if sponsor is not None:
        if not isinstance(sponsor, dict) or not str(sponsor.get("url", "")).startswith("https://") or not sponsor.get("name"):
            errors.append(f"{pid} : sponsor invalide (name et url https requis)")
    if "sponsor" in (plugins or []) and not sponsor:
        errors.append(f"{pid} : plugin sponsor sans sponsor")
    groups = profile.get("ad_groups")
    if not isinstance(groups, list) or any(g not in AD_GROUPS for g in groups):
        errors.append(f"{pid} : ad_groups invalide")
    cats = profile.get("jingle_categories")
    if not isinstance(cats, list) or not all(isinstance(c, str) for c in cats):
        errors.append(f"{pid} : jingle_categories doit être une liste")
    return errors


def admin_profile(profiles, plugins):
    sponsor = next((p["sponsor"] for p in profiles.values() if p.get("sponsor")), None)
    return {"id": "admin", "label": "Admin (tous les plugins)",
            "plugins": [p["id"] for p in plugins if p.get("scope") == "user" and (p["id"] != "sponsor" or sponsor)],
            "sponsor": sponsor, "ad_groups": list(AD_GROUPS), "jingle_categories": None}


def build_session(role, user, profile_id=None, view_as=None, profiles_dir=None, plugins_path=None):
    plugins = load_plugins(plugins_path)
    by_id = {p["id"]: p for p in plugins if isinstance(p, dict) and isinstance(p.get("id"), str)}
    profiles = list_profiles(profiles_dir)
    if role != "admin":
        view_as = None
    elif view_as not in profiles:
        view_as = None
    if role == "admin" and view_as is None:
        profile = admin_profile(profiles, plugins)
    else:
        pid = view_as or (profile_id if role == "user" else None) or DEFAULT_PROFILE
        profile = profiles.get(pid) or profiles.get(DEFAULT_PROFILE) or {
            "id": DEFAULT_PROFILE, "label": "Classique", "plugins": [], "sponsor": None, "ad_groups": [], "jingle_categories": []}
    allowed = SCOPES if role == "admin" else ("user",)
    entries = [by_id[x] for x in profile.get("plugins", []) if x in by_id and by_id[x].get("scope") in allowed]
    if role == "admin":
        listed = {p["id"] for p in entries}
        entries += [p for p in plugins if p.get("scope") == "admin" and p.get("id") not in listed]
    out = {"role": role, "user": user, "profile": profile, "plugins": entries, "view_as": view_as}
    if role == "admin":
        out["profiles"] = [{"id": p["id"], "label": p["label"]} for p in profiles.values()]
    return out
