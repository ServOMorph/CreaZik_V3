"""Extraction locale de paroles imprimees depuis des photos (Ollama, modele vision).

Usage : python extraire_paroles.py <image|dossier> --sortie <dossier> [--modele qwen2.5vl]
Un fichier .md par texte, statut A_RELIRE. Relecture humaine obligatoire.
"""
import argparse
import base64
import io
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

OLLAMA = "http://127.0.0.1:11434/api/generate"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_COTE = 1600

CONSIGNE = """Tu transcris le TEXTE IMPRIME de cette photo, sans rien corriger ni reformuler.
Regles strictes :
- Recopie uniquement le texte imprime (caracteres d'imprimerie). IGNORE toute ecriture manuscrite : accords, notes de musique, fleches, symboles, mots ajoutes au stylo ou au crayon.
- La photo peut contenir plusieurs textes. Commence chaque texte par une ligne exacte : ### TITRE : <titre imprime du texte>
- Recopie les lignes dans l'ordre, une ligne par ligne imprimee, en conservant orthographe, ponctuation et majuscules tels qu'ils sont imprimes.
- Laisse une ligne vide entre deux strophes (blocs separes par un espace vertical).
- Le mot imprime "Ref :" ou "Refrain :" est conserve tel quel sur sa propre ligne.
- N'ajoute aucun commentaire, aucune explication."""


def preparer_image(chemin: Path) -> str:
    img = ImageOps.exif_transpose(Image.open(chemin)).convert("RGB")
    img.thumbnail((MAX_COTE, MAX_COTE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def interroger(modele: str, image_b64: str, delai: int) -> str:
    corps = json.dumps({
        "model": modele,
        "prompt": CONSIGNE,
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0, "num_ctx": 8192},
    }).encode()
    req = urllib.request.Request(OLLAMA, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=delai) as r:
        return json.loads(r.read())["response"]


def decouper(reponse: str):
    morceaux = re.split(r"^###\s*(?:TITRE\s*:\s*)?", reponse, flags=re.M)
    textes = []
    for bloc in morceaux[1:]:
        lignes = bloc.strip().splitlines()
        if not lignes:
            continue
        titre = lignes[0].strip().strip("*# ")
        corps = "\n".join(l.rstrip() for l in lignes[1:]).strip()
        corps = re.sub(r"^```\w*\n?|```$", "", corps).strip()
        corps = re.sub(r"^(Ref|Refrain)\s*:?\s*$", "[chorus]", corps, flags=re.M | re.I)
        corps = re.sub(r"\n{3,}", "\n\n", corps)
        textes.append((titre, corps))
    return textes


def slug(titre: str) -> str:
    s = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "texte"


def ecrire(sortie: Path, titre: str, corps: str, photo: Path, modele: str) -> Path:
    sortie.mkdir(parents=True, exist_ok=True)
    chemin = sortie / f"{slug(titre)}.md"
    if chemin.exists():
        raise FileExistsError(f"{chemin} existe deja (jamais ecrase)")
    entete = (
        f"# {titre}\n\n"
        f"- Photo source : {photo.name}\n"
        f"- Modele d'extraction : {modele}\n"
        f"- Date d'extraction : {datetime.now().strftime('%Y-%m-%d')}\n"
        f"- Statut : A_RELIRE\n\n---\n\n"
    )
    chemin.write_text(entete + corps + "\n", encoding="utf-8", newline="\n")
    return chemin


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("--sortie", required=True)
    p.add_argument("--modele", default="qwen2.5vl")
    p.add_argument("--delai", type=int, default=600)
    a = p.parse_args()
    src = Path(a.source)
    photos = sorted(x for x in src.iterdir() if x.suffix.lower() in EXTENSIONS) if src.is_dir() else [src]
    if not photos:
        sys.exit("aucune image")
    for photo in photos:
        try:
            reponse = interroger(a.modele, preparer_image(photo), a.delai)
        except Exception as e:
            print(f"ECHEC {photo.name} : {e}")
            continue
        textes = decouper(reponse)
        if not textes:
            print(f"ECHEC {photo.name} : aucun titre detecte")
            continue
        for titre, corps in textes:
            try:
                print(f"{photo.name} -> {ecrire(Path(a.sortie), titre, corps, photo, a.modele)}")
            except FileExistsError as e:
                print(f"IGNORE {e}")


if __name__ == "__main__":
    main()
