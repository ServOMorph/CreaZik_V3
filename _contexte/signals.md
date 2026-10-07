# Signals — CreaZik_V3   (MAJ 2026-10-07)

## Actions ouvertes
- [P1|ouvert] Tests ACE « Marie » (voix) : écouter les v7 (seed 1) et, si générées, v8 (seed 7) et v9 (seed 123), même caption slam féminin piano seul sur le couplet 1 (40 s), et trancher si une seed garde un timbre de voix constant
  - fait quand: au moins une seed donne une voix féminine au timbre constant, ou la piste « seed » est écartée et une autre (extrait plus court, caption) est choisie
  - réf: `webradio/tests_ace/marie/config.json`, `webradio/tests_ace/marie/outputs/`, `webradio/playlists/tests-ace/outputs/playlist_results.json` (bouton Test de l'UI auditeur), `.claude/skills/generation-morceaux/SKILL.md`
- [P1|ouvert] Worker ACE des v7 à v9 probablement bloqué en décodage VAE (dernier log à 20:00, v7 seule générée) : à arrêter avec accord de l'utilisateur avant toute autre génération ; relancer v8 et v9 avec `generate.py tests_ace/marie/config.json --only 8,9`
  - fait quand: process `ace_worker.py` arrêté, v8 et v9 générées
  - réf: `webradio/tests_ace/marie/gen_v789.log`
- [P1|ouvert] Écouter les jingles 1 à 5 de la catégorie WebRadio régénérés avec « IA » (Whisper entend « il y a ») et décider : valider puis régénérer les 14 autres (environ 17 min), ou changer la graphie
  - fait quand: prononciation validée et les 19 jingles WebRadio disent « CréaZik IA WebRadio » (ou graphie retenue appliquée)
  - réf: `D:\ServOMorph\TTS_Local\jingles_ia_batch.py`, `D:\ServOMorph\TTS_Local\jingles_ia_wav\`, `D:\ServOMorph\TTS_Local\jingles_old_mp3\` (anciens mp3 1 à 5), `webradio/jingles/webradio/outputs/`
- [P1|ouvert] Valider les jingles SérénIA Tech (5 textes rédigés d'après les pubs) et la prononciation « Sérénia Tèk » / « Traveling Sound Ouèbe Radio »
  - fait quand: textes et prononciation validés ou corrigés puis régénérés
  - réf: `D:\ServOMorph\TTS_Local\jingles_pub_texts.json`, `D:\ServOMorph\TTS_Local\jingles_pub_batch.py`, `D:\ServOMorph\TTS_Local\jingles_pub_finalize.py`
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (cycle visuel, pubs, jingles, admin)
  - fait quand: les sections correspondantes de `tests_manuels.md` sont vidées par contrôles réels
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/radio.html`
- [P1|ouvert] Terminer la génération des pochettes éligibles (ComfyUI arrêté, reprise via `/generate_covers`)
  - fait quand: toutes les pochettes éligibles sont générées ou les échecs restants sont listés, scores négatifs exclus
  - réf: `python webradio/tools/cover_batch.py --status`, `webradio/logs/cover_generation_state.json`, `.claude/commands/generate_covers.md`
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP` dans `server.py`, `applyMode` dans `listen.js`), remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, et décider si les boutons Slow/Medium/High restent réservés au développeur
  - fait quand: aucun saut public possible, aucun nom d'artiste dans les titres publics, choix sur la dynamique tranché
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.4, 3.6 et 5.5, `webradio/playlists.json`
- [P2|ouvert] Choisir parmi les propositions de réaménagement de l'UI admin et décider du sort de `ui.html`
  - fait quand: l'utilisateur a tranché et les choix retenus sont appliqués
  - réf: `webradio/radio.html`, `webradio/ui.html`
- [P3|ouvert] Jingles de pub Traveling Sound : les 5 textes sont générés et mélangés aux autres ; à ajuster si besoin
  - fait quand: l'utilisateur confirme les 5 textes ou demande des changements
  - réf: `webradio/jingles/traveling-sound/outputs/playlist_results.json`
- [P3|ouvert] Poursuivre la génération musicale en rotation (`/start_generation`, service arrêté au dernier statut) et retirer de « idée de playlist.md » chaque entrée terminée
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md`
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Mode dev : un seul utilisateur (le développeur) ; votes, avis et dynamiques enregistrés dans `radio.db` sont à conserver (voir `.claude/memory.md`).
- Au dernier statut, le serveur radio, l'analyse et la compression tournaient ; la génération musicale était arrêtée, ComfyUI aussi. Après toute modification Python, redémarrer avec `services.ps1 restart -Only serveur`.
- Hors dépôt : `D:\ServOMorph\TTS_Local\` contient les scripts Chatterbox et les WAV sources des jingles.
- 29 jingles actifs : 19 WebRadio (le 20 supprimé par l'utilisateur), 5 Traveling Sound, 5 SérénIA Tech ; un jingle tous les 5 morceaux.
- Tests ACE : le bouton « Test » (UI auditeur, public comme « Suivant », à retirer avant déploiement) lit la dernière génération de `webradio/playlists/tests-ace/` (hors catalogue, non diffusé). Série Marie : v1 à v9 dans `webradio/tests_ace/marie/` (v6 à v9 : couplet 1, 40 s).
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`, `TEXTES/` (textes de test pour la génération musicale, ex. `Marie-1_ace.md` au format ACE-Step).

## Dernière session (2026-10-07)
# Session du 2026-10-07 (tests ACE)

## Décisions prises
- Série de tests de voix avec ACE-Step sur `TEXTES/Marie-1_ace.md`, un seul changement par version, sorties dans `webradio/tests_ace/marie/`, écoute via le bouton « Test » de l'UI auditeur (playlist hors catalogue `playlists/tests-ace/`).
- BPM, tonalité et signature passés en paramètres du worker (`ace_worker.py`), plus dans le caption ; skill `generation-morceaux` créé.
- Boutons « Mettre en file » (playlist, morceau) dans le catalogue admin.

## Livrables produits ou modifiés
- `webradio/ace_worker.py`, `webradio/tests_ace/marie/` (config v1 à v9, extrait du couplet 1), `.claude/skills/generation-morceaux/SKILL.md` : en place.
- `webradio/listen.html`, `listen.css`, `listen.js` (bouton Test), `webradio/radio.html` (Mettre en file) : en place, non commités avant cette clôture.

## Hypothèses validées / invalidées
- VALIDE : caption « heavy hard-tuned autotune vocals, T-Pain and Future style, pitch-snapped robotic vocal effect » + rap trap donne un autotune net (v3) ; piano seul et voix féminine tenus sur 40 s (v6).
- INVALIDE : « single male vocalist » ne stabilise pas le timbre (v4) ; voix féminine demandée en caption sur 120 s donne une voix qui passe de femme à homme et d'autres instruments entrent (v5) ; réduire la longueur à 40 s ne suffit pas pour un timbre constant (v6).
- EN ATTENTE : effet de la seed sur la constance du timbre (v7 à v9) ; un décodage VAE à 120 s s'est figé 12 min (v4) puis est passé en 47 s ; v8 probablement figée.

## Prochaine étape exacte
Arrêter le worker figé (avec accord), générer v8 et v9, écouter v7 à v9 via « Test » et choisir la piste suivante (seed, extrait plus court ou caption).

## Question bloquante pour la session suivante
Autoriser l'arrêt du worker ACE figé ?
