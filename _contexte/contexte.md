# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Chatterbox multilingue (CPU, timbre de référence Kokoro) ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
WebRadio IA locale « CréaZik IA WebRadio » : 86 playlists musicales (921 morceaux) et 29 jingles vocaux dans `webradio/jingles/` ; interfaces auditeur/admin séparées (5000/5001) ; 25 tests du moteur passent.
Série de tests de voix ACE-Step « Marie » en cours (`webradio/tests_ace/marie/`, v1 à v9) : autotune net obtenu par caption, timbre de voix encore instable ; écoute via le bouton « Test » de l'UI auditeur.
Worker ACE des v7 à v9 probablement figé (arrêt à valider) ; prononciation « IA » des jingles à valider ; ComfyUI et génération en rotation arrêtés ; batch de pochettes à reprendre.
Contrôles iPhone en attente ; l'UI du port 5000 est l'UI dev (Suivant, Test et dynamique ouverts) : à remplacer par une UI auditeur avant le déploiement.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-06 : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
- 2026-10-06 : Pochettes via ComfyUI-Qwen, lancées quand la file de génération musicale est vide.
- 2026-10-06 : Pochettes avec texte généré par le modèle ; charte par playlist dans webradio/covers_charte.json.
- 2026-10-06 : Interfaces auditeur/admin séparées (ports 5000/5001) ; programmation admin avec recherche par morceau ou playlist.
- 2026-10-06 : Libellés publics sans préfixe « Playlist » ; libellés « Perso » remplacés par des noms descriptifs. Noms d'artistes conservés en développement et à remplacer avant déploiement.
- 2026-10-06 : Base SQLite `radio.db` pour diffusions, « sans avis » et dynamique perçue (fusionnée à l'énergie mesurée) ; statistiques admin avec exports JSON/CSV.
- 2026-10-06 : Suppression = fichiers effacés + archive dans `learning/morceaux_rejetes.jsonl` ; renommage via `catalog_overrides.json` ; score négatif = non diffusé automatiquement.
- 2026-10-06 : Panneau de pub carré cliquable avec mascotte (20 styles) ; jingles instrumentaux supprimés ; morceau en fondu sous le jingle.
- 2026-10-07 : Jingles rangés dans `webradio/jingles/<catégorie>/`, mélangés, 1 s de silence en tête, voix féminine Chatterbox.
- 2026-10-07 : Dynamique : seul l'admin saisit Slow/Medium/High et son choix remplace l'énergie mesurée ; mode dev à un seul utilisateur.
- 2026-10-07 : Tests de voix ACE hors catalogue (`playlists/tests-ace/`, bouton Test) ; BPM/tonalité en paramètres du worker ; un seul changement par version de test.
- 2026-10-07 : L'UI du port 5000 devient l'UI dev ; boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin), à refermer avec l'UI auditeur future.
