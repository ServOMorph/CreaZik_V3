"""Génère des paroles balisées pour ACE-Step 1.5 avec un LLM Ollama local (gemma4:12b par défaut)."""

import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma4:12b"
OUT_DIR = Path(__file__).resolve().parent.parent

SYSTEM_PROMPT = """Tu es parolier. Tu écris des paroles de chansons en français destinées à un modèle de génération musicale (ACE-Step 1.5).

Format de sortie obligatoire : uniquement les paroles, sans titre, sans commentaire, sans markdown, sans bloc de code.

Structure :
- Chaque section commence par une balise sur sa propre ligne : [intro], [verse], [pre-chorus], [chorus], [bridge], [outro]. Un descripteur d'un seul mot est permis après un tiret (ex. [chorus - intense]). Jamais de balise vide.
- Une ligne vide entre les sections.
- Le refrain [chorus] est identique chaque fois qu'il revient.

Écriture :
- Lignes de 6 à 10 syllabes, longueur voisine pour les lignes de même rang. Jamais plus de 12 syllabes.
- Une seule métaphore filée par chanson ; pas d'empilement d'adjectifs.
- Images concrètes plutôt qu'abstractions ; éviter les clichés (coeur/douleur, feu/amour, ciel/éternel) et les rimes pauvres.
- Rimes variées, naturelles, sans contorsion de syntaxe ; orthographe française correcte avec accents.
- Textes originaux : ne jamais recopier ni paraphraser de près des paroles existantes. Un nom d'artiste donné comme style est une consigne interne : ne jamais le citer dans le texte.
- Majuscules uniquement pour marquer une intensité voulue ; parenthèses pour chœurs ou échos."""


def sections_for(duration: int) -> str:
    if duration <= 60:
        return "1 couplet, 1 refrain, 1 outro court"
    if duration <= 100:
        return "2 couplets, 2 refrains, 1 outro court"
    return "2 couplets, 1 pont, 2 à 3 refrains, 1 outro"


def build_user_prompt(args: argparse.Namespace) -> str:
    lines = [f"Thème : {args.theme}"]
    if args.style:
        lines.append(f"Style musical : {args.style}")
    if args.ton:
        lines.append(f"Ton et point de vue : {args.ton}")
    if args.notes:
        lines.append(f"Consignes supplémentaires : {args.notes}")
    lines.append(f"Durée visée du morceau : {args.duree} s")
    lines.append(f"Structure attendue : {sections_for(args.duree)}")
    lines.append("Écris les paroles maintenant.")
    return "\n".join(lines)


def call_ollama(model: str, system: str, user: str, temperature: float, timeout: int) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "think": False,
            "keep_alive": 0,
            "options": {"temperature": temperature, "num_ctx": 8192},
        }
    ).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            detail = json.loads(body).get("error", body)
        except json.JSONDecodeError:
            detail = body
        sys.exit(f"ERREUR Ollama (HTTP {error.code}): {detail}")
    except urllib.error.URLError as error:
        sys.exit(f"ERREUR: connexion à Ollama impossible: {error.reason}")
    except TimeoutError:
        sys.exit("ERREUR: délai d'attente Ollama dépassé")
    content = (data.get("message") or {}).get("content", "") if isinstance(data, dict) else ""
    if not content.strip():
        sys.exit("ERREUR: réponse vide du modèle")
    return content


def clean(text: str) -> str:
    text = re.sub(r"```[a-z]*", "", text).replace("```", "")
    text = re.sub(r"^\s*#+\s.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\[[^\]\n]+\][ \t]*\n(?=\s*(?:\[|\Z))", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:50] or "texte"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", required=True, help="thème ou histoire de la chanson")
    parser.add_argument("--style", default="", help="style musical (consigne interne)")
    parser.add_argument("--ton", default="", help="ton et point de vue")
    parser.add_argument("--notes", default="", help="consignes supplémentaires")
    parser.add_argument("--duree", type=int, default=90, help="durée visée en secondes (défaut 90)")
    parser.add_argument("--nom", default="", help="nom du fichier de sortie (sans extension)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    raw = call_ollama(args.model, SYSTEM_PROMPT, build_user_prompt(args), args.temperature, args.timeout)
    lyrics = clean(raw)

    stem = slugify(args.nom or args.theme)
    out_path = OUT_DIR / f"{stem}.md"
    counter = 2
    while out_path.exists():
        out_path = OUT_DIR / f"{stem}-{counter}.md"
        counter += 1
    out_path.write_text(lyrics, encoding="utf-8", newline="\n")
    print(f"Fichier : {out_path}")
    print(f"Modèle : {args.model}")
    print("---")
    sys.stdout.buffer.write(lyrics.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
