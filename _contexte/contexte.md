# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Chatterbox multilingue (CPU, timbre de référence Kokoro) ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
WebRadio IA locale : 86 playlists musicales (921 morceaux au 2026-10-08) et 29 jingles actifs ; interfaces auditeur/admin (5000/5001), UI du port 5000 = UI dev ; 27 tests du moteur (dernier passage 2026-10-08).
Section « Tests » de l'UI admin (versions numérotées, pouces, suppression, barre de position, badge « Jamais écouté »), police Sora, titre et date sur la pochette, graine ACE désormais appliquée, contrôle de paroles `TEXTES/tools/check_lyrics.py`.
Démo T01 « Arroser Les Roses » : version 18 retenue (voix d'homme) ; voix de femme instable, grille à écouter (tests 26 à 31 et 39 à 44) ; accord de l'auteur non demandé, démo privée.
Pochettes : lot terminé (175 créées, 594 fichiers au total, 256 morceaux exclus pour score négatif). Génération musicale, analyse et compression arrêtées ; serveur actif (redémarré le 2026-10-09).
Avant déploiement : `DEV_UNIFIED`, boutons Suivant/Test, section Tests, noms d'artistes ; VPS Linux non réalisé ; contrôles iPhone en attente (`tests_manuels.md`).

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-06 : Panneau de pub carré cliquable avec mascotte (20 styles) ; jingles instrumentaux supprimés ; morceau en fondu sous le jingle.
- 2026-10-07 : Jingles rangés dans `webradio/jingles/<catégorie>/`, mélangés, 1 s de silence en tête, voix féminine Chatterbox.
- 2026-10-07 : Dynamique : seul l'admin saisit Slow/Medium/High et son choix remplace l'énergie mesurée ; mode dev à un seul utilisateur.
- 2026-10-07 : Tests de voix ACE hors catalogue (`playlists/tests-ace/`, bouton Test) ; BPM/tonalité en paramètres du worker ; un seul changement par version de test.
- 2026-10-07 : L'UI du port 5000 devient l'UI dev ; boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin), à refermer avec l'UI auditeur future.
- 2026-10-08 : Mise en ligne prévue sur VPS Linux bon marché (systemd, HTTPS, sous-domaine du site) ; Vercel, Render gratuit et Netlify écartés ; pas encore réalisée.
- 2026-10-08 : Deux agents de zone (`textes`, `modeles_llm`) pour travailler en parallèle ; nom d'artiste en consigne de style interne seulement, jamais public.
- 2026-10-09 : Section « Tests » dans l'UI admin (du plus récent au plus ancien, pouces, suppression, barre de position, repère « Jamais écouté », numéro unique par test) ; police Sora embarquée pour tous les titrages, pubs Traveling Sound en machine à écrire ; titre et date sur la pochette sans toucher l'image.
- 2026-10-09 : La graine ACE n'était pas appliquée (`use_random_seed` vrai par défaut) : corrigé dans `ace_worker.py` ; les essais « à graine fixe » antérieurs ne sont pas fiables ; paroles contrôlées par `check_lyrics.py` avant chaque lancement.
- 2026-10-09 : Démo privée T01 (Arroser Les Roses) : version 18 retenue, texte adapté (« posté », « zoublie »), voix de femme non retenue (instable), statut `VALIDE` interdit sans accord écrit de l'auteur ; lot de pochettes terminé, scores négatifs exclus.
