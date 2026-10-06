import json
import math
import os
import random
import struct
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

QUEUE_LEN = 8
PLAYED_LEN = 8
SKIP_FADE_OUT = 1.5
SKIP_FADE_IN = 1.0
MAX_CF_RATIO = 0.4
REFRESH_EVERY_S = 5.0
MP3_BITRATE = 192000
LOCAL_TZ = ZoneInfo("Europe/Paris")
ENERGY_WEIGHTS = {"onset": 0.35, "centroid_hz": 0.25, "rms_db": 0.2, "bpm": 0.2}

DEFAULT_TRANSITIONS = {
    "active": "fondu",
    "jingle_preset": "net",
    "presets": [
        {"id": "net", "name": "Enchaînement net", "crossfade_s": 0, "fade_in_s": 0, "fade_out_s": 0, "gap_s": 0},
        {"id": "fondu", "name": "Fondu doux", "crossfade_s": 0, "fade_in_s": 2, "fade_out_s": 2, "gap_s": 0.3},
    ],
}
DEFAULT_RADIO = {
    "default_weight": 5,
    "weights": {},
    "jingle_every": 5,
    "jingles_enabled": True,
    "favorites_only": False,
    "no_repeat": 3,
    "no_repeat_songs": 15,
    "excluded": [],
    "thumb_strength": 0.15,
    "ads_enabled": True,
    "ads_every": 5,
    "ad_seconds": 9,
    "ad_offset_s": 10,
    "visual_transition_s": 5,
    "dynamics_enabled": True,
    "dynamics_strength": 1.0,
    "dyn_base": 0.5,
    "dyn_amp": 0.33,
    "dyn_peak_hour": 17.5,
    "dyn_weekend_shift_h": 1.0,
    "dyn_energy_sigma": 0.25,
    "dyn_tempo_tolerance": 0.25,
    "transitions": DEFAULT_TRANSITIONS,
}


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def wav_duration(path):
    try:
        total = os.path.getsize(path)
        with open(path, "rb") as f:
            head = f.read(65536)
        pos = 12
        sr = ch = bits = None
        while pos + 8 <= len(head):
            cid = head[pos:pos + 4]
            size = struct.unpack("<I", head[pos + 4:pos + 8])[0]
            if cid == b"fmt ":
                _, ch, sr, _, _, bits = struct.unpack("<HHIIHH", head[pos + 8:pos + 24])
            elif cid == b"data":
                size = min(size, total - (pos + 8))
                if not (sr and ch and bits):
                    return None
                return size / float(sr * ch * (bits // 8))
            pos += 8 + size + (size & 1)
    except Exception:
        pass
    return None


class Catalog:
    def __init__(self, root):
        self.root = Path(root)
        self.sig = None
        self.tracks = {}
        self.playlists = []
        self._durations = {}
        self._features = {}

    def _signature(self, registry):
        parts = [self._mtime(self.root / "playlists.json")]
        for p in registry:
            parts.append(self._mtime(self.root / p["results"]))
        return tuple(parts)

    def _feature_count(self):
        try:
            return sum(1 for _ in self.root.glob("playlists/*/outputs/*.feat.json"))
        except OSError:
            return 0

    @staticmethod
    def _mtime(path):
        try:
            return os.path.getmtime(path)
        except OSError:
            return 0

    def _duration(self, rel):
        wav = self.root / rel
        mp3 = wav.with_suffix(".mp3")
        src = wav if wav.exists() else mp3
        key = (rel, self._mtime(src))
        if key not in self._durations:
            if src == wav:
                dur = wav_duration(wav)
            else:
                feat = read_json(self.root / (rel + ".feat.json"), None) or {}
                dur = float(feat.get("duration_s") or 0)
                if not dur and mp3.exists():
                    dur = os.path.getsize(mp3) * 8 / MP3_BITRATE
            self._durations[key] = dur
        return self._durations[key]

    def _load_features(self, rel):
        path = self.root / (rel + ".feat.json")
        key = (rel, self._mtime(path))
        if key not in self._features:
            self._features[key] = read_json(path, None)
        return self._features[key]

    @staticmethod
    def _ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        n = max(1, len(values) - 1)
        for pos, i in enumerate(order):
            ranks[i] = pos / n
        return ranks

    def _compute_energy(self, tracks):
        pool = [t for t in tracks.values() if not t["jingle"] and t.get("feat")]
        if len(pool) < 3:
            return
        columns = {}
        for name in ENERGY_WEIGHTS:
            vals = []
            for t in pool:
                v = t["feat"].get(name)
                if name == "bpm" and v:
                    v = max(70.0, min(170.0, v))
                vals.append(float(v) if v is not None else 0.0)
            columns[name] = self._ranks(vals)
        for i, t in enumerate(pool):
            t["energy"] = round(sum(ENERGY_WEIGHTS[n] * columns[n][i] for n in ENERGY_WEIGHTS), 4)
            t["bpm"] = t["feat"].get("bpm")

    def refresh(self):
        registry = read_json(self.root / "playlists.json", [])
        sig = self._signature(registry) + (self._feature_count(),)
        if sig == self.sig:
            return False
        tracks = {}
        playlists = []
        for p in registry:
            data = read_json(self.root / p["results"], {})
            cfg = read_json(self.root / "playlists" / p["id"] / "config.json", {})
            group = cfg.get("song_group")
            is_jingle = p.get("role") == "jingle"
            keys = []
            for g in data.get("generations", []):
                if g.get("status") != "generated":
                    continue
                rel = g.get("output_file", "")
                dur = self._duration(rel)
                if not dur:
                    continue
                key = f"{p['id']}:{g['test_case_id']}"
                tracks[key] = {
                    "key": key, "song": f"{group}:{g['test_case_id']}" if group else key, "playlist": p["id"], "playlist_label": p.get("label", p["id"]),
                    "playlist_description": p.get("description", ""), "jingle": is_jingle,
                    "name": g.get("name", key), "prompt": g.get("prompt", ""), "type": g.get("type", ""),
                    "generated_at": g.get("generated_at", ""), "model": g.get("model") or data.get("model", ""),
                    "file": rel, "duration": dur, "energy_wh_est": g.get("energy_wh_est"),
                    "feat": self._load_features(rel), "energy": None, "bpm": None,
                }
                keys.append(key)
            if keys:
                playlists.append({"id": p["id"], "label": p.get("label", p["id"]), "jingle": is_jingle, "keys": keys})
        self._compute_energy(tracks)
        self.tracks = tracks
        self.playlists = playlists
        self.sig = sig
        return True


class RadioEngine:
    def __init__(self, root, time_fn=time.time, rng=None, persist=False):
        self.root = Path(root)
        self.now = time_fn
        self.rng = rng or random.Random()
        self.lock = threading.RLock()
        self.cat = Catalog(root)
        self.rev = 0
        self.uid = 0
        self.active = []
        self.current = None
        self.explicit = []
        self.auto = []
        self.upcoming = []
        self.played = []
        self.history = []
        self.since_jingle = 0
        self.jingle_seq = 0
        self.since_ad = 0
        self.ad_seq = 0
        self.jingle_msg_seq = 0
        self.song_history = []
        self._last_refresh = 0.0
        self._settings = (None, dict(DEFAULT_RADIO))
        self._votes = (None, {})
        self._favs = (None, set())
        self.persist = persist
        if persist:
            self._load_state()

    def _state_path(self):
        return self.root / "radio_state.json"

    def _save_state(self):
        data = {
            "uid": self.uid, "rev": self.rev, "active": self.active, "current_uid": self.current["uid"] if self.current else None,
            "explicit": self.explicit, "auto": self.auto, "played": self.played, "history": self.history,
            "since_jingle": self.since_jingle, "jingle_seq": self.jingle_seq, "since_ad": self.since_ad,
            "ad_seq": self.ad_seq, "jingle_msg_seq": self.jingle_msg_seq, "song_history": self.song_history,
        }
        tmp = self._state_path().with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self._state_path())
        except OSError:
            pass

    def _load_state(self):
        data = read_json(self._state_path(), None)
        if not data:
            return
        t = self.now()
        self.uid = data.get("uid", 0)
        self.rev = data.get("rev", 0) + 1
        self.active = [it for it in data.get("active", []) if it.get("end", 0) > t]
        cur_uid = data.get("current_uid")
        pool = data.get("active", [])
        self.current = next((it for it in pool if it.get("uid") == cur_uid), None)
        self.explicit = data.get("explicit", [])
        self.auto = data.get("auto", [])
        self.played = data.get("played", [])
        self.history = data.get("history", [])
        self.since_jingle = data.get("since_jingle", 0)
        self.jingle_seq = data.get("jingle_seq", 0)
        self.since_ad = data.get("since_ad", 0)
        self.ad_seq = data.get("ad_seq", 0)
        self.jingle_msg_seq = data.get("jingle_msg_seq", 0)
        self.song_history = data.get("song_history", [])

    def _cached(self, slot, path, loader):
        mtime = Catalog._mtime(path)
        if slot[0] != mtime:
            return (mtime, loader())
        return slot

    def settings(self):
        def load():
            data = read_json(self.root / "radio_settings.json", {})
            merged = json.loads(json.dumps(DEFAULT_RADIO))
            merged.update(data)
            return merged
        self._settings = self._cached(self._settings, self.root / "radio_settings.json", load)
        return self._settings[1]

    def votes(self):
        self._votes = self._cached(self._votes, self.root / "votes.json",
                                   lambda: read_json(self.root / "votes.json", {}).get("tracks", {}))
        return self._votes[1]

    def favorites(self):
        self._favs = self._cached(self._favs, self.root / "favorites.json",
                                  lambda: set(read_json(self.root / "favorites.json", [])))
        return self._favs[1]

    def _preset(self, prev_jingle, next_jingle):
        tr = self.settings().get("transitions") or DEFAULT_TRANSITIONS
        presets = tr.get("presets") or DEFAULT_TRANSITIONS["presets"]
        by_id = {p["id"]: p for p in presets}
        pid = tr.get("active")
        if (prev_jingle or next_jingle) and tr.get("jingle_preset") and tr["jingle_preset"] != "same":
            pid = tr["jingle_preset"]
        return by_id.get(pid) or presets[0]

    def _transition(self, prev, next_dur, next_jingle):
        pr = self._preset(prev["jingle"], next_jingle)
        cf = float(pr.get("crossfade_s") or 0)
        if cf > 0:
            cf = min(cf, MAX_CF_RATIO * min(prev["duration"], next_dur))
        if cf > 0.2:
            return prev["end"] - cf, cf, cf
        gap = float(pr.get("gap_s") or 0)
        fout = min(float(pr.get("fade_out_s") or 0), prev["duration"] / 2)
        fin = min(float(pr.get("fade_in_s") or 0), next_dur / 2)
        return prev["end"] + gap, fout, fin

    def _multiplier(self, key):
        v = self.votes().get(key) or {}
        score = (v.get("up") or 0) - (v.get("down") or 0)
        try:
            k = float(self.settings().get("thumb_strength", 0.15))
        except (TypeError, ValueError):
            k = 0.15
        return max(1e-9, min(20.0, math.exp(k * score)))

    def _weight(self, playlist_id):
        st = self.settings()
        w = (st.get("weights") or {}).get(playlist_id)
        return st.get("default_weight", 5) if w is None else w

    def _playable_groups(self):
        st = self.settings()
        excluded = set(st.get("excluded") or [])
        favs = self.favorites() if st.get("favorites_only") else None
        groups = []
        for pl in self.cat.playlists:
            if pl["jingle"] or self._weight(pl["id"]) <= 0:
                continue
            keys = [k for k in pl["keys"] if k not in excluded and (favs is None or k in favs)]
            if keys:
                groups.append((pl, keys))
        return groups

    def _jingle_keys(self):
        excluded = set(self.settings().get("excluded") or [])
        out = []
        for pl in self.cat.playlists:
            if pl["jingle"]:
                out.extend(k for k in pl["keys"] if k not in excluded)
        return out

    def dyn_target(self, t):
        st = self.settings()
        local = datetime.fromtimestamp(t, LOCAL_TZ)
        hour = local.hour + local.minute / 60.0
        peak = float(st.get("dyn_peak_hour", 17.5))
        if local.weekday() >= 5:
            peak += float(st.get("dyn_weekend_shift_h", 1.0))
        e = float(st.get("dyn_base", 0.5)) + float(st.get("dyn_amp", 0.33)) * math.cos(2 * math.pi * (hour - peak) / 24.0)
        return max(0.0, min(1.0, e))

    def _dyn_factor(self, key, prev_key, slot_time):
        st = self.settings()
        strength = float(st.get("dynamics_strength", 1.0) or 0)
        if not st.get("dynamics_enabled", True) or strength <= 0:
            return 1.0
        tr = self.cat.tracks.get(key)
        if tr is None:
            return 1.0
        f = 1.0
        if tr.get("energy") is not None:
            sigma = max(0.05, float(st.get("dyn_energy_sigma", 0.25)))
            f *= math.exp(-0.5 * ((tr["energy"] - self.dyn_target(slot_time)) / sigma) ** 2)
        prev = self.cat.tracks.get(prev_key) if prev_key else None
        if prev and prev.get("bpm") and tr.get("bpm"):
            tol = max(0.05, float(st.get("dyn_tempo_tolerance", 0.25)))
            r = tr["bpm"] / prev["bpm"]
            d = min(abs(math.log2(r)), abs(math.log2(2 * r)), abs(math.log2(r / 2)))
            f *= math.exp(-0.5 * (d / tol) ** 2)
        return max(1e-3, f) ** strength

    def dynamics_info(self):
        with self.lock:
            self.cat.refresh()
            t = self.now()
            curve = [{"h": h / 2.0, "e": round(self._curve_at(h / 2.0, t), 3)} for h in range(0, 49)]
            local = datetime.fromtimestamp(t, LOCAL_TZ)
            with_energy = sum(1 for tr in self.cat.tracks.values() if tr.get("energy") is not None and not tr["jingle"])
            total = sum(1 for tr in self.cat.tracks.values() if not tr["jingle"])
            return {"enabled": bool(self.settings().get("dynamics_enabled", True)), "hour": round(local.hour + local.minute / 60.0, 2),
                    "target_now": round(self.dyn_target(t), 3), "curve": curve,
                    "tracks_with_features": with_energy, "tracks_total": total}

    def _curve_at(self, hour, t):
        st = self.settings()
        local = datetime.fromtimestamp(t, LOCAL_TZ)
        peak = float(st.get("dyn_peak_hour", 17.5))
        if local.weekday() >= 5:
            peak += float(st.get("dyn_weekend_shift_h", 1.0))
        e = float(st.get("dyn_base", 0.5)) + float(st.get("dyn_amp", 0.33)) * math.cos(2 * math.pi * (hour - peak) / 24.0)
        return max(0.0, min(1.0, e))

    def _song_of(self, key):
        tr = self.cat.tracks.get(key)
        return tr["song"] if tr else key

    def _pick_track(self, used, last=None, songs=None, slot_time=None):
        groups = self._playable_groups()
        if not groups:
            return None
        if slot_time is None:
            slot_time = self.now()
        prev_key = last or (self.current["key"] if self.current else None)
        others = [g for g in groups if any(k != prev_key for k in g[1])]
        if others:
            groups = others
        factors = {}
        for _, keys in groups:
            for k in keys:
                factors[k] = self._dyn_factor(k, prev_key, slot_time)

        def group_weight(g):
            keys = g[1]
            return self._weight(g[0]["id"]) * (sum(factors[k] for k in keys) / len(keys))

        total = sum(group_weight(g) for g in groups)
        r = self.rng.random() * total
        chosen = groups[-1]
        for g in groups:
            r -= group_weight(g)
            if r < 0:
                chosen = g
                break
        keys = chosen[1]
        avoid = last or (self.current["key"] if self.current else None)
        cands = [k for k in keys if k != avoid] or keys
        songs = songs or set()
        fresh = [k for k in cands if k not in used and self._song_of(k) not in songs and self._multiplier(k) >= 0.05]
        if fresh:
            cands = fresh
            weights = [self._multiplier(k) * factors[k] for k in cands]
        else:
            weights = [self._multiplier(k) * factors[k] * (0.01 if k in used else 1.0) for k in cands]
        return self.rng.choices(cands, weights=weights, k=1)[0]

    def _auto_ok(self, key):
        if key not in self.cat.tracks:
            return False
        return any(key in keys for _, keys in self._playable_groups())

    def _compose(self):
        st = self.settings()
        every = int(st.get("jingle_every") or 0)
        jingles = self._jingle_keys() if st.get("jingles_enabled") else []
        out = []
        sim = self.since_jingle
        jseq = self.jingle_seq
        used = set(self.history)
        for it in self.active:
            used.add(it["key"])
        songs = set(self.song_history)
        for it in self.active:
            songs.add(it.get("song") or it["key"])
        last = self.current["key"] if self.current else None
        t_now = self.now()
        slot_clock = [t_now + (max(0.0, self.current["end"] - t_now) if self.current else 0.0)]

        def add(entry):
            nonlocal sim, jseq, last
            if not entry["jingle"] and every > 0 and sim >= every and jingles:
                out.append({"key": jingles[jseq % len(jingles)], "jingle": True, "auto": True})
                jseq += 1
                sim = 0
            out.append(entry)
            tr_slot = self.cat.tracks.get(entry["key"])
            slot_clock[0] += tr_slot["duration"] if tr_slot else 90.0
            if entry["jingle"]:
                sim = 0
            else:
                sim += 1
                used.add(entry["key"])
                songs.add(self._song_of(entry["key"]))
                last = entry["key"]

        self.explicit = [e for e in self.explicit if e["key"] in self.cat.tracks]
        for e in self.explicit:
            add({"key": e["key"], "jingle": e["jingle"], "explicit": True})
        self.auto = [k for k in self.auto if self._auto_ok(k)]
        for k in self.auto:
            if len(out) >= QUEUE_LEN:
                break
            add({"key": k, "jingle": False})
        while len(out) < QUEUE_LEN:
            k = self._pick_track(used, last, songs, slot_clock[0])
            if not k:
                break
            self.auto.append(k)
            add({"key": k, "jingle": False})
        cleaned = []
        for e in out:
            prev = cleaned[-1] if cleaned else None
            same_as_last = e["key"] == (prev["key"] if prev else (self.current["key"] if self.current else None))
            if same_as_last and not e["jingle"] and not e.get("explicit") and len(self.cat.tracks) > 1:
                if e["key"] in self.auto:
                    self.auto.remove(e["key"])
                continue
            cleaned.append(e)
        self.upcoming = cleaned

    def _item(self, entry, start, fade_in):
        tr = self.cat.tracks[entry["key"]]
        self.uid += 1
        item = dict(tr)
        item.update({"uid": self.uid, "jingle": entry["jingle"], "start": start, "end": start + tr["duration"],
                     "fade_in": fade_in, "fade_out": 0.0, "explicit": bool(entry.get("explicit"))})
        return item

    def _commit(self, entry):
        if entry["jingle"]:
            self.since_jingle = 0
            self.jingle_seq += 1
            return
        self.since_jingle += 1
        self.history.append(entry["key"])
        keep = int(self.settings().get("no_repeat") or 0)
        self.history = self.history[-keep:] if keep > 0 else []
        self.song_history.append(self._song_of(entry["key"]))
        keep_songs = int(self.settings().get("no_repeat_songs") or 0)
        self.song_history = self.song_history[-keep_songs:] if keep_songs > 0 else []

    def _consume(self, entry):
        if entry.get("explicit"):
            for i, e in enumerate(self.explicit):
                if e["key"] == entry["key"]:
                    del self.explicit[i]
                    break
        elif not entry["jingle"] and entry["key"] in self.auto:
            self.auto.remove(entry["key"])

    def _promote(self, t, forced=False):
        if not self.upcoming:
            return False
        entry = self.upcoming[0]
        if entry["key"] not in self.cat.tracks:
            self._compose()
            return False
        tr = self.cat.tracks[entry["key"]]
        if self.current is None:
            start, fade_in = t, 0.0
        elif forced:
            start, fade_in = t, SKIP_FADE_IN
            self.current["end"] = min(self.current["end"], t + SKIP_FADE_OUT)
            self.current["fade_out"] = SKIP_FADE_OUT
        else:
            start, fout, fade_in = self._transition(self.current, tr["duration"], entry["jingle"])
            self.current["fade_out"] = fout
        item = self._item(entry, start, fade_in)
        self._attach_overlay(item)
        self._consume(entry)
        self._commit(entry)
        self.active.append(item)
        if self.current is not None:
            self.played.append(self.current)
            self.played = self.played[-PLAYED_LEN:]
        self.current = item
        self._compose()
        self.rev += 1
        if self.persist:
            self._save_state()
        return True

    def _attach_overlay(self, item):
        st = self.settings()
        if item["jingle"]:
            item["overlay"] = {"type": "jingle", "n": self.jingle_msg_seq, "start": item["start"], "end": item["end"]}
            self.jingle_msg_seq += 1
            return
        self.since_ad += 1
        every = int(st.get("ads_every") or 0)
        if not st.get("ads_enabled", True) or every <= 0 or self.since_ad < every:
            return
        offset = float(st.get("ad_offset_s", 10))
        length = float(st.get("ad_seconds", 9))
        if item["duration"] < offset + length + 3:
            return
        item["overlay"] = {"type": "ad", "n": self.ad_seq, "start": item["start"] + offset,
                           "end": item["start"] + offset + length}
        self.ad_seq += 1
        self.since_ad = 0

    def tick(self):
        with self.lock:
            t = self.now()
            if t - self._last_refresh >= REFRESH_EVERY_S:
                self._last_refresh = t
                if self.cat.refresh():
                    self._compose()
                    self.rev += 1
            self.active = [it for it in self.active if it["end"] > t]
            if not self.upcoming:
                self._compose()
            if self.current is None:
                if self.upcoming:
                    self._promote(t)
                return
            if self.upcoming:
                entry = self.upcoming[0]
                tr = self.cat.tracks.get(entry["key"])
                if tr is None:
                    self._compose()
                    return
                start, _, _ = self._transition(self.current, tr["duration"], entry["jingle"])
                if t >= start:
                    self._promote(t)

    def _plan(self):
        planned = []
        prev = self.current
        for e in self.upcoming:
            tr = self.cat.tracks.get(e["key"])
            if tr is None or prev is None:
                break
            start, fout, fin = self._transition(prev, tr["duration"], e["jingle"])
            item = dict(tr)
            item.update({"uid": 0, "jingle": e["jingle"], "start": start, "end": start + tr["duration"],
                         "fade_in": fin, "fade_out": 0.0, "explicit": bool(e.get("explicit")),
                         "auto": bool(e.get("auto"))})
            if planned:
                planned[-1]["fade_out"] = fout
            elif self.current is not None:
                pass
            planned.append(item)
            prev = item
        return planned

    def snapshot(self, admin=False):
        with self.lock:
            t = self.now()
            plan = self._plan()
            active = [dict(it) for it in self.active]
            if self.current is not None and plan and self.current["end"] > t:
                _, fout, _ = self._transition(self.current, plan[0]["duration"], plan[0]["jingle"])
                for it in active:
                    if it["uid"] == self.current["uid"]:
                        it["fade_out"] = fout
            st = self.settings()
            out = {"server_time": t, "rev": self.rev, "active": active,
                   "upcoming": plan if admin else plan[:2],
                   "ui": {"visual_transition_s": float(st.get("visual_transition_s", 5))}}
            if admin:
                out["played"] = [dict(p) for p in self.played]
                out["queue"] = [
                    {"index": i, "key": e["key"], "jingle": e["jingle"],
                     "explicit": bool(e.get("explicit")), "auto": bool(e.get("auto"))}
                    for i, e in enumerate(self.upcoming)
                ]
            return out

    def stats(self):
        with self.lock:
            self.cat.refresh()
            groups = self._playable_groups()
            total = sum(self._weight(pl["id"]) for pl, _ in groups) or 1
            out = []
            for pl, keys in groups:
                share = self._weight(pl["id"]) / total
                mult = {k: self._multiplier(k) for k in keys}
                msum = sum(mult.values()) or 1
                out.append({"id": pl["id"], "label": pl["label"], "share": round(share * 100, 2),
                            "tracks": [{"key": k, "share": round(share * mult[k] / msum * 100, 3)} for k in keys]})
            return out

    def energy(self):
        with self.lock:
            self.cat.refresh()
            measured = [t for t in self.cat.tracks.values() if t.get("energy_wh_est") is not None]
            total = sum(t["energy_wh_est"] for t in measured)
            return {"tracks_total": len(self.cat.tracks), "tracks_measured": len(measured),
                    "wh_total": round(total, 2),
                    "wh_per_track_avg": round(total / len(measured), 3) if measured else None,
                    "kind": "estimation",
                    "scope": "estimation de l'énergie du GPU pendant la génération, d'après son taux d'utilisation et sa puissance maximale (115 W) ; hors processeur, ventilation et diffusion ; le GPU n'expose pas sa puissance réelle"}

    def library(self):
        with self.lock:
            self.cat.refresh()
            return [
                {"id": pl["id"], "label": pl["label"], "jingle": pl["jingle"],
                 "tracks": [{"key": k, "name": self.cat.tracks[k]["name"], "duration": self.cat.tracks[k]["duration"]}
                            for k in pl["keys"]]}
                for pl in self.cat.playlists
            ]

    def action(self, name, params):
        with self.lock:
            t = self.now()
            key = params.get("key")
            if name == "skip":
                self._promote(t, forced=True)
            elif name in ("next", "front", "now"):
                tr = self.cat.tracks.get(key)
                if tr is None:
                    return False
                entry = {"key": key, "jingle": tr["jingle"], "explicit": True}
                if name == "next":
                    self.explicit.append(entry)
                else:
                    self.explicit.insert(0, entry)
                self._compose()
                if name == "now":
                    self._promote(t, forced=True)
            elif name == "remove":
                if not self._remove(int(params.get("index", -1))):
                    return False
            elif name in ("move_front", "play_index"):
                idx = int(params.get("index", -1))
                if not 0 <= idx < len(self.upcoming):
                    return False
                entry = dict(self.upcoming[idx])
                if not entry["jingle"] or entry.get("explicit"):
                    self._remove(idx)
                self.explicit.insert(0, {"key": entry["key"], "jingle": entry["jingle"], "explicit": True})
                self._compose()
                if name == "play_index":
                    self._promote(t, forced=True)
            elif name in ("playlist_next", "playlist_front", "playlist_now"):
                pl = next((p for p in self.cat.playlists if p["id"] == params.get("id")), None)
                if pl is None:
                    return False
                excluded = set(self.settings().get("excluded") or [])
                entries = [{"key": k, "jingle": pl["jingle"], "explicit": True} for k in pl["keys"] if k not in excluded]
                if name == "playlist_next":
                    self.explicit.extend(entries)
                else:
                    self.explicit[0:0] = entries
                self._compose()
                if name == "playlist_now":
                    self._promote(t, forced=True)
            else:
                return False
            self._compose()
            self.rev += 1
            if self.persist:
                self._save_state()
            return True

    def _remove(self, index):
        if not 0 <= index < len(self.upcoming):
            return False
        e = self.upcoming[index]
        if e.get("explicit"):
            n = sum(1 for x in self.upcoming[:index] if x.get("explicit"))
            del self.explicit[n]
        elif not e["jingle"]:
            n = sum(1 for x in self.upcoming[:index] if not x["jingle"] and not x.get("explicit"))
            del self.auto[n]
        else:
            return False
        return True

    def run(self, interval=0.25):
        while True:
            try:
                self.tick()
            except Exception as exc:
                print("moteur radio :", exc, flush=True)
            time.sleep(interval)
