import argparse
import datetime
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from annonce import synthesize, finalize, MODEL, WEB


def results_path(categorie):
    if not categorie or categorie == "annonces" or "/" in categorie or "\\" in categorie or categorie in (".", ".."):
        sys.exit(f"catégorie invalide : {categorie!r} (dossier attendu sous jingles/, hors annonces)")
    path = WEB / "jingles" / categorie / "outputs" / "playlist_results.json"
    if not path.exists():
        sys.exit(f"catégorie invalide : {categorie!r} (fichier absent : {path})")
    return path


def register(results, categorie, spoken, display, duration, n):
    data = json.loads(results.read_text(encoding="utf-8"))
    libelle = data.get("playlist", categorie)
    label = libelle[7:] if libelle.startswith("Jingles ") else libelle
    data.setdefault("model", MODEL)
    data.setdefault("generations", []).append({
        "test_case_id": str(n), "name": f"Jingle {label} {n:02d}", "prompt": display, "spoken": spoken,
        "type": "voice", "duration": round(duration, 1),
        "output_file": f"jingles/{categorie}/outputs/{n:02d}_voix.wav", "status": "generated",
        "generated_at": datetime.datetime.now().astimezone().isoformat(), "model": MODEL})
    tmp = results.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, results)


def main():
    p = argparse.ArgumentParser(description="Génère un jingle parlé dans une catégorie de rotation, sans diffusion.")
    p.add_argument("categorie", help="Catégorie de rotation (dossier sous jingles/, hors annonces)")
    p.add_argument("texte", help="Texte prononcé (graphie phonétique possible)")
    p.add_argument("--affiche", default=None, help="Texte affiché (par défaut, le texte prononcé)")
    a = p.parse_args()

    results = results_path(a.categorie)
    data = json.loads(results.read_text(encoding="utf-8"))
    existing = data.get("generations", [])
    n = max([int(g["test_case_id"]) for g in existing] + [0]) + 1
    out = results.parent
    out.mkdir(parents=True, exist_ok=True)
    mp3 = out / f"{n:02d}_voix.mp3"
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        wav = Path(tmpdir) / "voix.wav"
        synthesize(a.texte, wav)
        duration = finalize(wav, mp3)
    (out / f"{n:02d}_voix.wav.feat.json").write_text(json.dumps({"duration_s": duration}), encoding="utf-8")
    register(results, a.categorie, a.texte, a.affiche or a.texte, duration, n)
    print(f"jingle jingles-{a.categorie}:{n:02d} : {duration:.1f} s, généré en {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
