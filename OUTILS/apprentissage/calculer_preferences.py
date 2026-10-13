"""Calcule les preferences de generation a partir des seuls votes radio.

Ecrit DOCUMENTATION/apprentissage/preferences.proposition.json. Ne touche jamais preferences.json.
Sources : webradio/votes.json, config.json des playlists, learning/morceaux_rejetes.jsonl, .feat.json.
Exclus : avis Slow/Medium/High, pouces et commentaires des Tests.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
EFFECTIF_MINIMUM = 5
MODELE_DEFAUT = "ace-step-1.5-turbo"

FAMILLES = {
    "folk": ["folk", "acoustic", "chanson", "ballad"],
    "rock": ["rock", "punk", "grunge", "hard rock"],
    "metal": ["metal"],
    "electro": ["electro", "synth", "techno", "house", "edm", "dance", "trance"],
    "hip-hop": ["rap", "hip hop", "hip-hop", "trap"],
    "jazz-blues": ["jazz", "blues", "swing"],
    "classique-sacre": ["classical", "orchestral", "gregorian", "chant", "baroque", "symphon", "opera"],
    "choeur": ["choir", "choral", "chorale", "a cappella", "acappella"],
    "funk-soul": ["funk", "soul", "groove", "r&b"],
    "latin-monde": ["latin", "bossa", "salsa", "bachata", "afro", "reggae", "samba", "tropical", "world"],
    "pop": ["pop"],
    "ambient": ["ambient", "drone", "atmospheric", "cinematic"],
}


def modele_de(nom):
    if not nom:
        return MODELE_DEFAUT
    n = nom.lower()
    if "ace" in n:
        return MODELE_DEFAUT
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")


def voix_de(rec):
    p = (rec.get("prompt") or "").lower()
    if rec.get("type") == "instrumental":
        return "instrumental"
    if re.search(r"\bfemale|woman|women|soprano|femme", p):
        return "female"
    if re.search(r"\bmale\b|\bman\b|baritone|tenor|bass voice", p):
        return "male"
    if re.search(r"choir|choral|chorus|a cappella", p):
        return "choeur"
    return "non_precise"


def familles_de(prompt):
    p = (prompt or "").lower()
    return [f for f, mots in FAMILLES.items() if any(m in p for m in mots)]


def termes_de(prompt):
    return {t.strip().lower() for t in (prompt or "").split(",") if 2 < len(t.strip()) < 60}


def charger_enregistrements(racine):
    web = racine / "webradio"
    recs = {}
    corpus = web / "learning" / "morceaux_rejetes.jsonl"
    if corpus.exists():
        for ligne in corpus.read_text(encoding="utf-8").splitlines():
            if ligne.strip():
                r = json.loads(ligne)
                bpm = (r.get("features") or {}).get("bpm")
                recs[r["key"]] = {
                    "prompt": r.get("prompt"), "type": r.get("type"), "duree": r.get("duration_s") or r.get("requested_duration_s"),
                    "bpm": bpm, "modele": modele_de(r.get("model")),
                }
    return recs


def completer_depuis_playlists(recs, cles, racine):
    web = racine / "webradio"
    for cle in cles:
        if cle in recs:
            continue
        pid, cid = cle.rsplit(":", 1)
        cfg = web / "playlists" / pid / "config.json"
        if not cfg.exists():
            continue
        data = json.loads(cfg.read_text(encoding="utf-8"))
        tc = next((t for t in data.get("test_cases", []) if str(t.get("id")) == cid), None)
        if not tc:
            continue
        bpm = None
        for f in (web / "playlists" / pid / "outputs").glob(f"{int(cid):02d}_*.feat.json"):
            bpm = json.loads(f.read_text(encoding="utf-8")).get("bpm")
            break
        recs[cle] = {"prompt": tc.get("prompt"), "type": tc.get("type"), "duree": tc.get("duration"), "bpm": bpm, "modele": MODELE_DEFAUT}


def intervalle(valeurs):
    if not valeurs:
        return [0, 0]
    v = sorted(valeurs)
    n = len(v)
    return [round(v[int(0.1 * (n - 1))], 1), round(v[int(0.9 * (n - 1) + 0.5)], 1)]


def taux(pour, contre):
    return round(pour / (pour + contre), 3) if pour + contre else 0.0


def calculer(votes, recs, maintenant=None):
    par_modele = defaultdict(lambda: {"termes": defaultdict(lambda: [0, 0]), "familles": defaultdict(lambda: [0, 0]),
                                      "voix": defaultdict(lambda: [0, 0]), "bpm_pour": [], "bpm_contre": [], "duree_pour": []})
    votes_pris = 0
    for cle, v in votes.items():
        score = v.get("score", v.get("up", 0) - v.get("down", 0))
        rec = recs.get(cle)
        if not rec or score == 0:
            continue
        aime = score > 0
        i = 0 if aime else 1
        m = par_modele[rec["modele"]]
        votes_pris += 1
        for t in termes_de(rec["prompt"]):
            m["termes"][t][i] += 1
        for f in familles_de(rec["prompt"]):
            m["familles"][f][i] += 1
        m["voix"][voix_de(rec)][i] += 1
        if rec.get("bpm"):
            m["bpm_pour" if aime else "bpm_contre"].append(rec["bpm"])
        if aime and rec.get("duree"):
            m["duree_pour"].append(rec["duree"])
    modeles = {}
    for nom, m in sorted(par_modele.items()):
        termes = [{"terme": t, "pour": p, "contre": c, "taux": taux(p, c)} for t, (p, c) in m["termes"].items() if p + c >= 3]
        termes.sort(key=lambda x: (-(x["pour"] + x["contre"]), x["terme"]))
        modeles[nom] = {
            "mots_cles_caption": termes[:80],
            "familles_style": sorted(
                ({"famille": f, "pour": p, "contre": c, "taux": taux(p, c)} for f, (p, c) in m["familles"].items()),
                key=lambda x: (-x["taux"], x["famille"])),
            "tempo": {"aime": intervalle(m["bpm_pour"]), "rejete": intervalle(m["bpm_contre"])},
            "duree_s": {"aime": intervalle(m["duree_pour"])},
            "voix": sorted(
                ({"type": t, "pour": p, "contre": c, "taux": taux(p, c)} for t, (p, c) in m["voix"].items()),
                key=lambda x: (-x["taux"], x["type"])),
        }
    return {
        "version": 1,
        "calcule_le": (maintenant or datetime.now().astimezone()).isoformat(timespec="seconds"),
        "sources": {"votes": "webradio/votes.json", "morceaux_votes": votes_pris},
        "modeles": modeles,
        "effectif_minimum": EFFECTIF_MINIMUM,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--racine", default=str(RACINE))
    p.add_argument("--sortie", default=None)
    a = p.parse_args()
    racine = Path(a.racine)
    votes = json.loads((racine / "webradio" / "votes.json").read_text(encoding="utf-8"))["tracks"]
    recs = charger_enregistrements(racine)
    completer_depuis_playlists(recs, votes.keys(), racine)
    res = calculer(votes, recs)
    sortie = Path(a.sortie) if a.sortie else racine / "DOCUMENTATION" / "apprentissage" / "preferences.proposition.json"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{sortie} : {res['sources']['morceaux_votes']} morceaux votes pris en compte (sur {len(votes)})")
    for nom, m in res["modeles"].items():
        print(nom, "familles:", [(f["famille"], f["pour"], f["contre"]) for f in m["familles_style"]][:6])


if __name__ == "__main__":
    main()
