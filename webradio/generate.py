import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("config", help="chemin de playlists/<id>/config.json")
parser.add_argument("--only", default="", help="ids séparés par des virgules, ex: 1,2")
parser.add_argument("--lm", action="store_true", help="active le LM 0.6B (plus lent, plus de VRAM)")
parser.add_argument("--steps", type=int, default=8)
args = parser.parse_args()

with open(args.config, "r", encoding="utf-8") as f:
    ace = Path(json.load(f)["ace_step_path"])

py = ace / ".venv" / "Scripts" / "python.exe"
if not py.exists():
    sys.exit(f"Python du venv ACE-Step introuvable : {py}")

cmd = [str(py), str(HERE / "ace_worker.py"), "--config", args.config,
       "--only", args.only, "--steps", str(args.steps)]
if args.lm:
    cmd.append("--lm")
sys.exit(subprocess.call(cmd))
