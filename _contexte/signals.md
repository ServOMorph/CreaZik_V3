# Signals — CreaZik_V3   (MAJ 2026-10-09, fin de session)

## Actions ouvertes
- [P1|ouvert] Écouter la grille de voix de femme (section Tests de l'UI admin : tests 26 à 31 en 135 s et 39 à 44 en 60 s, texte corrigé) et trancher si une version garde la voix de femme du début à la fin ; en tirer la règle du skill `generation-morceaux` (la note actuelle dit « grille à écouter avant de conclure »)
  - fait quand: une version à voix de femme stable est retenue ou la piste est abandonnée, et le skill et `REGLES_GENERATION_DEV.md` section 6 sont mis à jour
  - réf: `webradio/playlists/tests-ace/outputs/playlist_results.json`, `.claude/skills/generation-morceaux/SKILL.md`, `tests_manuels.md` n°5
- [P1|ouvert] Démo T01 « Arroser Les Roses » : version 18 retenue (voix d'homme) ; écouter sa fin et décider quoi envoyer à l'auteur (texte adapté « posté », « zoublie », à lui signaler) ; l'accord écrit de l'auteur n'a pas été demandé et le statut `VALIDE` reste interdit
  - fait quand: la version à envoyer est confirmée à l'écoute (`tests_manuels.md` n°6) et l'envoi à l'auteur est décidé
  - réf: `webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3`, `TEXTES/liste_attente.md`, `TEXTES/usage_prive/INDEX.md`
- [P1|ouvert] Valider sur iPhone le titrage de la pochette (titre centré en haut, date en bas à droite, tailles à 375 à 430 px), la section Tests et la police Sora
  - fait quand: les contrôles 2, 3 et 4 de `tests_manuels.md` sont validés ou les corrections demandées sont faites
  - réf: `webradio/listen.js` (`fitCoverTitle`), `webradio/listen.css`, `webradio/motion.js`
- [P1|ouvert] Compléter la commande `/generate_lyrics` (créée, agent `textes`) : grille rimes, répétitions, clichés en plus de `check_lyrics.py`, et lot de paroles écouté et jugé par l'utilisateur
  - fait quand: un lot test de paroles est généré dans `TEXTES/` puis écouté et jugé
  - réf: `.claude/commands/generate_lyrics.md`, `TEXTES/tools/check_lyrics.py`, `TEXTES/agent_role.md`
- [P1|ouvert] Écouter les jingles 1 à 5 de la catégorie WebRadio régénérés avec « IA » (Whisper entend « il y a ») et décider : valider puis régénérer les 14 autres (environ 17 min), ou changer la graphie
  - fait quand: prononciation validée et les 19 jingles WebRadio disent « CréaZik IA WebRadio » (ou graphie retenue appliquée)
  - réf: `D:\ServOMorph\TTS_Local\jingles_ia_batch.py`, `D:\ServOMorph\TTS_Local\jingles_ia_wav\`, `D:\ServOMorph\TTS_Local\jingles_old_mp3\` (anciens mp3 1 à 5), `webradio/jingles/webradio/outputs/`
- [P1|ouvert] Valider les jingles SérénIA Tech (5 textes rédigés d'après les pubs) et la prononciation « Sérénia Tèk » / « Traveling Sound Ouèbe Radio »
  - fait quand: textes et prononciation validés ou corrigés puis régénérés
  - réf: `D:\ServOMorph\TTS_Local\jingles_pub_texts.json`, `D:\ServOMorph\TTS_Local\jingles_pub_batch.py`, `D:\ServOMorph\TTS_Local\jingles_pub_finalize.py`
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (écran verrouillé avec Web Audio, section Tests, titrage, police, cycle visuel, pubs, jingles, admin)
  - fait quand: les sections correspondantes de `tests_manuels.md` sont vidées par contrôles réels
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/radio.html`
- [P2|ouvert] Relancer les services `analyse` et `compression` (arrêtés) avant la prochaine génération de morceaux, puis `/start_generation`
  - fait quand: `services.ps1 status` montre analyse et compression actifs
  - réf: `webradio/services.ps1`, `webradio/REGLES_GENERATION_DEV.md` section 5.2
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP`), le bouton « Test » et la section « Tests » (ou les verrouiller), remplacer `DEV_UNIFIED = True` en dur par un réglage explicite, remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, refermer `/api/dynamics` avec une UI auditeur séparée
  - fait quand: aucun saut public possible, `DEV_UNIFIED` piloté, aucun nom d'artiste public, dynamique, Test et Tests refermés dans l'UI auditeur
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.4, 3.6, 3.7 et 5.5, `webradio/server.py`
- [P2|ouvert] Confirmer deux changements du répertoire de travail non faits pendant cette session : seuil `0.688` dans `jlayout` (`webradio/motion.js`) et suppression du formulaire de commentaires, du bloc « musique humaine » et du contact dans `webradio/listen.html`
  - fait quand: l'utilisateur confirme ou demande la correction
  - réf: `git diff webradio/motion.js webradio/listen.html`, `AMELIORATIONS.md`
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
- Agents de zone `textes` (`TEXTES/`) et `modeles_llm` (`MODELES_LLM/`, `webradio/tests_ace/` exclu) ; lancement par `/start textes` ou `/start modeles_llm`. Tests GPU à faire à tour de rôle (RTX 4060 8 Go), ne pas lancer `/close` complet dans deux sessions à la fois.
- Mode dev : un seul utilisateur ; votes, avis et dynamiques de `radio.db` à conserver (voir `.claude/memory.md`). Le lien de l'application n'est connu de personne (déclaré par l'utilisateur le 2026-10-08) ; le tunnel `cloudflared` tournait.
- État au dernier statut : serveur radio actif (port 5000, redémarré le 2026-10-09 après le correctif de suppression des tests) ; analyse, compression et génération arrêtées ; lot de pochettes terminé (`completed_with_skips`, 256 morceaux à score négatif exclus) ; aucun worker ACE, ComfyUI arrêté. Après toute modification Python, redémarrer avec `services.ps1 restart -Only serveur`.
- Section « Tests » : versions dans `webradio/playlists/tests-ace/outputs/` (non versionné), état dans `webradio/tests_state.json` ; prochain numéro de test libre : 45 ; originaux des versions Lagniel dans `webradio/tests_ace/demo_lagniel/outputs/` (non versionné). Les graines ACE ne sont appliquées que depuis le 2026-10-09.
- Hors dépôt : `D:\ServOMorph\TTS_Local\` contient les scripts Chatterbox et les WAV sources des jingles.
- 29 jingles actifs : 19 WebRadio, 5 Traveling Sound, 5 SérénIA Tech ; un jingle tous les 5 morceaux.
- Fichiers non suivis ou modifiés laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `ad.png`, `MODELES_LLM/`, `DOCUMENTATION/`, `TEXTES/domaine_public/`, modifications d'outils de pochettes (`cover_batch.py`, `cover_gen.py`, `covers_charte.json`, `make_charte.py`, `generate_covers.md`) et journaux `tests_ace/marie/` antérieurs à cette session.

## Dernière session (2026-10-09)
# Session du 2026-10-09 (section Tests, démo T01, graine ACE, titrage)

## Décisions prises
- Section « Tests » dans l'UI admin (liste récente d'abord, pouces, suppression, position, repère « Jamais écouté », numéro unique par test) ; police Sora embarquée ; titre et date sur la pochette.
- Démo T01 : version 18 retenue (voix d'homme, `[Silence]`, texte adapté « posté », « zoublie ») ; voix de femme non retenue, instable.
- Graine ACE corrigée (`use_random_seed=False`) ; paroles contrôlées par `check_lyrics.py` avant lancement.

## Livrables produits ou modifiés
- `webradio/server.py`, `listen.js`, `listen.css`, `listen.html`, `motion.js`, `radio_engine.py`, `radio.html`, `ace_worker.py`, `fonts/` : voir `CHANGELOG.md` v1.7 ; correctifs de revue de code appliqués (suppression de test sous Windows, contrôleur de paroles).
- `TEXTES/tools/check_lyrics.py`, `.claude/commands/generate_lyrics.md`, `.claude/skills/generation-morceaux/SKILL.md`, `webradio/REGLES_GENERATION_DEV.md`, `tests_manuels.md`, `AMELIORATIONS.md` : mis à jour.
- Pochettes : lot terminé (175 créées, 256 exclues pour score négatif).

## Hypothèses validées / invalidées
- VALIDE : la graine n'était pas appliquée (corrélation 0,0008 puis 0,99997 après correctif) ; volume des jingles réglable fonctionnel sur iPhone ; version 18 de la démo jugée bonne par l'utilisateur.
- INVALIDE : les essais « seed » du test Marie (v7 à v9) et de la démo (graines 7, 123, 2024) ; le duo homme/femme par balises de section.
- EN ATTENTE : voix de femme stable (grille à écouter) ; titrage sur iPhone ; relecture de la revue de code (points hors session).

## Prochaine étape exacte
Écouter la grille voix de femme (tests 26 à 31 et 39 à 44) et valider le titrage sur iPhone ; relancer analyse et compression avant la prochaine génération de morceaux.

## Question bloquante pour la session suivante
Une voix de femme stable est-elle obtenue sur l'une des versions de la grille ?
