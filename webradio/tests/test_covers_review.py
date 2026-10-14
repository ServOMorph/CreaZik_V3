import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import covers_review as cr  # noqa: E402
import cover_review_watch as watch  # noqa: E402


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(cr, "HERE", tmp_path)
    out = tmp_path / "playlists" / "p" / "outputs"
    out.mkdir(parents=True)
    tracks = {}
    for i in (2, 10, 1):
        (out / f"0{i}_t.mp3").write_bytes(b"x")
        (out / f"0{i}_t.cover.png").write_bytes(b"png")
        tracks[f"p:{i}"] = {"file": f"playlists/p/outputs/0{i}_t.mp3", "name": f"Titre {i}", "playlist": "p",
                            "playlist_label": "Playlist P", "jingle": False}
    tracks["p:3"] = {"file": "playlists/p/outputs/03_t.mp3", "name": "Sans pochette", "playlist": "p",
                     "playlist_label": "Playlist P", "jingle": False}
    tracks["j:1"] = {"file": "playlists/p/outputs/01_t.mp3", "name": "Jingle", "playlist": "j",
                     "playlist_label": "J", "jingle": True}
    return tmp_path, tracks, tmp_path / "state.json"


def test_list_review_ordre_et_filtre(env):
    _, tracks, state = env
    d = cr.list_review(tracks, state)
    assert [i["key"] for i in d["items"]] == ["p:1", "p:2", "p:10"]
    assert d["total"] == 3 and d["counts"]["pending"] == 3
    assert all("?v=" in i["url"] and i["url"].startswith("/playlists/p/outputs/") for i in d["items"])


def test_verdict_valide_et_refait(env):
    _, tracks, state = env
    assert cr.apply_verdict("p:1", "validated", tracks, state) == "validated"
    assert cr.apply_verdict("p:2", "redo", tracks, state) == "redo"
    d = cr.list_review(tracks, state)
    assert d["counts"]["validated"] == 1 and d["counts"]["redo"] == 1 and d["counts"]["pending"] == 1


def test_verdict_refuse_cle_inconnue_jingle_ou_verdict_invalide(env):
    _, tracks, state = env
    assert cr.apply_verdict("zz:1", "redo", tracks, state) is None
    assert cr.apply_verdict("j:1", "redo", tracks, state) is None
    assert cr.apply_verdict("p:1", "supprimer", tracks, state) is None


def test_plafond_de_regenerations(env):
    _, tracks, state = env
    cr.update_item("p:1", {"redo_count": cr.MAX_REDO}, state)
    assert cr.apply_verdict("p:1", "redo", tracks, state) == "abandoned"


def test_regeneration_remet_en_attente_de_validation(env):
    tmp, tracks, state = env
    target = tmp / "playlists" / "p" / "outputs" / "01_t.cover.png"
    jobs = {"p:1": {"title": "Titre 1", "style": "s", "target": target}}
    cr.apply_verdict("p:1", "redo", tracks, state)
    seen = []

    def fake(job, seed, temp):
        seen.append(seed)
        temp.write_bytes(b"nouveau")
        return True

    assert watch.pending_redos(state) == ["p:1"]
    assert watch.process_key("p:1", jobs, state, fake) == "regenerated"
    item = cr.read_state(state)["items"]["p:1"]
    assert item["status"] == "pending" and item["redo_count"] == 1 and item["seeds"] == seen
    assert target.read_bytes() == b"nouveau"
    assert watch.pending_redos(state) == []
    cr.apply_verdict("p:1", "redo", tracks, state)
    watch.process_key("p:1", jobs, state, fake)
    assert len(set(seen)) == 2


def test_echecs_repetes_puis_erreur(env):
    tmp, tracks, state = env
    target = tmp / "playlists" / "p" / "outputs" / "01_t.cover.png"
    jobs = {"p:1": {"title": "Titre 1", "style": "s", "target": target}}
    cr.apply_verdict("p:1", "redo", tracks, state)
    results = [watch.process_key("p:1", jobs, state, lambda j, s, t: False) for _ in range(cr.MAX_FAILS)]
    assert results[-1] == "error" and results[0] == "failed"
    assert target.read_bytes() == b"png"
    assert watch.pending_redos(state) == []


def test_playlist_exclue_marque_abandon(env):
    _, tracks, state = env
    cr.apply_verdict("p:2", "redo", tracks, state)
    assert watch.process_key("p:2", {}, state, lambda j, s, t: True) == "abandoned"
    assert cr.read_state(state)["items"]["p:2"]["status"] == "abandoned"


def test_verrou_exclusif(env):
    _, _, state = env
    with cr.state_lock(state):
        with pytest.raises(TimeoutError):
            with cr.state_lock(state, timeout=0.2):
                pass
    with cr.state_lock(state, timeout=0.2):
        pass
