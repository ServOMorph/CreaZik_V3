import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import admin_jingle  # noqa: E402
from test_radio_engine import make, preset, run  # noqa: E402

NODE = shutil.which("node")


def test_phonetic_spelling():
    p = admin_jingle.phonetic
    assert p("Bienvenue sur CréaZik IA WebRadio") == "Bienvenue sur Créa Zique I A Ouèbe Radio"
    assert p("Une pub SérénIA Tech") == "Une pub Sérénia Tèk"
    assert p("SérénIA et Creazik") == "Sérénia et Créa Zique"
    assert p("La Web Radio") == "La Ouèbe Radio"
    assert p("IAMBE, via, IA.") == "IAMBE, via, I A."


def test_clean_text():
    c = admin_jingle.clean_text
    assert c("  Bonjour\n\ttout   le monde ") == "Bonjour tout le monde"
    assert c("x" * 300) == "x" * 300
    for bad in ("x" * 301, "", "   ", None, 12, ["a"], {"a": 1}):
        assert c(bad) is None


def test_queue_one_job_at_a_time_and_order():
    seen = []
    q = admin_jingle.JingleQueue(runner=lambda job: seen.append(job["text"]) or {"key": "k:1", "duration_s": 2.5, "broadcast": True})
    a = q.submit("premier", "kokoro")
    b = q.submit("second", "chatterbox")
    assert q.status(a)["status"] == "queued" and q.status(b)["ahead"] == 1
    assert q.process_one()
    assert seen == ["premier"] and q.status(a)["status"] == "ready" and q.status(b)["status"] == "queued"
    assert q.status(a)["duration_s"] == 2.5 and q.status(a)["elapsed_s"] is not None
    assert q.process_one() and seen == ["premier", "second"]
    assert not q.process_one()
    assert q.status("f" * 32) is None


def test_queue_spoken_text_error_and_limit(monkeypatch):
    def boom(job):
        assert job["spoken"] == "Créa Zique" and job["text"] == "CréaZik"
        raise RuntimeError("synthèse en échec")
    q = admin_jingle.JingleQueue(runner=boom)
    jid = q.submit("CréaZik", "kokoro")
    q.process_one()
    st = q.status(jid)
    assert st["status"] == "error" and "échec" in st["error"]
    ids = [q.submit(f"t{i}", "kokoro") for i in range(admin_jingle.QUEUE_MAX)]
    assert all(ids) and q.submit("trop", "kokoro") is None


def test_dry_run_env_never_calls_runner(monkeypatch):
    monkeypatch.setenv("CREAZIK_JINGLE_DRY_RUN", "1")
    q = admin_jingle.JingleQueue(runner=lambda job: pytest.fail("synthèse lancée en mode d'essai"))
    jid = q.submit("Bonjour", "chatterbox")
    assert q.status(jid)["dry_run"] is True
    q.process_one()
    assert q.status(jid)["status"] == "ready" and q.status(jid)["broadcast"] is False


def test_subprocess_command_uses_cpu_and_annonce(monkeypatch, tmp_path):
    fake_py = tmp_path / "python.exe"
    fake_py.write_text("", encoding="utf-8")
    monkeypatch.setenv("CREAZIK_KOKORO_PYTHON", str(fake_py))
    captured = {}

    class R:
        returncode = 0
        stdout = 'annonce jingles-annonces:9 : 3.0 s\n{"key": "jingles-annonces:9", "duration_s": 3.0, "broadcast": true}\n'
        stderr = ""

    def fake_run(cmd, **kw):
        captured["cmd"], captured["env"] = cmd, kw["env"]
        return R()

    monkeypatch.setattr(admin_jingle.subprocess, "run", fake_run)
    q = admin_jingle.JingleQueue()
    jid = q.submit("Salut WebRadio", "kokoro")
    q.process_one()
    st = q.status(jid)
    assert st["status"] == "ready" and st["key"] == "jingles-annonces:9" and st["broadcast"] is True
    cmd = captured["cmd"]
    assert cmd[0] == str(fake_py) and cmd[1].endswith("annonce.py") and cmd[2] == "Salut Ouèbe Radio"
    assert cmd[cmd.index("--affiche") + 1] == "Salut WebRadio" and cmd[cmd.index("--moteur") + 1] == "kokoro"
    assert "--sans-diffusion" not in cmd and captured["env"]["CUDA_VISIBLE_DEVICES"] == ""


@pytest.mark.skipif(NODE is None, reason="node absent")
def test_global_prev_key_js():
    script = (
        "const fs=require('fs');let def=null;global.window={CreaZik:{registerPlugin:d=>{def=d;}}};"
        "eval(fs.readFileSync(process.argv[1],'utf8'));"
        "const k=def.prevKey;"
        "console.log(JSON.stringify([k([{key:'a:1'},{key:'j:1',jingle:true},{key:'b:2'},{key:'j:2',jingle:true}]),"
        "k([{key:'j:1',jingle:true}]),k([]),k(undefined)]));"
    )
    out = subprocess.run([NODE, "-e", script, str(ROOT / "plugins" / "commandes_globales.js")],
                         capture_output=True, text=True, timeout=30, check=True).stdout
    assert json.loads(out) == ["b:2", None, None, None]


def test_global_prev_replays_last_played_song():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (4, 30, False), "j": (2, 5, True)},
                          {"jingle_every": 1, "no_repeat": 0, "transitions": preset()})
        run(eng, clock, 200)
        played = eng.snapshot(admin=True)["played"]
        songs = [p["key"] for p in played if not p["jingle"]]
        assert songs and any(p["jingle"] for p in played)
        key = songs[-1]
        assert eng.action("now", {"key": key})
        if eng.current["jingle"]:
            upcoming = eng.snapshot(admin=True)["upcoming"]
            assert next(u["key"] for u in upcoming if not u["jingle"]) == key
        else:
            assert eng.current["key"] == key
        eng.tick()
        with tempfile.TemporaryDirectory() as tmp2:
            eng2, clock2 = make(tmp2, {"a": (4, 30, False)}, {"jingles_enabled": False, "transitions": preset()})
            run(eng2, clock2, 100)
            key2 = [p["key"] for p in eng2.snapshot(admin=True)["played"] if not p["jingle"]][-1]
            assert eng2.action("now", {"key": key2}) and eng2.current["key"] == key2
