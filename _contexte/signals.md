# Signals — CreaZik_V3   (MAJ 2026-10-07)

## Actions ouvertes
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
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`, `TEXTES/` (textes de test pour la génération musicale, ex. `Marie-1_ace.md` au format ACE-Step).

## Dernière session (2026-10-07)
# Session du 2026-10-07

## Décisions prises
- Jingles : voix féminine Chatterbox (timbre synthétique), 1 s de silence en tête, rangés dans `webradio/jingles/` par catégorie (WebRadio, Traveling Sound, SérénIA Tech), mélangés, un tous les 5 morceaux.
- UI auditeur : cadre visuel unique centré, cycle de phases de 5 s (pochette, animations, pub 9 s, animations, pochette) avec transitions animées ; mascotte masquée ; pubs SérénIA Tech et Traveling Sound cliquables, charte Traveling Sound.
- Dynamique : boutons Slow/Medium/High réservés à l'admin ; le choix du développeur remplace l'énergie mesurée (poids 1).
- Nom affiché « CréaZik IA WebRadio » partout ; la voix dit « IA » (test sur 5 jingles).

## Livrables produits ou modifiés
- `webradio/jingles/`, `playlists.json`, `radio_engine.py`, `server.py` : jingles hors playlists, catégories, route statique `/jingles/`, dynamique admin.
- `webradio/radio.html` : jingles par catégories repliables, lecture et texte des jingles, libellé du poids de dynamique.
- `webradio/listen.html`, `listen.css`, `listen.js`, `motion.js`, `radio_content.json` : cycle visuel, transitions, pubs et charte.
- `TEXTES/`, `.claude/memory.md` : dossier de textes de test ; mémoire « mode dev ».

## Hypothèses validées / invalidées
- VALIDE : 25 tests du moteur passent ; serveur redémarré, mp3 des 3 catégories servis (HTTP 200) ; catalogue de 29 jingles chargé ; rendu des pubs Traveling Sound validé par l'utilisateur.
- INVALIDE : la transcription Whisper n'a pas pu confirmer « IA » (elle écrit « il y a ») : à trancher à l'écoute.
- EN ATTENTE : écoute des jingles 1 à 5 « IA » et des jingles SérénIA Tech ; contrôles iPhone ; affichage réel des catégories repliables dans l'admin.

## Prochaine étape exacte
Écouter les jingles 1 à 5 dans l'admin, trancher la prononciation de « IA », puis régénérer les 14 autres si elle convient.

## Question bloquante pour la session suivante
La prononciation « I A » des jingles WebRadio convient-elle ?
