# Changelog

## v0.3 — 2026-10-06

### Ajouté
- `run.py` (lance serveur, analyse, compression, génération et ouvre l'UI) et commande `/stop` (arrêt de tout, VRAM libérée).

### Corrigé
- `services.ps1 stop` arrête aussi `run_rotation.py`.

## v0.2 — 2026-10-06

### Ajouté
- 11 playlists « Esprit » et blues (génération en rotation), `run.py` à la racine.
- Charte graphique par playlist (`webradio/covers_charte.json`, `tools/cover_gen.py`).

### Modifié
- Nom de la radio « CréaZik IA WebRadio » (UI et jingles vocaux, régénérés).
- Mise en queue sans couper (▶, « Lire »), Programmation lisible, noms de playlists sans « Playlist », bandeau « Aperçu auditeur » retiré.

## v0.1 — 2026-10-06

### Ajouté
- Dynamique de la journée (réglages, courbe, tests) et arc visuel narratif par morceau.
- Mode auditeur : texte et bandeau vers Traveling Sound Web Radio.
- Règles de génération et de développement (`webradio/REGLES_GENERATION_DEV.md`), branchées sur `/start` et `/close`.
- Test de pochette avec ComfyUI-Qwen (`webradio/tools/cover_test.py`).

### Modifié
- Audio : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
