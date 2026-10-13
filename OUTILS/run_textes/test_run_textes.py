import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import run_textes as r


def monter(tmp_path, n_textes=2):
    d = tmp_path / "DOCUMENTATION" / "apprentissage"
    d.mkdir(parents=True)
    (tmp_path / "webradio" / "playlists" / "tests-ace" / "outputs").mkdir(parents=True)
    (tmp_path / "webradio" / "playlists" / "tests-ace" / "outputs" / "playlist_results.json").write_text(
        json.dumps({"generations": [{"name": "55 · ancien"}]}), encoding="utf-8")
    (tmp_path / "paroles.md").write_text("[verse]\nUne ligne\n", encoding="utf-8")
    regles = {"graines_de_reprise": [2026, 31415, 42], "modeles": {"ace-step-1.5-turbo": {"duree_max_s": 150}}}
    plan = {"textes": [{"id": f"t{i}", "titre": f"Texte {i}", "source": f"TEXTES/x/t{i}.md", "versions": [
        {"id": "A", "label": "folk", "caption": "folk, acoustic", "duree_s": 200, "paroles": "paroles.md", "graine": 7}]}
        for i in range(n_textes)]}
    (d / "regles_modeles.json").write_text(json.dumps(regles), encoding="utf-8")
    (d / "plan_run.json").write_text(json.dumps(plan), encoding="utf-8")
    return d


def lancer(tmp_path, *extra):
    sys.argv = ["run_textes", "--racine", str(tmp_path), "--simulation", *extra]
    r.main()


def test_simulation_deux_textes(tmp_path):
    d = monter(tmp_path)
    lancer(tmp_path)
    etat = json.loads((d / "run_state.json").read_text(encoding="utf-8"))
    assert [v["statut"] for v in etat["versions"].values()] == ["TERMINE", "TERMINE"]
    res = json.loads((tmp_path / "webradio/playlists/tests-ace/outputs/playlist_results.json").read_text(encoding="utf-8"))
    nouveaux = res["generations"][1:]
    assert [g["name"][:2] for g in nouveaux] == ["56", "57"]
    assert all(g["folder"] == "Funky Yogi" and g["seed"] == 7 and g["duration"] <= 150 for g in nouveaux)
    for g in nouveaux:
        assert (tmp_path / "webradio" / g["output_file"]).is_file()


def test_reprise_ne_regenere_pas(tmp_path):
    monter(tmp_path)
    lancer(tmp_path)
    lancer(tmp_path)
    res = json.loads((tmp_path / "webradio/playlists/tests-ace/outputs/playlist_results.json").read_text(encoding="utf-8"))
    assert len(res["generations"]) == 3


def test_echec_change_de_graine_puis_echec_documente(tmp_path, monkeypatch):
    d = monter(tmp_path, 1)
    monkeypatch.setattr(r, "generer_simulation", lambda *a: "erreur simulee")
    lancer(tmp_path)
    etat = json.loads((d / "run_state.json").read_text(encoding="utf-8"))["versions"]["t0_A"]
    assert etat["statut"] == "ECHEC" and etat["cause"] == "erreur simulee"
    assert [t["graine"] for t in etat["tentatives"]] == [7, 2026, 31415]


def test_echec_puis_succes_avec_nouvelle_graine(tmp_path, monkeypatch):
    d = monter(tmp_path, 1)
    vrai = r.generer_simulation
    appels = []

    def capricieux(racine, config_rel, delai):
        appels.append(1)
        return "boom" if len(appels) == 1 else vrai(racine, config_rel, delai)

    monkeypatch.setattr(r, "generer_simulation", capricieux)
    lancer(tmp_path)
    etat = json.loads((d / "run_state.json").read_text(encoding="utf-8"))["versions"]["t0_A"]
    assert etat["statut"] == "TERMINE" and etat["graine"] == 2026


def test_simulation_refusee_sur_racine_reelle():
    sys.argv = ["run_textes", "--simulation"]
    with pytest.raises(SystemExit):
        r.main()


def test_ecriture_hors_zone_refusee(tmp_path):
    with pytest.raises(r.Arret):
        r.verifier_ecriture(tmp_path, tmp_path / "webradio" / "playlists" / "perso" / "x.json")


def test_publication_retire_le_test_a_faire(tmp_path):
    monter(tmp_path, 1)
    chemin = tmp_path / "webradio/playlists/tests-ace/outputs/playlist_results.json"
    data = json.loads(chemin.read_text(encoding="utf-8"))
    data["generations"].append({"name": "A faire", "status": "planned", "plan_id": "t0_A"})
    chemin.write_text(json.dumps(data), encoding="utf-8")
    lancer(tmp_path)
    res = json.loads(chemin.read_text(encoding="utf-8"))["generations"]
    assert not [g for g in res if g.get("status") == "planned"]
    assert len(res) == 2
