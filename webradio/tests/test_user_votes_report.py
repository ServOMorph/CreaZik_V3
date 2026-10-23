import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import user_votes_report as rep  # noqa: E402


def write(path, voters):
    path.write_text(json.dumps({"voters": voters}), encoding="utf-8")


def test_collect_counts_votes_per_track(tmp_path):
    f = tmp_path / "uv.json"
    write(f, {"a": {"p:1": {"vote": "up", "t": "2026-10-18T10:00:00+02:00"}, "p:2": {"vote": "down", "t": "x"}},
              "b": {"p:1": {"vote": "up", "t": "2026-10-18T11:00:00+02:00"}},
              "c": {}})
    per, voters = rep.collect(f)
    assert per["p:1"]["up"] == 2 and per["p:1"]["down"] == 0
    assert per["p:1"]["last"] == "2026-10-18T11:00:00+02:00"
    assert per["p:2"]["down"] == 1
    assert voters == {"a", "b"}


def test_rows_min_votes_and_order(tmp_path, monkeypatch):
    monkeypatch.setattr(rep, "track_names", lambda: {"p:1": "Un"})
    monkeypatch.setattr(rep, "owner_scores", lambda: {"p:1": -3, "p:2": 2})
    per = {"p:1": {"up": 2, "down": 0, "last": ""}, "p:2": {"up": 0, "down": 1, "last": ""},
           "p:3": {"up": 1, "down": 0, "last": ""}}
    items = rep.rows(per, 1)
    assert [r["key"] for r in items] == ["p:2", "p:3", "p:1"]
    by_key = {r["key"]: r for r in items}
    assert by_key["p:1"]["disagree"] is True and by_key["p:1"]["name"] == "Un"
    assert by_key["p:2"]["disagree"] is True
    assert by_key["p:3"]["owner"] is None and by_key["p:3"]["disagree"] is False
    assert [r["key"] for r in rep.rows(per, 2)] == ["p:1"]
    assert rep.rows(per, 3) == []


def test_missing_file_gives_empty_report(tmp_path):
    per, voters = rep.collect(tmp_path / "absent.json")
    assert per == {} and voters == set()
    assert rep.rows(per, 1) == []
