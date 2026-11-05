# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Chatterbox multilingue (CPU, timbre de référence Kokoro) ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
UI unique sur le port 5000 (commit `7181805`, sans push) : profils `classique` et `traveling-sound`, comptes, plugins auditeur (styles, image, morceau) et admin (programmation, outils, jingle texte, suivi), jingles urgents ; tunnel `vertia-test.serenia-tech.fr`.
Files GPU d'images et de morceaux en pause (`gpu_pause.flag`, entraînement v9 d'une autre session) ; le port 5000 est occupé par un autre projet, CréaZik non lancé.
Stop motion : piste « robot batteur » retenue (3 poses/s + transitions générées), usage à choisir. Écriture humaine : 19 versions Funky Yogi à écouter ; préférences et règles des négatifs en attente d'accord.
Restent : contrôles manuels (tests 18 à 24, iPhone), test réel des plugins image/morceau après la pause, clip L'Invariable, déploiement.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-10 : Paroles classées par artiste dans `TEXTES/artistes/` ; l'utilisateur déclare être Funky Yogi et détenir les droits sur ce texte, et déclare disposer des droits sur les textes Marie.
- 2026-10-10 : section Tests rangée en dossiers (clé `folder` ou règles du serveur) avec commentaire par version dans `tests_state.json` ; bouton « Test » supprimé.
- 2026-10-10 : Graine toujours imposée pour les tests ; sidecar et manifeste par génération ; « garde » = ranger le MP3 chez l'artiste ; instrus de Marie générés par 5 graines puis triés à l'écoute (intro non pilotable).
- 2026-10-12 : Écriture humaine : Funky Yogi mis en musique (electro/funk/disco/soul, ~120 BPM), préférences issues des seuls votes radio avec accord avant mise à jour ; chansons françaises retirées de la radio sauf 14 versions.
- 2026-10-12 : À chaque ajout de morceau à la WebRadio, prendre les JSON (sidecar, audiomap) avec ; playlist `creation-francaise` créée pour les créations originales.
- 2026-10-15 : Morceaux à score négatif du catalogue diffusé supprimés (suppression par `RadioEngine.edit_catalog` hors serveur), scores remis à zéro ; archive `DOCUMENTATION/apprentissage/votes_archive/` sommée par `calculer_preferences.py` ; règles tirées des négatifs proposées, non appliquées.
- 2026-10-15 : Playlist « Blues-rock guitare claire » (anglais, nom d'artiste jamais public) validée après test : 6 morceaux positifs en rotation, 4 négatifs supprimés ; bouton Test (`test_loop`) ; revue des pochettes par page locale, plafond de 3 refus ; pas de push pendant l'exécution autonome.
- 2026-10-17 : UI auditeur séparée `webradio/user.html` (même `listen.js`, drapeau `CREAZIK_USER_UI`), page d'accueil du port 5000 ; sans Suivant, Slow/Medium/High ni remise à zéro ; pouces à vote unique exclusif ; commentaires restaurés ; pages dev inchangées ; revue dans un artefact claude.ai (lecture du son impossible dans l'artefact).
- 2026-10-18 : Votes auditeurs collectés à part (`user_votes.json`, cookie `creazik_voter_u`, en-tête `X-Creazik-Ui`), sans effet sur la rotation, pour analyse manuelle avant suppression ou pondération ; pubs et jingles Traveling Sound supprimés.
- 2026-11-05 : UI unique sur le port 5000 en plugins déclaratifs avec profils et comptes ; plugins image et morceau d'auditeurs en file GPU sans quota (phase de test) ; création d'auditeur diffusée à tous après un jingle ; annonces radio réservées aux changements visibles de l'UI auditeur, diffusées sans passage par les Tests ; délégation Codex et OpenCode gratuit (jamais pour image ou musique).
