"""Met à jour TEXTES/liste_attente.md : changement de statut, ajout d'un texte, journal."""

import argparse
import datetime
import re
import sys
from pathlib import Path

LISTE = Path(__file__).resolve().parent.parent / "liste_attente.md"
STATUTS = ["A_PREPARER", "PRET", "EN_GENERATION", "GENERE", "VALIDE", "REJETE", "BLOQUE_DROITS"]


def clean(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def read() -> list[str]:
    return LISTE.read_text(encoding="utf-8").split("\n")


def write(lines: list[str]) -> None:
    LISTE.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def row_index(lines: list[str], text_id: str) -> int:
    for i, line in enumerate(lines):
        if line.startswith(f"| {text_id} |"):
            return i
    sys.exit(f"ERREUR: identifiant introuvable : {text_id}")


def append_journal(lines: list[str], entry: str) -> None:
    while lines and lines[-1] == "":
        lines.pop()
    lines.append(f"- {datetime.date.today().isoformat()} : {entry}")
    lines.append("")


def cmd_set(args: argparse.Namespace) -> None:
    lines = read()
    i = row_index(lines, args.id)
    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    if len(cells) != 8:
        sys.exit(f"ERREUR: ligne {args.id} mal formée ({len(cells)} colonnes)")
    if args.statut:
        cells[5] = args.statut
    if args.note:
        cells[7] = clean(args.note)
    cells[6] = datetime.date.today().isoformat()
    lines[i] = "| " + " | ".join(cells) + " |"
    append_journal(lines, f"{args.id} -> {cells[5]}" + (f" ({clean(args.note)})" if args.note else ""))
    write(lines)
    print(lines[i])


def cmd_add(args: argparse.Namespace) -> None:
    lines = read()
    ids = [int(m.group(1)) for line in lines if (m := re.match(r"\| T(\d+) \|", line))]
    new_id = f"T{(max(ids) if ids else 0) + 1:02d}"
    last = max(i for i, line in enumerate(lines) if re.match(r"\| T\d+ \|", line))
    row = [
        new_id,
        clean(args.titre),
        clean(args.auteur or "(non fourni)"),
        clean(args.fichier or "(à créer)"),
        clean(args.droits or "(non précisé)"),
        args.statut,
        datetime.date.today().isoformat(),
        clean(args.note or ""),
    ]
    lines.insert(last + 1, "| " + " | ".join(row) + " |")
    append_journal(lines, f"ajout de {new_id} ({clean(args.titre)})")
    write(lines)
    print(lines[last + 1])


def cmd_log(args: argparse.Namespace) -> None:
    lines = read()
    append_journal(lines, clean(args.message))
    write(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="changer le statut et/ou la note d'un texte")
    p_set.add_argument("id")
    p_set.add_argument("--statut", choices=STATUTS)
    p_set.add_argument("--note", help="résultat ou remarque (ex. chemin du mp3)")
    p_set.set_defaults(func=cmd_set)

    p_add = sub.add_parser("add", help="ajouter un texte")
    p_add.add_argument("--titre", required=True)
    p_add.add_argument("--auteur")
    p_add.add_argument("--fichier")
    p_add.add_argument("--droits")
    p_add.add_argument("--statut", choices=STATUTS, default="A_PREPARER")
    p_add.add_argument("--note")
    p_add.set_defaults(func=cmd_add)

    p_log = sub.add_parser("log", help="ajouter une ligne au journal")
    p_log.add_argument("message")
    p_log.set_defaults(func=cmd_log)

    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    args.func(args)


if __name__ == "__main__":
    main()
