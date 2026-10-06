# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Kokoro-82M ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
WebRadio IA locale en direct « CréaZik IA WebRadio » : 88 entrées au catalogue, 86 identifiants en rotation ; interfaces auditeur/admin séparées sur les ports 5000/5001.
Programmation admin restaurée avec recherche de titres/playlists ; les 88 libellés n'affichent plus « Playlist » ni « Perso » ; 19 tests du moteur passent.
Batch pochettes interrompu à la demande : 107 créées sur 950 tâches initiales, 804 manquantes au dernier statut, 26 exclues pour score négatif ; reprise via `/generate_covers`.
Tous les services WebRadio et ComfyUI sont arrêtés ; VRAM à 1714 MiB au dernier contrôle. Redémarrage radio via `python run.py`.
Contrôles iPhone/jingles en attente ; noms d'artistes maintenus pendant le développement, à remplacer avant déploiement.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-05 : Initialisation du protocole vibecoding.
- 2026-10-06 : Le projet devient une WebRadio IA locale ; règles consignées dans webradio/REGLES_GENERATION_DEV.md (chargé par /start, mis à jour par /close).
- 2026-10-06 : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
- 2026-10-06 : Pochettes via ComfyUI-Qwen, lancées quand la file de génération musicale est vide.
- 2026-10-06 : Pochettes avec texte généré par le modèle ; charte par playlist dans webradio/covers_charte.json.
- 2026-10-06 : Interfaces auditeur/admin séparées (ports 5000/5001) ; programmation admin avec recherche par morceau ou playlist.
- 2026-10-06 : Libellés publics sans préfixe « Playlist » ; libellés « Perso » remplacés par des noms descriptifs. Noms d'artistes conservés en développement et à remplacer avant déploiement.
