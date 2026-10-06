import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Paris")

SCHEMA = """
CREATE TABLE IF NOT EXISTS plays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    ts_iso TEXT NOT NULL,
    key TEXT NOT NULL,
    playlist_id TEXT NOT NULL,
    song TEXT,
    name TEXT,
    duration_s REAL,
    hour INTEGER,
    weekday INTEGER,
    energy REAL,
    bpm REAL,
    explicit INTEGER NOT NULL DEFAULT 0,
    forced INTEGER NOT NULL DEFAULT 0,
    listened_s REAL,
    skipped INTEGER
);
CREATE INDEX IF NOT EXISTS idx_plays_key ON plays(key);
CREATE INDEX IF NOT EXISTS idx_plays_ts ON plays(ts);
CREATE TABLE IF NOT EXISTS neutral (
    voter TEXT NOT NULL,
    key TEXT NOT NULL,
    ts REAL NOT NULL,
    PRIMARY KEY (voter, key)
);
CREATE INDEX IF NOT EXISTS idx_neutral_key ON neutral(key);
CREATE TABLE IF NOT EXISTS dynamics (
    voter TEXT NOT NULL,
    key TEXT NOT NULL,
    level TEXT NOT NULL,
    ts REAL NOT NULL,
    PRIMARY KEY (voter, key)
);
CREATE INDEX IF NOT EXISTS idx_dynamics_key ON dynamics(key);
CREATE TABLE IF NOT EXISTS vote_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    voter TEXT NOT NULL,
    key TEXT NOT NULL,
    kind TEXT NOT NULL,
    count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    name TEXT PRIMARY KEY,
    value TEXT
);
"""

DICTIONARY = {
    "plays": "Nombre de diffusions du morceau depuis le début de l'enregistrement (db_since).",
    "distinct_tracks": "Nombre de morceaux différents diffusés.",
    "last_played": "Date de la dernière diffusion (heure de Paris).",
    "up": "Total des pouces haut (votes.json, tous auditeurs, y compris avant db_since).",
    "down": "Total des pouces bas (votes.json).",
    "score": "up moins down.",
    "neutral": "Nombre d'auditeurs ayant marqué le morceau comme écouté sans avis.",
    "skipped": "Diffusions interrompues avant la fin par un passage forcé (suivant, lire maintenant).",
    "skip_rate": "skipped divisé par les diffusions dont la fin est connue, entre 0 et 1.",
    "avg_listen_ratio": "Part moyenne du morceau réellement diffusée avant le suivant, entre 0 et 1.",
    "share_expected_pct": "Part de diffusion attendue d'après les pondérations et les pouces (en %).",
    "share_actual_pct": "Part de diffusion observée sur la période enregistrée (en %).",
    "share_gap_pct": "share_actual_pct moins share_expected_pct, en points de pourcentage.",
    "weight": "Pondération de la playlist (0 à 10).",
    "status": "Évaluation : positif (score > 0), negatif (score < 0), sans_avis (marqué sans avis), non_evalue (diffusé sans aucune réaction), jamais_diffuse.",
    "dyn_slow": "Nombre d'auditeurs dont le choix inclut la dynamique lente (un choix à deux boutons compte dans chacun des deux niveaux).",
    "dyn_medium": "Nombre d'auditeurs ayant classé le morceau en dynamique moyenne.",
    "dyn_high": "Nombre d'auditeurs ayant classé le morceau en dynamique forte.",
    "dyn_user": "Dynamique moyenne perçue par les auditeurs, entre 0 (lente) et 1 (forte) ; deux boutons choisis valent la moyenne de leurs niveaux (ex. slow+medium = 0,325) ; comparable à energy.",
    "hour": "Heure de Paris (0 à 23) du début de diffusion.",
    "weekday": "Jour de la semaine, 0 = lundi.",
}


DYN_LEVELS = {"slow": 0.15, "medium": 0.5, "high": 0.85}


DYN_ORDER = ("slow", "medium", "high")


def parse_level(text):
    parts = str(text).split("+")
    if not 1 <= len(parts) <= 2 or len(set(parts)) != len(parts) or any(p not in DYN_LEVELS for p in parts):
        return None
    return tuple(sorted(parts, key=DYN_ORDER.index))


def level_value(text):
    parts = parse_level(text)
    return sum(DYN_LEVELS[p] for p in parts) / len(parts) if parts else None


def dynamics_mean(counts):
    n = sum(counts.values()) if counts else 0
    if not n:
        return None, 0
    return sum(level_value(k) * v for k, v in counts.items()) / n, n


class StatsDB:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.Lock()
        c = self._conn()
        try:
            with c:
                c.executescript(SCHEMA)
                c.execute("INSERT OR IGNORE INTO meta(name, value) VALUES ('since', ?)", (str(time.time()),))
        finally:
            c.close()

    def _conn(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    def _run(self, sql, params=()):
        with self.lock:
            c = self._conn()
            try:
                with c:
                    cur = c.execute(sql, params)
                    return cur.lastrowid
            finally:
                c.close()

    def _all(self, sql, params=()):
        with self.lock:
            c = self._conn()
            try:
                return [dict(r) for r in c.execute(sql, params).fetchall()]
            finally:
                c.close()

    def log_play(self, t, track, explicit, forced):
        dt = datetime.fromtimestamp(t, LOCAL_TZ)
        return self._run(
            "INSERT INTO plays(ts, ts_iso, key, playlist_id, song, name, duration_s, hour, weekday, energy, bpm, explicit, forced)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (t, dt.isoformat(timespec="seconds"), track["key"], track["playlist"], track.get("song"), track.get("name"),
             track.get("duration"), dt.hour, dt.weekday(), track.get("energy"), track.get("bpm"),
             1 if explicit else 0, 1 if forced else 0))

    def finish_play(self, play_id, listened_s, skipped):
        if not play_id:
            return
        self._run("UPDATE plays SET listened_s = ?, skipped = ? WHERE id = ?",
                  (round(max(0.0, listened_s), 2), 1 if skipped else 0, play_id))

    def set_neutral(self, voter, key, on):
        if on:
            self._run("INSERT OR REPLACE INTO neutral(voter, key, ts) VALUES (?,?,?)", (voter, key, time.time()))
        else:
            self._run("DELETE FROM neutral WHERE voter = ? AND key = ?", (voter, key))

    def clear_neutral(self, voter, key):
        self._run("DELETE FROM neutral WHERE voter = ? AND key = ?", (voter, key))

    def clear_neutral_key(self, key):
        self._run("DELETE FROM neutral WHERE key = ?", (key,))

    def neutral_of(self, voter):
        return [r["key"] for r in self._all("SELECT key FROM neutral WHERE voter = ?", (voter,))]

    def set_dynamics(self, voter, key, level):
        parts = parse_level(level)
        if parts:
            self._run("INSERT OR REPLACE INTO dynamics(voter, key, level, ts) VALUES (?,?,?,?)",
                      (voter, key, "+".join(parts), time.time()))
        else:
            self._run("DELETE FROM dynamics WHERE voter = ? AND key = ?", (voter, key))

    def dynamics_of(self, voter):
        return {r["key"]: r["level"] for r in self._all("SELECT key, level FROM dynamics WHERE voter = ?", (voter,))}

    def dynamics_counts(self):
        out = {}
        for r in self._all("SELECT key, level, COUNT(*) AS n FROM dynamics GROUP BY key, level"):
            out.setdefault(r["key"], {})[r["level"]] = r["n"]
        return out

    def clear_dynamics_key(self, key):
        self._run("DELETE FROM dynamics WHERE key = ?", (key,))

    def log_vote(self, voter, key, kind, count):
        self._run("INSERT INTO vote_events(ts, voter, key, kind, count) VALUES (?,?,?,?,?)",
                  (time.time(), voter, key, kind, count))

    def plays(self):
        return self._all("SELECT id, ts, ts_iso, key, playlist_id, duration_s, hour, weekday, energy, explicit, forced,"
                         " listened_s, skipped FROM plays")

    def neutral_counts(self):
        return {r["key"]: r["n"] for r in self._all("SELECT key, COUNT(*) AS n FROM neutral GROUP BY key")}

    def since(self):
        rows = self._all("SELECT value FROM meta WHERE name = 'since'")
        return float(rows[0]["value"]) if rows else time.time()


def _dyn_votes(counts, level):
    return sum(n for k, n in (counts or {}).items() if level in k.split("+"))


def _round(v):
    return None if v is None else round(v, 3)


def _rate(num, den):
    return round(num / den, 3) if den else None


def build_analytics(plays, neutral_counts, votes, tracks, playlists, expected, weights, since, now, dyn_counts=None):
    dyn_counts = dyn_counts or {}
    cat_keys = {k for k, t in tracks.items() if not t["jingle"]}
    by_key = {}
    for p in plays:
        by_key.setdefault(p["key"], []).append(p)

    def agg(rows):
        done = [r for r in rows if r["skipped"] is not None]
        ratios = [min(1.0, r["listened_s"] / r["duration_s"]) for r in rows
                  if r["listened_s"] is not None and r["duration_s"]]
        return {
            "plays": len(rows),
            "skipped": sum(1 for r in done if r["skipped"]),
            "skip_rate": _rate(sum(1 for r in done if r["skipped"]), len(done)),
            "avg_listen_ratio": round(sum(ratios) / len(ratios), 3) if ratios else None,
            "last_played": max((r["ts_iso"] for r in rows), default=None),
        }

    track_rows = []
    for k in sorted(cat_keys):
        tr = tracks[k]
        v = votes.get(k) or {}
        up, down = int(v.get("up", 0)), int(v.get("down", 0))
        a = agg(by_key.get(k, []))
        neu = neutral_counts.get(k, 0)
        if a["plays"] == 0:
            status = "jamais_diffuse"
        elif up - down > 0:
            status = "positif"
        elif up - down < 0:
            status = "negatif"
        elif neu > 0:
            status = "sans_avis"
        elif up or down:
            status = "equilibre"
        else:
            status = "non_evalue"
        track_rows.append({
            "key": k, "name": str(tr.get("name", k)), "playlist_id": tr["playlist"], "playlist": tr["playlist_label"],
            "duration_s": round(tr["duration"], 1), "energy": tr.get("energy"), "bpm": tr.get("bpm"),
            **a, "up": up, "down": down, "score": up - down, "neutral": neu, "status": status,
            "dyn_slow": _dyn_votes(dyn_counts.get(k), "slow"), "dyn_medium": _dyn_votes(dyn_counts.get(k), "medium"),
            "dyn_high": _dyn_votes(dyn_counts.get(k), "high"), "dyn_user": _round(dynamics_mean(dyn_counts.get(k))[0]),
        })

    total_plays = sum(1 for p in plays if p["key"] in cat_keys)
    pl_rows = []
    for pl in playlists:
        if pl["jingle"]:
            continue
        rows = [r for r in track_rows if r["playlist_id"] == pl["id"]]
        pl_plays = [p for p in plays if p["playlist_id"] == pl["id"]]
        a = agg(pl_plays)
        exp = expected.get(pl["id"])
        actual = round(len(pl_plays) / total_plays * 100, 2) if total_plays else None
        pl_rows.append({
            "id": pl["id"], "label": pl["label"], "weight": weights.get(pl["id"]), "tracks_total": len(rows),
            "distinct_tracks": sum(1 for r in rows if r["plays"] > 0), **a,
            "up": sum(r["up"] for r in rows), "down": sum(r["down"] for r in rows),
            "score": sum(r["score"] for r in rows), "neutral": sum(r["neutral"] for r in rows),
            "share_expected_pct": exp, "share_actual_pct": actual,
            "share_gap_pct": round(actual - exp, 2) if actual is not None and exp is not None else None,
        })

    hours = []
    for h in range(24):
        rows = [p for p in plays if p["hour"] == h and p["key"] in cat_keys]
        en = [p["energy"] for p in rows if p["energy"] is not None]
        a = agg(rows)
        hours.append({"hour": h, "plays": a["plays"], "skip_rate": a["skip_rate"],
                      "avg_energy": round(sum(en) / len(en), 3) if en else None})
    weekdays = []
    for d in range(7):
        rows = [p for p in plays if p["weekday"] == d and p["key"] in cat_keys]
        weekdays.append({"weekday": d, "plays": len(rows)})

    day = 86400
    kpis = {
        "total_plays": total_plays,
        "plays_24h": sum(1 for p in plays if p["key"] in cat_keys and now - p["ts"] <= day),
        "plays_7d": sum(1 for p in plays if p["key"] in cat_keys and now - p["ts"] <= 7 * day),
        "catalogue_tracks": len(cat_keys),
        "distinct_tracks_played": sum(1 for r in track_rows if r["plays"] > 0),
        "never_played": sum(1 for r in track_rows if r["plays"] == 0),
        "coverage_pct": round(sum(1 for r in track_rows if r["plays"] > 0) / len(cat_keys) * 100, 1) if cat_keys else None,
        "skip_rate": agg([p for p in plays if p["key"] in cat_keys])["skip_rate"],
        "avg_listen_ratio": agg([p for p in plays if p["key"] in cat_keys])["avg_listen_ratio"],
        "total_up": sum(r["up"] for r in track_rows),
        "total_down": sum(r["down"] for r in track_rows),
        "neutral_marks": sum(r["neutral"] for r in track_rows),
        "played_without_opinion": sum(1 for r in track_rows if r["status"] == "non_evalue"),
    }

    insights = []
    if total_plays < 30:
        insights.append({"level": "info", "text": f"Échantillon faible : {total_plays} diffusions enregistrées, les taux et écarts ne sont pas fiables avant une trentaine."})
    if kpis["never_played"]:
        insights.append({"level": "info", "text": f"{kpis['never_played']} morceau(x) sur {kpis['catalogue_tracks']} jamais diffusé(s) depuis le début de l'enregistrement."})
    if kpis["played_without_opinion"]:
        insights.append({"level": "info", "text": f"{kpis['played_without_opinion']} morceau(x) diffusé(s) sans aucune réaction (ni pouce, ni marque « sans avis »)."})
    skipped = sorted((r for r in track_rows if r["plays"] >= 2 and (r["skip_rate"] or 0) >= 0.5),
                     key=lambda r: (-(r["skip_rate"] or 0), -r["plays"]))[:5]
    if skipped:
        insights.append({"level": "warn", "text": "Souvent sautés (au moins 2 diffusions, 50 % ou plus de passages forcés) : "
                         + ", ".join(f"{r['name']} ({r['playlist']})" for r in skipped) + "."})
    if total_plays >= 30:
        over = [p for p in pl_rows if p["share_gap_pct"] is not None and p["share_expected_pct"]
                and p["share_actual_pct"] >= 1.5 * p["share_expected_pct"] and p["share_gap_pct"] >= 1]
        under = [p for p in pl_rows if p["share_gap_pct"] is not None and p["share_expected_pct"]
                 and p["share_actual_pct"] <= 0.5 * p["share_expected_pct"] and p["share_gap_pct"] <= -1]
        if over:
            insights.append({"level": "warn", "text": "Playlists diffusées nettement plus que prévu : " + ", ".join(
                f"{p['label']} ({p['share_actual_pct']} % pour {p['share_expected_pct']} % attendus)" for p in over[:5]) + "."})
        if under:
            insights.append({"level": "warn", "text": "Playlists diffusées nettement moins que prévu : " + ", ".join(
                f"{p['label']} ({p['share_actual_pct']} % pour {p['share_expected_pct']} % attendus)" for p in under[:5]) + "."})
    neg_played = [r for r in track_rows if r["score"] < 0 and r["plays"] > 0]
    if neg_played:
        insights.append({"level": "warn", "text": f"{len(neg_played)} morceau(x) à score négatif encore diffusé(s) ; le plus bas : "
                         + min(neg_played, key=lambda r: r["score"])["name"] + "."})

    return {
        "generated_at": datetime.fromtimestamp(now, LOCAL_TZ).isoformat(timespec="seconds"),
        "db_since": datetime.fromtimestamp(since, LOCAL_TZ).isoformat(timespec="seconds"),
        "kpis": kpis, "insights": insights, "by_playlist": pl_rows, "by_track": track_rows,
        "by_hour": hours, "by_weekday": weekdays, "dictionary": DICTIONARY,
    }
