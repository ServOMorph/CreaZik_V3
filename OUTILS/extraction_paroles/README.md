# Extraction de paroles depuis des photos

Outil 100 % local (Ollama, aucun envoi hors machine). Relecture humaine obligatoire.

## Usage
```
python OUTILS/extraction_paroles/extraire_paroles.py <image|dossier> --sortie <dossier> [--modele qwen2.5vl]
```
- Un fichier `.md` par texte (une photo peut en contenir plusieurs), jamais écrasé s'il existe.
- En-tête : titre, photo source, modèle, date, `Statut : A_RELIRE`.
- Le texte imprimé seul est transcrit ; les annotations manuscrites (accords, flèches, notes) sont ignorées. « Ref : » devient `[chorus]`.
- Modèle par défaut `qwen2.5vl` (essai du 2026-10-11 : sortie correcte ; `gemma4:12b` a renvoyé une réponse vide). Ollama doit tourner et la VRAM être libre (environ 6 Go).

## Après extraction
Relire chaque fichier contre la photo (accents, ponctuation, lignes manquantes, mots manuscrits restés dans le texte), corriger, puis demander le passage du statut à `RELU`. Un texte non `RELU` n'entre pas dans le run.

## Test
`python -m pytest OUTILS/extraction_paroles/test_extraire_paroles.py`
