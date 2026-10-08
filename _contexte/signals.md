# Signals — CreaZik_V3   (MAJ 2026-10-08, fin de session)

## Actions ouvertes
- [P1|ouvert] Créer la commande `/generate_lyrics` (paroles françaises de qualité, thème et style « à la manière de » en consigne interne, grille de qualité par script) : travail confié à l'agent `textes` (écriture limitée à `TEXTES/`)
  - fait quand: la commande existe, un lot test de paroles est généré dans `TEXTES/` puis écouté et jugé par l'utilisateur
  - réf: `TEXTES/agent_role.md`, `.claude/skills/generation-morceaux/SKILL.md`, `webradio/REGLES_GENERATION_DEV.md` sections 1 et 5.5
- [P1|ouvert] Tests ACE « Marie » (voix) : écouter v7 (seed 1), v8 (seed 7) et v9 (seed 123), générées (fichiers du 07/10), même caption slam féminin piano seul sur le couplet 1 (40 s), et trancher si une seed garde un timbre de voix constant
  - fait quand: au moins une seed donne une voix féminine au timbre constant, ou la piste « seed » est écartée et une autre (extrait plus court, caption) est choisie
  - réf: `webradio/tests_ace/marie/config.json`, `webradio/tests_ace/marie/outputs/`, `webradio/playlists/tests-ace/outputs/playlist_results.json` (bouton Test de l'UI auditeur), `.claude/skills/generation-morceaux/SKILL.md`
- [P1|ouvert] Écouter les jingles 1 à 5 de la catégorie WebRadio régénérés avec « IA » (Whisper entend « il y a ») et décider : valider puis régénérer les 14 autres (environ 17 min), ou changer la graphie
  - fait quand: prononciation validée et les 19 jingles WebRadio disent « CréaZik IA WebRadio » (ou graphie retenue appliquée)
  - réf: `D:\ServOMorph\TTS_Local\jingles_ia_batch.py`, `D:\ServOMorph\TTS_Local\jingles_ia_wav\`, `D:\ServOMorph\TTS_Local\jingles_old_mp3\` (anciens mp3 1 à 5), `webradio/jingles/webradio/outputs/`
- [P1|ouvert] Valider les jingles SérénIA Tech (5 textes rédigés d'après les pubs) et la prononciation « Sérénia Tèk » / « Traveling Sound Ouèbe Radio »
  - fait quand: textes et prononciation validés ou corrigés puis régénérés
  - réf: `D:\ServOMorph\TTS_Local\jingles_pub_texts.json`, `D:\ServOMorph\TTS_Local\jingles_pub_batch.py`, `D:\ServOMorph\TTS_Local\jingles_pub_finalize.py`
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (cycle visuel, pubs, jingles, admin)
  - fait quand: les sections correspondantes de `tests_manuels.md` sont vidées par contrôles réels
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/radio.html`
- [P1|ouvert] Terminer la génération des pochettes éligibles : batch relancé par l'utilisateur dans son propre terminal cmd (hors VS Code, pour survivre à la fermeture de la session) ; si le processus s'arrête, relancer `start "covers" /min python tools\cover_batch.py` depuis `webradio` (ComfyUI d'abord ; une seule instance)
  - fait quand: `python webradio/tools/cover_batch.py --status` ne liste plus de pochette manquante éligible (échecs restants listés, scores négatifs exclus)
  - réf: `python webradio/tools/cover_batch.py --status`, `webradio/logs/cover_generation_state.json`, `.claude/commands/generate_covers.md`
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP` dans `server.py`, `applyMode` dans `listen.js`), remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, et refermer `/api/dynamics` (contrôle admin) avec la création d'une UI auditeur séparée de l'UI dev
  - fait quand: aucun saut public possible, aucun nom d'artiste dans les titres publics, dynamique et Test refermés dans l'UI auditeur
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
- [P3|ouvert] Mise en ligne permanente : VPS Linux (systemd, Caddy ou Cloudflare, sous-domaine `radio.serenia-tech.fr`, rsync des mp3) ; Vercel, Render gratuit et Netlify écartés ; fonctionnement du serveur sous Linux non testé
  - fait quand: décision de déployer prise et VPS commandé, ou piste abandonnée
  - réf: `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Agents de zone créés le 2026-10-08 : `textes` (`TEXTES/`) et `modeles_llm` (`MODELES_LLM/`, installation et comparaison de modèles musicaux, `webradio/tests_ace/` exclu) ; lancement par `/start textes` ou `/start modeles_llm`. Travail en parallèle : tests GPU à faire à tour de rôle (RTX 4060 8 Go), ne pas lancer `/close` complet dans deux sessions à la fois.
- Mode dev : un seul utilisateur (le développeur) ; votes, avis et dynamiques enregistrés dans `radio.db` sont à conserver (voir `.claude/memory.md`).
- Au dernier statut, le serveur radio (port 5000) et ComfyUI (port 8189) tournaient, le batch de pochettes lancé dans un terminal cmd de l'utilisateur ; aucun worker ACE actif ; génération musicale en rotation arrêtée. Après toute modification Python, redémarrer avec `services.ps1 restart -Only serveur`.
- Hors dépôt : `D:\ServOMorph\TTS_Local\` contient les scripts Chatterbox et les WAV sources des jingles.
- 29 jingles actifs : 19 WebRadio (le 20 supprimé par l'utilisateur), 5 Traveling Sound, 5 SérénIA Tech ; un jingle tous les 5 morceaux.
- Tests ACE : le bouton « Test » (UI auditeur, public comme « Suivant », à retirer avant déploiement) lit la dernière génération de `webradio/playlists/tests-ace/` (hors catalogue, non diffusé). Série Marie : v1 à v9 dans `webradio/tests_ace/marie/` (v6 à v9 : couplet 1, 40 s).
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`, `TEXTES/` (textes de test pour la génération musicale, ex. `Marie-1_ace.md` au format ACE-Step).

## Dernière session (2026-10-08, suite)
# Session du 2026-10-08 (légende animée, cadrage des paroles)

## Décisions prises
- Légende du visuel (titre / description) : défilement vertical alterné toutes les 3,5 s, validé sur iPhone par l'utilisateur.
- Travail en parallèle réparti en deux agents de zone : `textes` (paroles françaises, commande `/generate_lyrics` à créer) et `modeles_llm` (autres modèles musicaux).
- Paroles : le nom d'artiste ne sert que de consigne de style interne, jamais dans un titre, un caption ou une attribution publics.

## Livrables produits ou modifiés
- `webradio/listen.js`, `webradio/listen.css` : légende animée (`setCaption`, `startCaptionTyping`) ; première version en frappe remplacée par le défilement.
- `webradio/REGLES_GENERATION_DEV.md` : règle de légende et cadrage des paroles.

## Hypothèses validées / invalidées
- VALIDE : défilement de la légende correct sur iPhone (contrôle utilisateur).
- EN ATTENTE : qualité réelle des paroles produites par la future commande, à juger à l'écoute.

## Prochaine étape exacte
Lancer `/start textes` dans une session dédiée et créer `/generate_lyrics` ; écouter v7 à v9 des tests ACE si ce n'est pas fait.

## Question bloquante pour la session suivante
Aucune
