"""Compare preferences.json (valide) et preferences.proposition.json ; --appliquer apres accord de l'utilisateur."""
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
IGNORES = {"calcule_le"}


def aplatir(obj, prefixe=""):
    plat = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            plat.update(aplatir(v, f"{prefixe}{k}."))
    elif isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        cle = next((c for c in ("terme", "famille", "type") if c in obj[0]), None)
        for i, x in enumerate(obj):
            plat.update(aplatir(x, f"{prefixe}{x[cle] if cle else i}."))
    else:
        plat[prefixe.rstrip(".")] = obj
    return plat


def differences(ancien, nouveau):
    a, b = aplatir(ancien or {}), aplatir(nouveau)
    lignes = []
    for k in sorted(set(a) | set(b)):
        if k.split(".")[0] in IGNORES:
            continue
        if k not in a:
            lignes.append(f"+ {k} = {b[k]}")
        elif k not in b:
            lignes.append(f"- {k} (etait {a[k]})")
        elif a[k] != b[k]:
            lignes.append(f"~ {k} : {a[k]} -> {b[k]}")
    return lignes


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--racine", default=str(RACINE))
    p.add_argument("--appliquer", action="store_true")
    a = p.parse_args()
    dossier = Path(a.racine) / "DOCUMENTATION" / "apprentissage"
    valide, prop = dossier / "preferences.json", dossier / "preferences.proposition.json"
    if not prop.exists():
        print("Aucune proposition : lancer calculer_preferences.py d'abord.")
        sys.exit(1)
    nouveau = json.loads(prop.read_text(encoding="utf-8"))
    ancien = json.loads(valide.read_text(encoding="utf-8")) if valide.exists() else None
    lignes = differences(ancien, nouveau)
    if not lignes:
        print("Aucune difference.")
        return
    print(f"{len(lignes)} difference(s)" + (" (premier calcul, aucun fichier valide)" if ancien is None else ""))
    for l in lignes[:200]:
        print(l)
    if len(lignes) > 200:
        print(f"... {len(lignes) - 200} autres")
    if a.appliquer:
        if ancien is not None:
            hist = dossier / "historique"
            hist.mkdir(exist_ok=True)
            shutil.copyfile(valide, hist / f"preferences_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json")
        shutil.copyfile(prop, valide)
        print("preferences.json mis a jour.")
    else:
        print("Rien d'applique. Relancer avec --appliquer apres accord de l'utilisateur.")


if __name__ == "__main__":
    main()
