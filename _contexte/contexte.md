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
Tests de voix ACE-Step « Marie » v1 à v9 générés (`webradio/tests_ace/marie/`) : v7 à v9 (seeds) à écouter via le bouton « Test » ; timbre de voix encore instable.
Batch de pochettes en cours dans un terminal cmd de l'utilisateur (reprise automatique) ; prononciation « IA » des jingles à valider ; génération en rotation arrêtée.
Travail réparti en deux agents de zone (`textes` pour les paroles françaises, `modeles_llm` pour les autres modèles musicaux) ; légende animée du visuel validée sur iPhone.
Déploiement : solution VPS Linux notée (ARCHITECTURE_WEBRADIO.md 8.3 bis), non réalisée ; l'UI du port 5000 reste l'UI dev (Suivant, Test et dynamique ouverts) à remplacer avant mise en ligne ; contrôles iPhone en attente.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-06 : Interfaces auditeur/admin séparées (ports 5000/5001) ; programmation admin avec recherche par morceau ou playlist.
- 2026-10-06 : Libellés publics sans préfixe « Playlist » ; libellés « Perso » remplacés par des noms descriptifs. Noms d'artistes conservés en développement et à remplacer avant déploiement.
- 2026-10-06 : Base SQLite `radio.db` pour diffusions, « sans avis » et dynamique perçue (fusionnée à l'énergie mesurée) ; statistiques admin avec exports JSON/CSV.
- 2026-10-06 : Suppression = fichiers effacés + archive dans `learning/morceaux_rejetes.jsonl` ; renommage via `catalog_overrides.json` ; score négatif = non diffusé automatiquement.
- 2026-10-06 : Panneau de pub carré cliquable avec mascotte (20 styles) ; jingles instrumentaux supprimés ; morceau en fondu sous le jingle.
- 2026-10-07 : Jingles rangés dans `webradio/jingles/<catégorie>/`, mélangés, 1 s de silence en tête, voix féminine Chatterbox.
- 2026-10-07 : Dynamique : seul l'admin saisit Slow/Medium/High et son choix remplace l'énergie mesurée ; mode dev à un seul utilisateur.
- 2026-10-07 : Tests de voix ACE hors catalogue (`playlists/tests-ace/`, bouton Test) ; BPM/tonalité en paramètres du worker ; un seul changement par version de test.
- 2026-10-07 : L'UI du port 5000 devient l'UI dev ; boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin), à refermer avec l'UI auditeur future.
- 2026-10-08 : Mise en ligne prévue sur VPS Linux bon marché (systemd, HTTPS, sous-domaine du site) ; Vercel, Render gratuit et Netlify écartés ; pas encore réalisée.
- 2026-10-08 : Deux agents de zone (`textes`, `modeles_llm`) pour travailler en parallèle ; nom d'artiste en consigne de style interne seulement, jamais public.
