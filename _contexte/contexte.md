# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Kokoro-82M ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
WebRadio IA locale en direct « CréaZik IA WebRadio » (89 playlists configurées dont 11 « Esprit », génération en rotation).
Bug du clic admin corrigé (confirmé), 19 tests passent ; jingles vocaux régénérés avec le nom de la radio.
Tout arrêté (/stop) ; relance par run.py. Pochettes : style avec texte validé, charte graphique par playlist écrite, 3 exemples à générer. Contrôles iPhone en attente.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-05 : Initialisation du protocole vibecoding.
- 2026-10-06 : Le projet devient une WebRadio IA locale ; règles consignées dans webradio/REGLES_GENERATION_DEV.md (chargé par /start, mis à jour par /close).
- 2026-10-06 : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
- 2026-10-06 : Pochettes via ComfyUI-Qwen, lancées quand la file de génération musicale est vide.
- 2026-10-06 : Pochettes avec texte généré par le modèle ; charte par playlist dans webradio/covers_charte.json.
