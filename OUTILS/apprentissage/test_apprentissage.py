import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import calculer_preferences as c
import diff_preferences as d

DIFF = str(Path(__file__).parent / "diff_preferences.py")


def jeu():
    recs, votes = {}, {}
    for i in range(6):
        recs[f"a:{i}"] = {"prompt": "acoustic folk, warm, female vocals", "type": "vocal", "duree": 100, "bpm": 90, "modele": c.MODELE_DEFAUT}
        votes[f"a:{i}"] = {"up": 1, "down": 0, "score": 1}
    for i in range(4):
        recs[f"b:{i}"] = {"prompt": "heavy metal, aggressive", "type": "vocal", "duree": 200, "bpm": 180, "modele": c.MODELE_DEFAUT}
        votes[f"b:{i}"] = {"up": 0, "down": 1, "score": -1}
    recs["n:1"] = {"prompt": "folk", "type": "vocal", "duree": 100, "bpm": 90, "modele": c.MODELE_DEFAUT}
    votes["n:1"] = {"up": 0, "down": 0, "score": 0}
    return votes, recs


def test_calcul_connu():
    votes, recs = jeu()
    res = c.calculer(votes, recs)
    assert res["sources"]["morceaux_votes"] == 10
    m = res["modeles"][c.MODELE_DEFAUT]
    fam = {f["famille"]: f for f in m["familles_style"]}
    assert (fam["folk"]["pour"], fam["folk"]["contre"], fam["folk"]["taux"]) == (6, 0, 1.0)
    assert (fam["metal"]["pour"], fam["metal"]["contre"]) == (0, 4)
    assert m["tempo"]["aime"] == [90, 90] and m["tempo"]["rejete"] == [180, 180]
    assert m["duree_s"]["aime"] == [100, 100]
    voix = {v["type"]: v for v in m["voix"]}
    assert voix["female"]["pour"] == 6


def test_diff_vide_si_rien_ne_change():
    votes, recs = jeu()
    a = c.calculer(votes, recs)
    b = c.calculer(votes, recs)
    assert d.differences(a, b) == []


def test_diff_detecte_changement():
    votes, recs = jeu()
    a = c.calculer(votes, recs)
    votes["a:0"] = {"up": 0, "down": 1, "score": -1}
    b = c.calculer(votes, recs)
    assert d.differences(a, b)


def test_appliquer_refuse_sans_proposition(tmp_path):
    r = subprocess.run([sys.executable, DIFF, "--racine", str(tmp_path), "--appliquer"], capture_output=True, text=True)
    assert r.returncode == 1
    assert not (tmp_path / "DOCUMENTATION" / "apprentissage" / "preferences.json").exists()


def test_appliquer_archive_ancienne_version(tmp_path):
    dossier = tmp_path / "DOCUMENTATION" / "apprentissage"
    dossier.mkdir(parents=True)
    votes, recs = jeu()
    (dossier / "preferences.json").write_text(json.dumps(c.calculer(votes, recs)), encoding="utf-8")
    votes["a:0"] = {"up": 0, "down": 1, "score": -1}
    (dossier / "preferences.proposition.json").write_text(json.dumps(c.calculer(votes, recs)), encoding="utf-8")
    r = subprocess.run([sys.executable, DIFF, "--racine", str(tmp_path), "--appliquer"], capture_output=True, text=True)
    assert r.returncode == 0
    assert len(list((dossier / "historique").glob("preferences_*.json"))) == 1
    assert json.loads((dossier / "preferences.json").read_text(encoding="utf-8")) == json.loads(
        (dossier / "preferences.proposition.json").read_text(encoding="utf-8"))


def test_fusion_archive_et_courant():
    archive = {"a:1": {"up": 2, "down": 1}, "b:1": {"up": 0, "down": 3}}
    courant = {"a:1": {"up": 1, "down": 0, "score": 1}, "c:1": {"up": 1, "down": 0}}
    f = c.fusionner_votes(archive, courant)
    assert f["a:1"] == {"up": 3, "down": 1, "score": 2}
    assert f["b:1"]["score"] == -3
    assert f["c:1"]["score"] == 1


def test_archive_absente_ou_vide(tmp_path):
    assert c.charger_archives(tmp_path / "inexistant") == []
    assert c.charger_archives(tmp_path) == []
    assert c.fusionner_votes({}, {}) == {}


def test_main_avec_et_sans_archive(tmp_path):
    (tmp_path / "webradio").mkdir()
    (tmp_path / "webradio" / "votes.json").write_text(json.dumps({"tracks": {}, "voters": {}}), encoding="utf-8")
    arch = tmp_path / "DOCUMENTATION" / "apprentissage" / "votes_archive"
    arch.mkdir(parents=True)
    (arch / "v.json").write_text(json.dumps({"tracks": {"x:1": {"up": 1, "down": 0, "score": 1}}}), encoding="utf-8")
    votes = json.loads((tmp_path / "webradio" / "votes.json").read_text(encoding="utf-8"))["tracks"]
    avec = c.fusionner_votes(*c.charger_archives(arch), votes)
    assert list(avec) == ["x:1"]
    assert votes == {}
