import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import user_songs  # noqa: E402

LYRICS = "[verse]\nJe marche au bord du canal\nLa ville dort sous la pluie\n\n[chorus]\nDanse avec moi ce soir\nLa nuit nous appartient\n"


def fake_lyrics(job):
    return {"title": "Pluie du soir", "caption": "funk, female vocal, slap bass, rhythm guitar, warm, joyful", "bpm": 110,
            "lyrics": LYRICS, "artists_cited": [], "attempts": [{"attempt": 1}], "check": {"warnings": []}}


def make(tmp_path, lyrics=None, music=None, finalize=None, busy=None, schedule=None, lock=None):
    return user_songs.SongQueue(tmp_path, schedule=schedule or (lambda key: True), music_busy=busy or (lambda: False),
                                gpu_lock=lock, lyrics=lyrics or fake_lyrics,
                                music=music or (lambda job: {"output_file": "x.wav", "metadata_file": "x.metadata.json", "elapsed_s": 1}),
                                finalize=finalize or (lambda job, entry: ("creations-auditeurs:1", 92.0)),
                                prepare=lambda: None, before_music=lambda: None)


def test_ready_and_scheduled(tmp_path):
    scheduled = []
    q = make(tmp_path, schedule=lambda key: scheduled.append(key) or True)
    a = q.submit("un funk joyeux")
    b = q.submit("une valse")
    assert q.status(a)["position"] == 1 and q.status(b)["position"] == 2
    q.run_once()
    st = q.status(a)
    assert st["status"] == "ready" and st["key"] == "creations-auditeurs:1" and st["scheduled"] and st["title"] == "Pluie du soir"
    assert scheduled == ["creations-auditeurs:1"]
    trace = json.loads((tmp_path / f"{a}.json").read_text(encoding="utf-8"))
    assert trace["prompt"] == "un funk joyeux" and isinstance(trace["seed"], int) and trace["seed"] >= 0
    assert 45 <= trace["duration"] <= 135 and trace["lyrics"] == LYRICS
    assert {"lyrics_s", "music_s", "finalize_s", "total_s"} <= set(trace["timings"])
    assert q.status(b)["position"] == 1


def test_stage_visible_while_running(tmp_path):
    stages = []

    def music(job):
        stages.append(q.status(job["id"])["stage"])
        return {"output_file": "x.wav"}

    q = make(tmp_path, music=music)
    q.submit("x")
    q.run_once()
    assert stages == ["music"]


def test_error_then_queue_continues(tmp_path):
    def music(job):
        if job["prompt"] == "bad":
            raise user_songs.SongError("timeout", "trop long")
        return {"output_file": "x.wav"}

    q = make(tmp_path, music=music)
    a = q.submit("bad")
    b = q.submit("good")
    q.run_once()
    q.run_once()
    st = q.status(a)
    assert st["status"] == "error" and "trop de temps" in st["error"]
    assert q.status(b)["status"] == "ready"


def test_lyrics_error_is_readable(tmp_path):
    def lyrics(job):
        raise user_songs.SongError("lyrics", "refus")

    q = make(tmp_path, lyrics=lyrics)
    a = q.submit("x")
    q.run_once()
    assert q.status(a)["status"] == "error" and "paroles" in q.status(a)["error"]


def test_unknown_or_invalid_id(tmp_path):
    q = make(tmp_path)
    assert q.status("0" * 32) is None
    assert q.status("../x") is None


def test_waits_for_rotation(tmp_path, monkeypatch):
    monkeypatch.setattr(user_songs, "MUSIC_POLL_S", 0)
    q = make(tmp_path, busy=lambda: True)
    a = q.submit("x")
    q.run_once()
    st = q.status(a)
    assert st["status"] == "queued" and st["waiting_music"]


def test_gpu_lock_covers_whole_job(tmp_path):
    lock = threading.Lock()
    seen = []

    def busy():
        seen.append(lock.locked())
        return False

    def music(job):
        seen.append(lock.locked())
        return {"output_file": "x.wav"}

    q = make(tmp_path, busy=busy, music=music, lock=lock)
    q.submit("x")
    q.run_once()
    assert seen == [True, True] and not lock.locked()


def test_save_failure_ends_in_error(tmp_path, monkeypatch):
    q = make(tmp_path)
    a = q.submit("x")
    real = q._save

    def save(job):
        if job.get("status") == "running":
            raise OSError("disque plein")
        real(job)

    monkeypatch.setattr(q, "_save", save)
    q.run_once()
    assert q.status(a)["status"] == "error" and a not in q.order


def test_reload_requeues_and_keeps_lyrics(tmp_path):
    calls = []

    def lyrics(job):
        calls.append(job["id"])
        return fake_lyrics(job)

    q = make(tmp_path, lyrics=lyrics)
    a = q.submit("x")
    job = q.jobs[a]
    job.update(status="running", stage="music", lyrics=LYRICS, title="T", caption="c", seed=7, duration=90, timings={})
    q._save(job)
    q2 = make(tmp_path, lyrics=lyrics)
    assert q2.status(a)["status"] == "queued"
    q2.run_once()
    assert q2.status(a)["status"] == "ready" and calls == []
    assert q2.jobs[a]["seed"] == 7


def test_parse_llm_rejects_artist_and_bad_lyrics(tmp_path):
    path = tmp_path / "l.txt"
    raw = json.dumps({"titre": "Hommage à Stromae", "caption": "pop, male vocal, piano, synth bass, polished, melancholic",
                      "bpm": 100, "artistes_cites": ["Stromae"], "paroles": LYRICS})
    res, why = user_songs.parse_llm(raw, "dans le style de Stromae", 90, path)
    assert res is None and "Stromae" in why
    raw = json.dumps({"titre": "Nuit", "caption": "pop, male vocal, piano, synth bass, polished, melancholic",
                      "bpm": 100, "artistes_cites": [], "paroles": "du texte sans balise"})
    res, why = user_songs.parse_llm(raw, "x", 90, path)
    assert res is None and "contrôle des paroles" in why
    res, why = user_songs.parse_llm("pas du json", "x", 90, path)
    assert res is None


def test_parse_llm_ok_and_title_sanitized(tmp_path):
    path = tmp_path / "l.txt"
    raw = json.dumps({"titre": "Pluie : du soir?", "caption": "funk, female vocal, slap bass, rhythm guitar, warm, joyful",
                      "bpm": 400, "artistes_cites": [], "paroles": LYRICS})
    res, why = user_songs.parse_llm(raw, "x", 90, path)
    assert why is None and res["title"] == "Pluie du soir" and res["bpm"] is None
    assert path.read_text(encoding="utf-8").startswith("[verse]")


def test_write_lyrics_retries_once(tmp_path):
    good = json.dumps({"titre": "Nuit", "caption": "funk, female vocal, slap bass, rhythm guitar, warm, joyful",
                       "bpm": 110, "artistes_cites": [], "paroles": LYRICS})
    answers = iter(["{}", good])
    prompts = []

    def llm(user):
        prompts.append(user)
        return next(answers)

    res = user_songs.write_lyrics("x", 90, tmp_path / "l.txt", llm=llm)
    assert res["title"] == "Nuit" and len(res["attempts"]) == 2 and "refusée" in prompts[1]
    answers = iter(["{}", "{}"])
    try:
        user_songs.write_lyrics("x", 90, tmp_path / "l.txt", llm=lambda u: next(answers))
        assert False
    except user_songs.SongError as e:
        assert e.kind == "lyrics"


def test_pick_duration_range():
    values = {user_songs.pick_duration() for _ in range(300)}
    assert min(values) >= 45 and max(values) <= 135 and all(v % 5 == 0 for v in values)


def test_style_refs_detected_without_llm(tmp_path):
    assert user_songs.style_refs("un funk dans l'esprit de Daft Punk, basse slap") == ["Daft Punk"]
    assert user_songs.style_refs("un rock comme les Beatles") == ["Beatles"]
    assert user_songs.style_refs("une valse musette avec accordéon") == []
    raw = json.dumps({"titre": "Daft Punk en vacances", "caption": "nu-disco, female vocal, slap bass, funky guitar, polished, joyful",
                      "bpm": 120, "artistes_cites": [], "paroles": LYRICS})
    res, why = user_songs.parse_llm(raw, "dans le style de Daft Punk", 90, tmp_path / "l.txt")
    assert res is None and "Daft Punk" in why


def test_strip_directions_keeps_sung_echoes():
    text = "[intro]\n(Rythme saccadé)\n\n[verse]\nLa mer\n(La mer)\n\n[outro]\n(Fade out)\n"
    out = user_songs.strip_directions(text)
    assert "Rythme" not in out and "Fade" not in out and "(La mer)" in out
