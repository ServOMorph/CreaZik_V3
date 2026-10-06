import json
import random
import struct
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radio_engine import RadioEngine  # noqa: E402


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


def write_wav(path, seconds, rate=8000):
    data = b"\x00" * int(seconds * rate)
    header = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate, 1, 8)
    header += b"data" + struct.pack("<I", len(data))
    Path(path).write_bytes(header + data)


def build(root, playlists, settings=None):
    reg = []
    for pid, (count, dur, jingle) in playlists.items():
        out = root / "playlists" / pid / "outputs"
        out.mkdir(parents=True, exist_ok=True)
        gens = []
        for i in range(1, count + 1):
            rel = f"playlists/{pid}/outputs/{i:02d}.wav"
            write_wav(root / rel, dur)
            gens.append({"test_case_id": str(i), "name": f"{pid} {i}", "status": "generated", "output_file": rel,
                         "prompt": "x", "generated_at": "2026-01-01T00:00:00", "model": "m"})
        res = f"playlists/{pid}/outputs/playlist_results.json"
        (root / res).write_text(json.dumps({"model": "m", "generations": gens}), encoding="utf-8")
        entry = {"id": pid, "label": pid, "results": res, "description": ""}
        if jingle:
            entry["role"] = "jingle"
        reg.append(entry)
    (root / "playlists.json").write_text(json.dumps(reg), encoding="utf-8")
    if settings is not None:
        (root / "radio_settings.json").write_text(json.dumps(settings), encoding="utf-8")


def run(engine, clock, seconds, step=0.25):
    seq = []
    end = clock.t + seconds
    last = None
    while clock.t < end:
        engine.tick()
        cur = engine.current["key"] if engine.current else None
        if cur != last and cur is not None:
            seq.append((clock.t, cur, engine.current["jingle"]))
            last = cur
        clock.t += step
    return seq


def make(tmp, playlists, settings=None, seed=1):
    root = Path(tmp)
    build(root, playlists, settings)
    clock = Clock()
    return RadioEngine(root, time_fn=clock, rng=random.Random(seed)), clock


def preset(**kw):
    base = {"id": "p", "name": "p", "crossfade_s": 0, "fade_in_s": 0, "fade_out_s": 0, "gap_s": 0}
    base.update(kw)
    return {"active": "p", "jingle_preset": "same", "presets": [base]}


def test_continuity_and_jingles():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (6, 20, False), "j": (3, 5, True)},
                          {"jingle_every": 3, "no_repeat": 2, "transitions": preset()})
        seq = run(eng, clock, 600)
        assert len(seq) > 15, len(seq)
        run_len = 0
        for _, key, is_j in seq:
            if is_j:
                assert run_len == 3, f"jingle apres {run_len} morceaux"
                run_len = 0
            else:
                run_len += 1
        for (t0, _, _), (t1, k, _) in zip(seq, seq[1:]):
            assert 4 <= t1 - t0 <= 21, (t1 - t0)


def test_crossfade_overlap_and_two_active_max():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (6, 30, False)},
                          {"jingles_enabled": False, "transitions": preset(crossfade_s=4)})
        max_active = 0
        starts = []
        end = clock.t + 400
        while clock.t < end:
            eng.tick()
            snap = eng.snapshot(admin=True)
            max_active = max(max_active, len(snap["active"]))
            assert len(snap["active"]) <= 2
            if snap["active"]:
                s = snap["active"][-1]
                if not starts or starts[-1] != s["uid"]:
                    starts.append(s["uid"])
            clock.t += 0.25
        assert max_active == 2
        snap = eng.snapshot(admin=True)
        for a, b in zip(snap["upcoming"], snap["upcoming"][1:]):
            assert abs((a["end"] - b["start"]) - 4) < 1e-6, (a["end"], b["start"])


def test_gap_and_fades():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (4, 20, False)},
                          {"jingles_enabled": False, "transitions": preset(fade_in_s=2, fade_out_s=3, gap_s=1)})
        seq = run(eng, clock, 200)
        for (t0, _, _), (t1, _, _) in zip(seq, seq[1:]):
            assert 20.5 <= t1 - t0 <= 21.8, t1 - t0
        snap = eng.snapshot(admin=True)
        nxt = snap["upcoming"][0]
        assert nxt["fade_in"] == 2
        assert snap["active"][0]["fade_out"] == 3


def test_weights_and_zero():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (5, 10, False), "b": (5, 10, False), "c": (5, 10, False)},
                          {"weights": {"a": 10, "b": 1, "c": 0}, "jingles_enabled": False, "no_repeat": 0,
                           "transitions": preset()})
        seq = run(eng, clock, 10 * 4000, step=1.0)
        counts = {"a": 0, "b": 0, "c": 0}
        for _, key, _ in seq:
            counts[key.split(":")[0]] += 1
        assert counts["c"] == 0
        ratio = counts["a"] / max(1, counts["b"])
        assert 6 < ratio < 16, counts


def test_thumbs_raise_probability():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (4, 10, False)},
                          {"jingles_enabled": False, "no_repeat": 0, "thumb_strength": 0.5, "transitions": preset()})
        (Path(tmp) / "votes.json").write_text(json.dumps({"tracks": {"a:1": {"up": 4, "down": 0},
                                                                     "a:2": {"up": 0, "down": 3}}}), encoding="utf-8")
        seq = run(eng, clock, 10 * 3000, step=1.0)
        counts = {}
        for _, key, _ in seq:
            counts[key] = counts.get(key, 0) + 1
        assert counts["a:1"] > counts["a:3"] > counts["a:2"], counts


def test_skip_now_and_queue_actions():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (5, 60, False), "b": (3, 60, False)},
                          {"jingles_enabled": False, "transitions": preset()})
        run(eng, clock, 5)
        first = eng.current["key"]
        assert eng.action("skip", {})
        assert eng.current["key"] != first or len(eng.cat.tracks) == 1
        assert eng.action("now", {"key": "b:2"})
        assert eng.current["key"] == "b:2"
        snap = eng.snapshot(admin=True)
        assert len([x for x in snap["active"] if x["key"] == "b:2"]) == 1
        assert eng.action("next", {"key": "a:5"})
        assert eng.action("next", {"key": "a:4"})
        queue = [q["key"] for q in eng.snapshot(admin=True)["queue"]]
        assert queue[:2] == ["a:5", "a:4"], queue
        assert eng.action("front", {"key": "b:3"})
        queue = [q["key"] for q in eng.snapshot(admin=True)["queue"]]
        assert queue[:3] == ["b:3", "a:5", "a:4"], queue
        assert eng.action("remove", {"index": 1})
        queue = [q["key"] for q in eng.snapshot(admin=True)["queue"]]
        assert queue[:2] == ["b:3", "a:4"], queue
        assert eng.action("playlist_next", {"id": "b"})
        queue = [q["key"] for q in eng.snapshot(admin=True)["queue"]]
        assert queue[:5] == ["b:3", "a:4", "b:1", "b:2", "b:3"], queue
        assert eng.action("playlist_now", {"id": "a"})
        assert eng.current["key"].startswith("a:")
        assert not eng.action("now", {"key": "zzz:1"})


def test_many_thumbs_down_removes_track():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (4, 10, False)},
                          {"jingles_enabled": False, "no_repeat": 0, "thumb_strength": 0.15, "transitions": preset()})
        (Path(tmp) / "votes.json").write_text(json.dumps({"tracks": {"a:1": {"up": 0, "down": 100}}}), encoding="utf-8")
        seq = run(eng, clock, 10 * 3000, step=1.0)
        counts = {}
        for _, key, _ in seq:
            counts[key] = counts.get(key, 0) + 1
        assert counts.get("a:1", 0) <= 30, counts
        assert min(counts.get("a:2", 0), counts.get("a:3", 0), counts.get("a:4", 0)) > 200, counts


def test_overlays_jingle_and_ads():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (8, 40, False), "j": (2, 5, True)},
                          {"jingle_every": 4, "ads_every": 5, "ad_seconds": 9, "ad_offset_s": 10,
                           "no_repeat": 2, "transitions": preset()})
        ads = []
        jingles = 0
        tracks = 0
        end = clock.t + 2400
        last_uid = None
        while clock.t < end:
            eng.tick()
            cur = eng.current
            if cur and cur["uid"] != last_uid:
                last_uid = cur["uid"]
                ov = cur.get("overlay")
                if cur["jingle"]:
                    jingles += 1
                    assert ov and ov["type"] == "jingle"
                else:
                    tracks += 1
                    if ov:
                        assert ov["type"] == "ad"
                        assert abs((ov["end"] - ov["start"]) - 9) < 1e-6
                        assert abs((ov["start"] - cur["start"]) - 10) < 1e-6
                        ads.append(tracks)
            clock.t += 0.25
        assert jingles >= 3 and len(ads) >= 3, (jingles, ads)
        assert all(b - a == 5 for a, b in zip(ads, ads[1:])), ads


def test_move_front_and_play_index():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (14, 60, False)}, {"jingles_enabled": False, "transitions": preset()})
        run(eng, clock, 2)
        queue = eng.snapshot(admin=True)["queue"]
        target = queue[3]["key"]
        assert eng.action("move_front", {"index": 3})
        after = eng.snapshot(admin=True)["queue"]
        assert after[0]["key"] == target and after[0]["explicit"]
        assert [q["key"] for q in after].count(target) == 1, [q["key"] for q in after]
        pick = after[2]["key"]
        assert eng.action("play_index", {"index": 2})
        assert eng.current["key"] == pick
        assert [q["key"] for q in eng.snapshot(admin=True)["queue"]].count(pick) <= 1


def test_settings_change_revalidates_queue():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (5, 20, False), "b": (5, 20, False)},
                          {"jingles_enabled": False, "transitions": preset()})
        run(eng, clock, 2)
        assert any(q["key"].startswith("b:") for q in eng.snapshot(admin=True)["queue"])
        (Path(tmp) / "radio_settings.json").write_text(json.dumps(
            {"weights": {"b": 0}, "jingles_enabled": False, "transitions": preset()}), encoding="utf-8")
        import os
        os.utime(Path(tmp) / "radio_settings.json", (clock.t + 100, clock.t + 100))
        eng.action("noop_refresh", {})
        eng._compose()
        assert all(q["key"].startswith("a:") for q in eng.snapshot(admin=True)["queue"])


def test_song_cooldown_across_versions():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, {"a": (30, 10, False), "b": (30, 10, False), "c": (30, 10, False)})
        for pid in ("a", "b", "c"):
            cfg = {"song_group": "x", "test_cases": []}
            (root / "playlists" / pid / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
        (root / "radio_settings.json").write_text(json.dumps(
            {"jingles_enabled": False, "no_repeat": 3, "no_repeat_songs": 10, "transitions": preset()}), encoding="utf-8")
        clock = Clock()
        eng = RadioEngine(root, time_fn=clock, rng=random.Random(5))
        seq = run(eng, clock, 10 * 600, step=1.0)
        songs = [k.split(":")[1] for _, k, _ in seq]
        assert len(songs) > 200
        window = 8
        for i in range(window, len(songs)):
            assert songs[i] not in songs[i - window:i], (i, songs[i - window:i + 1])


def test_no_consecutive_repeat_with_single_track_playlists():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {f"p{i}": (1, 10, False) for i in range(6)},
                          {"jingles_enabled": False, "no_repeat": 0, "no_repeat_songs": 0,
                           "dynamics_enabled": False, "transitions": preset()}, seed=11)
        seq = run(eng, clock, 10 * 4000, step=1.0)
        keys = [k for _, k, _ in seq]
        assert len(keys) > 300
        for a, b in zip(keys, keys[1:]):
            assert a != b, (a, b)
        snap = eng.snapshot(admin=True)["queue"]
        for a, b in zip(snap, snap[1:]):
            assert a["key"] != b["key"], [q["key"] for q in snap]


def write_features(root, pid, count, **feat):
    for i in range(1, count + 1):
        rel = root / "playlists" / pid / "outputs" / f"{i:02d}.wav.feat.json"
        rel.write_text(json.dumps(feat), encoding="utf-8")


def paris_epoch(hour, minute=0):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime(2026, 10, 5, hour, minute, tzinfo=ZoneInfo("Europe/Paris")).timestamp()


def test_dynamics_follow_time_of_day():
    shares = {}
    for label, hour in (("matin", 5), ("soir", 17)):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(root, {"calme": (12, 10, False), "pechu": (12, 10, False)})
            write_features(root, "calme", 12, onset=1.0, centroid_hz=500.0, rms_db=-30.0, bpm=80.0)
            write_features(root, "pechu", 12, onset=10.0, centroid_hz=5000.0, rms_db=-10.0, bpm=80.0)
            (root / "radio_settings.json").write_text(json.dumps(
                {"jingles_enabled": False, "no_repeat": 0, "no_repeat_songs": 0, "dynamics_enabled": True,
                 "dynamics_strength": 1.0, "transitions": preset()}), encoding="utf-8")
            clock = Clock()
            clock.t = paris_epoch(hour, 30)
            eng = RadioEngine(root, time_fn=clock, rng=random.Random(2))
            seq = run(eng, clock, 3000, step=1.0)
            n = len(seq)
            shares[label] = sum(1 for _, k, _ in seq if k.startswith("pechu")) / n
    assert shares["matin"] < 0.3, shares
    assert shares["soir"] > 0.7, shares


def test_tempo_smoothing_reduces_jumps():
    results = {}
    for enabled in (False, True):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(root, {"lent": (12, 10, False), "rapide": (12, 10, False)})
            write_features(root, "lent", 12, onset=5.0, centroid_hz=2000.0, rms_db=-20.0, bpm=80.0)
            write_features(root, "rapide", 12, onset=5.0, centroid_hz=2000.0, rms_db=-20.0, bpm=115.0)
            (root / "radio_settings.json").write_text(json.dumps(
                {"jingles_enabled": False, "no_repeat": 0, "no_repeat_songs": 0, "dynamics_enabled": enabled,
                 "dynamics_strength": 1.0, "dyn_amp": 0.0, "transitions": preset()}), encoding="utf-8")
            clock = Clock()
            clock.t = paris_epoch(12)
            eng = RadioEngine(root, time_fn=clock, rng=random.Random(4))
            seq = run(eng, clock, 3000, step=1.0)
            kinds = [k.split(":")[0] for _, k, _ in seq]
            results[enabled] = sum(1 for a, b in zip(kinds, kinds[1:]) if a != b) / max(1, len(kinds) - 1)
    assert results[True] < results[False] * 0.5, results


def test_catalog_works_with_mp3_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, {"a": (3, 20, False), "b": (3, 20, False)})
        for wav in list(root.glob("playlists/*/outputs/*.wav")):
            size = wav.stat().st_size
            (wav.with_suffix(".mp3")).write_bytes(b"\x00" * int(20 * 192000 / 8))
            wav.unlink()
        clock = Clock()
        eng = RadioEngine(root, time_fn=clock, rng=random.Random(3))
        seq = run(eng, clock, 300, step=1.0)
        assert len(seq) >= 10
        assert all(abs(t["duration"] - 20) < 0.5 for t in eng.cat.tracks.values())


def test_stats_sum_to_100():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (4, 10, False), "b": (8, 10, False)}, {"weights": {"a": 5, "b": 5}, "transitions": preset()})
        run(eng, clock, 2)
        st = eng.stats()
        assert abs(sum(p["share"] for p in st) - 100) < 0.1
        assert abs(sum(t["share"] for p in st for t in p["tracks"]) - 100) < 0.1
        a = next(p for p in st if p["id"] == "a")
        b = next(p for p in st if p["id"] == "b")
        assert a["tracks"][0]["share"] > b["tracks"][0]["share"]


def test_restart_resumes_current_track():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, {"a": (6, 60, False)})
        (root / "radio_settings.json").write_text(json.dumps({"jingles_enabled": False, "transitions": preset()}), encoding="utf-8")
        clock = Clock()
        eng = RadioEngine(root, time_fn=clock, rng=random.Random(3), persist=True)
        run(eng, clock, 30)
        key, start = eng.current["key"], eng.current["start"]
        clock.t += 5
        eng2 = RadioEngine(root, time_fn=clock, rng=random.Random(4), persist=True)
        eng2.tick()
        assert eng2.current["key"] == key and eng2.current["start"] == start
        snap = eng2.snapshot()
        assert snap["active"] and snap["active"][0]["key"] == key
        eng2.tick()
        assert eng2.current["key"] == key


def test_listener_snapshot_hides_queue():
    with tempfile.TemporaryDirectory() as tmp:
        eng, clock = make(tmp, {"a": (5, 20, False)}, {"jingles_enabled": False, "transitions": preset()})
        run(eng, clock, 2)
        snap = eng.snapshot(admin=False)
        assert "queue" not in snap and "played" not in snap
        assert len(snap["upcoming"]) <= 2 and snap["active"]


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("OK  ", name)
            except Exception as exc:
                failed += 1
                import traceback
                traceback.print_exc()
                print("FAIL", name, exc)
    sys.exit(1 if failed else 0)
