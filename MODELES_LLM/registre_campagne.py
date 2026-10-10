import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "MODELES_LLM"
CAMPAIGN = ZONE / "configs" / "campagne_40.json"
MASTER = ZONE / "sorties" / "campagne_2026-10-09"
UI_OUT = ROOT / "webradio" / "playlists" / "tests-modeles" / "outputs"
UI_RESULTS = UI_OUT / "playlist_results.json"
MANIFEST = MASTER / "generation_manifest.json"
FFMPEG = Path(r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe")
FFPROBE = FFMPEG.with_name("ffprobe.exe")
MODEL_CODES = {
    "ace": ("ACE", "ACE-Step 1.5"),
    "heartmula": ("HM3", "HeartMuLa OSS 3B"),
    "musicgen": ("MG", "MusicGen Small"),
    "stable_audio": ("SA3", "Stable Audio 3 Small-Music"),
}

FOLDER_LABELS = {
    "ace": "ACE-Step 1.5 · Comparatif 2026-10-09 · Styles variés",
    "heartmula": "HeartMuLa OSS 3B · Comparatif 2026-10-09 · Styles variés",
    "musicgen": "MusicGen Small · Comparatif 2026-10-09 · Styles variés",
    "stable_audio": "Stable Audio 3 Small-Music · Comparatif 2026-10-09 · Styles variés",
}


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def track_name(model, case):
    code = MODEL_CODES[model][0]
    slug = re.sub(r"[^a-z0-9-]+", "-", case["slug"].lower()).strip("-")
    return f"{code}_{case['id']}_{slug}"


def initialize():
    data = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    MASTER.mkdir(parents=True, exist_ok=True)
    UI_OUT.mkdir(parents=True, exist_ok=True)
    manifest = read_json(MANIFEST, {
        "campaign_id": data["campaign_id"], "created_at": datetime.now(ZoneInfo("Europe/Paris")).isoformat(),
        "duration_seconds": data["duration_seconds"], "models": {}, "tracks": []
    })
    existing = {(t["model_key"], t["test_case_id"]) for t in manifest["tracks"]}
    for key, (_, label) in MODEL_CODES.items():
        manifest["models"][key] = {"name": label}
        for case in data["cases"]:
            if (key, case["id"]) not in existing:
                manifest["tracks"].append({
                    "model_key": key, "model_name": label, "test_case_id": case["id"],
                    "title": case["title"], "filename": track_name(key, case) + ".mp3",
                    "status": "pending", "listening_review": {"status": "pending"}
                })
    write_json(MANIFEST, manifest)
    write_json(UI_RESULTS, {"campaign_id": data["campaign_id"], "generations": read_json(UI_RESULTS, {}).get("generations", [])})
    print(f"Campagne prête : {len(manifest['tracks'])} entrées.")


def begin(model, case_id, metadata_path):
    if model not in MODEL_CODES:
        raise ValueError("Modèle inconnu")
    data = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    case = next(c for c in data["cases"] if c["id"] == str(case_id).zfill(2))
    now = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    details = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    details["started_at"] = now
    write_json(Path(metadata_path), details)
    manifest = read_json(MANIFEST, {"tracks": []})
    for track in manifest["tracks"]:
        if track["model_key"] == model and track["test_case_id"] == case["id"]:
            track.update({"status": "running", "started_at": now, "attempt": details})
            break
    write_json(MANIFEST, manifest)


def probe_audio(path):
    proc = subprocess.run([str(FFPROBE), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                          capture_output=True, text=True, check=True)
    result = json.loads(proc.stdout)
    stream = next(s for s in result["streams"] if s.get("codec_type") == "audio")
    return result, stream


def finalize(model, case_id, raw_path, metadata_path):
    if model not in MODEL_CODES:
        raise ValueError("Modèle inconnu")
    raw = Path(raw_path).resolve()
    master_root = MASTER.resolve()
    if master_root not in raw.parents or raw.suffix.lower() not in (".wav", ".mp3", ".flac"):
        raise ValueError("Le fichier source doit être un audio de la campagne sous MODELES_LLM/sorties.")
    data = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    case = next(c for c in data["cases"] if c["id"] == str(case_id).zfill(2))
    code, label = MODEL_CODES[model]
    base = track_name(model, case)
    master_mp3 = MASTER / f"{base}.mp3"
    ui_mp3 = UI_OUT / f"{base}.mp3"
    sidecar = MASTER / f"{base}.metadata.json"
    details = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    started_at = details.get("started_at", details.get("generated_at"))
    now = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    error = None
    try:
        subprocess.run([str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                        "-vn", "-ac", "2", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", str(master_mp3)],
                       capture_output=True, text=True, check=True)
        result, stream = probe_audio(master_mp3)
        check = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(master_mp3), "-af", "volumedetect,silencedetect=n=-45dB:d=1",
                                "-f", "null", "NUL"], capture_output=True, text=True)
        log = check.stderr
        import re as regex
        mean = regex.search(r"mean_volume:\s*(-?inf|-?[\d.]+) dB", log)
        peak = regex.search(r"max_volume:\s*(-?inf|-?[\d.]+) dB", log)
        duration = float(result["format"].get("duration", 0))
        mean_db = float(mean.group(1)) if mean and mean.group(1) != "-inf" else -120.0
        peak_db = float(peak.group(1)) if peak and peak.group(1) != "-inf" else -120.0
        failures = []
        if check.returncode != 0:
            failures.append("décodage ffmpeg en échec")
        if not 20 <= duration <= 35:
            failures.append(f"durée hors plage (20–35 s): {duration:.2f} s")
        if mean_db < -45:
            failures.append(f"niveau moyen trop faible: {mean_db:.1f} dB")
        if peak_db >= -0.05:
            failures.append(f"écrêtage probable: crête {peak_db:.2f} dB")
        analysis = {"technical_status": "invalid" if failures else "pass_needs_listening", "failures": failures,
                    "duration_seconds": round(duration, 3), "sample_rate": int(stream.get("sample_rate", 0)),
                    "channels": int(stream.get("channels", 0)), "codec": stream.get("codec_name"),
                    "mean_volume_db": mean_db, "peak_volume_db": peak_db,
                    "silence_detected": "silence_end:" in log}
        import shutil
        shutil.copy2(master_mp3, ui_mp3)
        digest = hashlib.sha256(master_mp3.read_bytes()).hexdigest()
        sidecar_data = {
            "generated_at": now, "generation_started_at": started_at, "model_name": label, "model_key": model,
            "model_version": details.get("model_version", "non spécifiée"),
            "model_revision": details.get("model_revision", "non spécifiée"),
            "runtime": details.get("runtime", {}), "test_case_id": case["id"], "title": case["title"],
            "prompt": details.get("prompt", ""), "lyrics": details.get("lyrics"), "tags": details.get("tags"),
            "input_files": details.get("input_files", []), "generation_config": details.get("generation_config", {}),
            "output": {"master_path": str(master_mp3), "ui_path": str(ui_mp3.relative_to(ROOT / "webradio")).replace("\\", "/"),
                       "format": "mp3", "bitrate": "192k", "duration_seconds": analysis["duration_seconds"],
                       "size_bytes": master_mp3.stat().st_size, "sha256": digest},
            "analysis": analysis, "listening_review": {"status": "pending"}, "attempt_error": error
        }
        write_json(sidecar, sidecar_data)
        results = read_json(UI_RESULTS, {"generations": []})
        items = [g for g in results.get("generations", []) if g.get("output_file") != sidecar_data["output"]["ui_path"]]
        items.append({"name": case["title"], "output_file": sidecar_data["output"]["ui_path"], "status": "generated",
                      "generated_at": now, "model": label, "prompt": sidecar_data["prompt"],
                      "duration": analysis["duration_seconds"], "technical_status": analysis["technical_status"],
                      "folder": FOLDER_LABELS[model],
                      "metadata_file": str((UI_OUT / f"{base}.metadata.json").relative_to(ROOT / "webradio")).replace("\\", "/")})
        results["generations"] = items
        write_json(UI_RESULTS, results)
        import shutil
        write_json(UI_OUT / f"{base}.metadata.json", sidecar_data)
        manifest = read_json(MANIFEST, {"tracks": []})
        for track in manifest["tracks"]:
            if track["model_key"] == model and track["test_case_id"] == case["id"]:
                track.update({"status": analysis["technical_status"], "generated_at": now,
                              "path": str(master_mp3), "sidecar": str(sidecar), "sha256": digest,
                              "error": failures or None})
                break
        write_json(MANIFEST, manifest)
        raw.unlink(missing_ok=True)
        print(f"{label} / {case['id']} : {analysis['technical_status']} ({duration:.1f} s)")
    except Exception as exc:
        error = str(exc)
        failed_attempt = {
            "generated_at": now, "generation_started_at": started_at, "model_name": label, "model_key": model,
            "model_version": details.get("model_version", "non spécifiée"),
            "model_revision": details.get("model_revision", "non spécifiée"),
            "runtime": details.get("runtime", {}), "test_case_id": case["id"], "title": case["title"],
            "prompt": details.get("prompt", ""), "lyrics": details.get("lyrics"), "tags": details.get("tags"),
            "input_files": details.get("input_files", []), "generation_config": details.get("generation_config", {}),
            "output": {"attempt_file": str(raw)}, "analysis": {"technical_status": "not_generated"},
            "listening_review": {"status": "pending"}, "generation_error": error
        }
        write_json(sidecar, failed_attempt)
        manifest = read_json(MANIFEST, {"tracks": []})
        for track in manifest["tracks"]:
            if track["model_key"] == model and track["test_case_id"] == str(case_id).zfill(2):
                track.update({"status": "failed", "generated_at": now, "error": error})
                break
        write_json(MANIFEST, manifest)
        print(f"{label} / {case_id} : échec technique — {error}")
        raise


parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="command", required=True)
sub.add_parser("init")
beg = sub.add_parser("begin")
beg.add_argument("model", choices=MODEL_CODES)
beg.add_argument("case_id")
beg.add_argument("metadata")
fin = sub.add_parser("finalize")
fin.add_argument("model", choices=MODEL_CODES)
fin.add_argument("case_id")
fin.add_argument("raw")
fin.add_argument("metadata")
args = parser.parse_args()
if args.command == "init":
    initialize()
elif args.command == "begin":
    begin(args.model, args.case_id, args.metadata)
else:
    finalize(args.model, args.case_id, args.raw, args.metadata)
