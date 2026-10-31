# File des agents (relue à chaque reprise)

Exécutants : agents Claude (UI, intégration), Codex (`_codex/run_codex.ps1`), OpenCode modèle gratuit (`_codex/run_opencode.ps1`, briefs autonomes : pas de lecture hors dépôt ni de bash). Jamais deux exécutants sur les mêmes fichiers en même temps ; une seule génération GPU à la fois.

Suivi visible par l'utilisateur : carte admin « Suivi du travail » de la page `/` (port 5000 ou tunnel ; `/suivi.html` redirige vers `/`), qui relit `suivi_travail/etat.json` toutes les 10 s : mettre à jour ce JSON à chaque changement de statut. L'artefact https://claude.ai/artifact/RXbmiQhokX3Uhb8A2nXA2p n'est plus mis à jour.

Consigne utilisateur (2026-10-30) : décider et lancer directement, sans demander son avis.

## Engagement GPU
La session « LLM » (entraînement v9, ~5,5 Go de VRAM) attend mon signal : quand les agents 2 (plugin morceau) et 3 (stop motion) ont fini et que ComfyUI, ACE-Step et Ollama sont déchargés (`POST http://127.0.0.1:8189/free`, `ollama stop`), la prévenir par SendMessage à `uds:\\.\pipe\LOCAL\cc-msg-45e531f89eb5b044f1b2e71024a9350d`, et prévenir l'utilisateur. Contrôler avant : `nvidia-smi`, `GET :8189/queue`, processus `ace_worker|generate|run_rotation|run_queue`.

## Pause GPU (depuis 2026-10-30 ~22:10)
Entraînement v9 de la session LLM (~5,6 Go, ~2,5 jours). Les files d'images (`user_images.py`) et de morceaux (`user_songs.py`) sont en pause tant que `webradio/gpu_pause.flag` existe (les demandes restent en attente). Reprise : supprimer ce fichier. Les agents de génération de contenu GPU (stop motion, tests ACE) ne doivent pas être lancés pendant la pause.

## En cours
- Agent 4 (Opus) : socle profils (`webradio/profiles/`), comptes (`users.json` hors git, `tools/user_add.py`, Olive/Olive = traveling-sound), plugins déclaratifs (`webradio/plugins/`), `GET /api/session`, jingles filtrés par profil côté client. Fichiers : `server.py`, `listen.js`, `user.html`, `listen.css`, `radio_content.json`, nouveaux modules, `REGLES_GENERATION_DEV.md`, `tests_manuels.md`. Pas de GPU.
- Codex : template de délégation réutilisable dans `_templates/delegation/` ; à la fin : vérifier puis prévenir la session « VibeObs » (SendMessage `VibeObs`) qu'il est disponible pour intégration comme nouveau template.

## Ensuite (séquentiel, mêmes fichiers que l'agent 4)
- Agent 5 : fusion de l'UI dev (`listen.html`, `radio.html`, panneaux admin) et de la page de suivi en plugins admin dans l'UI unique du port 5000 ; Précédent/Suivant GLOBAUX pour l'admin (Précédent = action `now` sur la clé du morceau précédent dans `played`) en plus des ⏮⏭ personnels ; `/listen.html` redirige vers `/`.
- Agent 5 (suite) : plugin admin « génération d'image » (réutilise la file d'images) ; plugin admin « texte → jingle urgent » (voix rapide Kokoro par défaut, option Chatterbox) ; le test réel de l'image attend la fin de l'entraînement GPU (`gpu_pause.flag`).
- Plugin « Rien » ci-dessous inchangé.

## En cours (ancien)
Rien. Signal GPU envoyé à la session LLM le 2026-10-30 ~22:00 (les files d'images et de morceaux du serveur peuvent toujours solliciter la carte : à mettre en pause si la session LLM le demande).

## Terminé
- Agent 1 (plugins + image) et agent 2 (plugin morceau) : vérifiés, annonces diffusées. Rien d'écouté ni testé sur iPhone (voir `tests_manuels.md` 19 à 21).

## En attente
1. Profils de démo : la démo actuelle est le profil « Olivier ». Stocker l'UI auditeur telle que développée pour chaque personne (copie figée par profil, servie à part), puis repartir de la version courante pour la démo suivante. Après l'agent 2.

## Règles de jingle
Annonce radio uniquement pour un changement ou une création visible dans l'UI auditeur (voir `webradio/REGLES_GENERATION_DEV.md` 3.11).
