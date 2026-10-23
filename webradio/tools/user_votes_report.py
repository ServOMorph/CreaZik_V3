import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def track_names():
    names = {}
    for pl in read_json(HERE / "playlists.json", []):
        res = read_json(HERE / pl.get("results", ""), {})
        for g in res.get("generations", []):
            names[f"{pl['id']}:{g.get('test_case_id')}"] = g.get("name", "")
    return names


def collect(path):
    per_track = defaultdict(lambda: {"up": 0, "down": 0, "last": ""})
    voters = set()
    for voter, mine in read_json(path, {}).get("voters", {}).items():
        for key, rec in mine.items():
            if rec.get("vote") in ("up", "down"):
                per_track[key][rec["vote"]] += 1
                per_track[key]["last"] = max(per_track[key]["last"], rec.get("t", ""))
                voters.add(voter)
    return per_track, voters


def owner_scores():
    return {k: int(v.get("score", 0)) for k, v in read_json(HERE / "votes.json", {}).get("tracks", {}).items()}


def rows(per_track, min_votes):
    names, owner = track_names(), owner_scores()
    out = []
    for key, v in per_track.items():
        n = v["up"] + v["down"]
        if n < min_votes:
            continue
        score = v["up"] - v["down"]
        own = owner.get(key)
        out.append({"key": key, "name": names.get(key, ""), "up": v["up"], "down": v["down"], "n": n, "score": score,
                    "owner": own, "last": v["last"],
                    "disagree": own is not None and own != 0 and score != 0 and (own > 0) != (score > 0)})
    return sorted(out, key=lambda r: (r["score"], r["n"]))


def by_playlist(items):
    agg = defaultdict(lambda: {"up": 0, "down": 0, "tracks": 0})
    for r in items:
        a = agg[r["key"].split(":")[0]]
        a["up"] += r["up"]
        a["down"] += r["down"]
        a["tracks"] += 1
    settings = read_json(HERE / "radio_settings.json", {})
    weights, default = settings.get("weights") or {}, settings.get("default_weight", 5)
    return [{"playlist": p, "weight": weights.get(p, default), **a, "score": a["up"] - a["down"]}
            for p, a in sorted(agg.items(), key=lambda kv: kv[1]["up"] - kv[1]["down"])]


def render(items, voters, pls):
    lines = [f"Votes des auditeurs : {len(voters)} auditeur(s), {len(items)} morceau(x) retenu(s)", "",
             "Morceaux (du score auditeur le plus bas au plus haut)", "",
             "| Morceau | Titre | Pouces haut | Pouces bas | Score auditeur | Score gestion | Dernier vote | Désaccord |",
             "|---|---|---|---|---|---|---|---|"]
    for r in items:
        own = "" if r["owner"] is None else r["owner"]
        lines.append(f"| {r['key']} | {r['name']} | {r['up']} | {r['down']} | {r['score']} | {own} | {r['last']} | {'oui' if r['disagree'] else ''} |")
    lines += ["", "Playlists", "", "| Playlist | Poids actuel | Morceaux votés | Pouces haut | Pouces bas | Score auditeur |", "|---|---|---|---|---|---|"]
    for p in pls:
        lines.append(f"| {p['playlist']} | {p['weight']} | {p['tracks']} | {p['up']} | {p['down']} | {p['score']} |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rapport des votes de l'interface auditeur (lecture seule)")
    ap.add_argument("--min-votes", type=int, default=1, help="nombre minimal de votes par morceau")
    ap.add_argument("--fichier", default=str(HERE / "user_votes.json"))
    a = ap.parse_args(argv)
    per_track, voters = collect(a.fichier)
    items = rows(per_track, a.min_votes)
    sys.stdout.reconfigure(encoding="utf-8")
    print(render(items, voters, by_playlist(items)))


if __name__ == "__main__":
    main()
