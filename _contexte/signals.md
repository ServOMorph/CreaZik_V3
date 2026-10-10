# Signals — CreaZik_V3   (MAJ 2026-10-10, fin de session)

## Actions ouvertes
- [P1|ouvert] Appliquer techniquement la validation préalable : envoyer les nouvelles générations vers les Tests et bloquer leur ajout à la diffusion ou à la rotation sans demande explicite.
  - fait quand: le pipeline automatique produit d'abord des fichiers accessibles dans les Tests et aucun chemin n'ajoute un nouveau contenu à la diffusion sans demande de l'utilisateur
  - réf: `AGENTS.md` section Spécificités projet, `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` section 2.6, `.claude/skills/generation-morceaux/SKILL.md` étapes 6 et 7
- [P1|ouvert] Écouter la grille de voix de femme (section Tests : tests 26 à 31 en 135 s et 39 à 44 en 60 s, texte corrigé) et trancher si une version garde la voix de femme du début à la fin ; en tirer la règle du skill `generation-morceaux`
  - fait quand: une version à voix de femme stable est retenue ou la piste est abandonnée, et le skill et `REGLES_GENERATION_DEV.md` section 6 sont mis à jour
  - réf: `webradio/playlists/tests-ace/outputs/playlist_results.json`, `.claude/skills/generation-morceaux/SKILL.md`, `tests_manuels.md` n°5
- [P1|ouvert] Démo T01 « Arroser Les Roses » : version 18 retenue (voix d'homme) ; écouter sa fin et décider quoi envoyer à l'auteur (texte adapté « posté », « zoublie », à lui signaler) ; l'accord écrit de l'auteur n'a pas été demandé et le statut `VALIDE` reste interdit
  - fait quand: la version à envoyer est confirmée à l'écoute (`tests_manuels.md` n°6) et l'envoi à l'auteur est décidé
  - réf: `webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3`, `TEXTES/liste_attente.md`, `TEXTES/usage_prive/INDEX.md`
- [P1|ouvert] Valider sur iPhone le titrage de la pochette, la section Tests et la police Sora
  - fait quand: les contrôles 2, 3 et 4 de `tests_manuels.md` sont validés ou les corrections demandées sont faites
  - réf: `webradio/listen.js` (`fitCoverTitle`), `webradio/listen.css`, `webradio/motion.js`
- [P1|ouvert] Compléter la commande `/generate_lyrics` (agent `textes`) : grille rimes, répétitions, clichés en plus de `check_lyrics.py`, et lot de paroles écouté et jugé
  - fait quand: un lot test de paroles est généré dans `TEXTES/` puis écouté et jugé
  - réf: `.claude/commands/generate_lyrics.md`, `TEXTES/tools/check_lyrics.py`, `TEXTES/agent_role.md`
- [P1|ouvert] Écouter les jingles 1 à 5 de la catégorie WebRadio régénérés avec « IA » (Whisper entend « il y a ») et décider : valider puis régénérer les 14 autres (environ 17 min), ou changer la graphie
  - fait quand: prononciation validée et les 19 jingles WebRadio disent « CréaZik IA WebRadio » (ou graphie retenue appliquée)
  - réf: `D:\ServOMorph\TTS_Local\jingles_ia_batch.py`, `D:\ServOMorph\TTS_Local\jingles_ia_wav\`, `D:\ServOMorph\TTS_Local\jingles_old_mp3\`, `webradio/jingles/webradio/outputs/`
- [P1|ouvert] Valider les jingles SérénIA Tech (5 textes) et la prononciation « Sérénia Tèk » / « Traveling Sound Ouèbe Radio »
  - fait quand: textes et prononciation validés ou corrigés puis régénérés
  - réf: `D:\ServOMorph\TTS_Local\jingles_pub_texts.json`, `D:\ServOMorph\TTS_Local\jingles_pub_batch.py`, `D:\ServOMorph\TTS_Local\jingles_pub_finalize.py`
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (écran verrouillé avec Web Audio, section Tests, titrage, police, cycle visuel, pubs, jingles, admin)
  - fait quand: les sections correspondantes de `tests_manuels.md` sont vidées par contrôles réels
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/radio.html`
- [P2|ouvert] Tester les modifications de pochettes sans texte et de traçabilité d'`ace_worker.py` commitées sans test complet : une pochette sur une playlist (`cover_batch.py --playlist`), puis la reprise d'une piste déjà générée avec le nouveau nom de fichier horodaté (risque de régénération), et la compatibilité avec `compress_audio.py` et la suppression de morceau
  - fait quand: une pochette est générée avec le nouveau prompt, une relance n'écrase ni ne régénère une piste `generated`, et la compression et la suppression retrouvent les fichiers nommés avec horodatage et graine
  - réf: `webradio/ace_worker.py` (`write_generation_trace`), `webradio/tools/cover_gen.py`, `webradio/tools/cover_batch.py`, `webradio/compress_audio.py`
- [P2|ouvert] Écouter et donner son avis sur le test 45 (Funky Yogi nu-disco) et le test 46 (Marie rap mélodique avec voix) de la section Tests
  - fait quand: avis donné et réglages ou graine retenus consignés, `tests_manuels.md` n°7 et n°8 vidés
  - réf: `tests_manuels.md` n°7 et n°8, `webradio/tests_ace/funky_yogi/`, `webradio/tests_ace/marie_rap/`
- [P2|ouvert] Câbler un protocole d'apprentissage : `webradio/learning/morceaux_rejetes.jsonl` n'est lu par aucun code de génération ; relier votes et commentaires des Tests, prompt et graine à des réglages recommandés dans le skill
  - fait quand: une procédure (script ou étape du skill) relit les votes des Tests et les rejets pour proposer les réglages d'une prochaine génération
  - réf: `webradio/tests_state.json`, `webradio/learning/morceaux_rejetes.jsonl`, `.claude/skills/generation-morceaux/SKILL.md`
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP`), la section « Tests » (ou la verrouiller), remplacer `DEV_UNIFIED = True` en dur par un réglage explicite, remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, refermer `/api/dynamics` avec une UI auditeur séparée
  - fait quand: aucun saut public possible, `DEV_UNIFIED` piloté, aucun nom d'artiste public, dynamique et Tests refermés dans l'UI auditeur
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.4, 3.6, 3.7 et 5.5, `webradio/server.py`
- [P2|ouvert] Confirmer deux changements du répertoire de travail non faits pendant ces sessions : seuil `0.688` dans `jlayout` (`webradio/motion.js`) et suppression du formulaire de commentaires, du bloc « musique humaine » et du contact dans `webradio/listen.html`
  - fait quand: l'utilisateur confirme ou demande la correction
  - réf: `git diff webradio/motion.js webradio/listen.html`, `AMELIORATIONS.md`
- [P2|ouvert] Choisir parmi les propositions de réaménagement de l'UI admin et décider du sort de `ui.html`
  - fait quand: l'utilisateur a tranché et les choix retenus sont appliqués
  - réf: `webradio/radio.html`, `webradio/ui.html`
- [P3|ouvert] Relever la graine effective quand `seed` vaut `-1` (rotation) : le sidecar enregistre `-1` et le morceau n'est pas reproductible
  - fait quand: la graine tirée par ACE est écrite dans le sidecar et dans `playlist_results.json`
  - réf: `webradio/ace_worker.py`, `D:\ServOMorph\ACE-Step-1.5\acestep\core\generation\handler\task_utils.py` (`prepare_seeds`)
- [P3|ouvert] Décider du versionnage des MP3 conservés dans `TEXTES/artistes/Marie/` (2 instrus et `tops_instrus/`, environ 3 à 3,6 Mo chacun) : non commités à cette clôture car la règle est de ne pas versionner l'audio
  - fait quand: l'utilisateur tranche entre versionner, ajouter au `.gitignore` ou stocker ailleurs
  - réf: `TEXTES/artistes/Marie/INDEX.md`, `.gitignore`
- [P3|ouvert] Jingles de pub Traveling Sound : les 5 textes sont générés et mélangés aux autres ; à ajuster si besoin
  - fait quand: l'utilisateur confirme les 5 textes ou demande des changements
  - réf: `webradio/jingles/traveling-sound/outputs/playlist_results.json`
- [P3|ouvert] Poursuivre la génération musicale en rotation (`/start_generation`, service `generation` arrêté ; `analyse` et `compression` relancés) et retirer de « idée de playlist.md » chaque entrée terminée
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md`
- [P3|ouvert] Mise en ligne permanente : VPS Linux (systemd, Caddy ou Cloudflare, sous-domaine `radio.serenia-tech.fr`, rsync des mp3) ; Vercel, Render gratuit et Netlify écartés ; fonctionnement du serveur sous Linux non testé
  - fait quand: décision de déployer prise et VPS commandé, ou piste abandonnée
  - réf: `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Section Tests : dossiers par clé `folder` (`tests_folder`, `server.py`) ; commentaires et pouces dans `webradio/tests_state.json`, à lire pour analyser les écoutes. Contient en fin de session : test 45 (Funky Yogi nu-disco), test 46 (Marie rap avec voix) et la grille voix de femme. Serveur actif (port 5000).
- Instrus de Marie : la règle (5 graines, tri à l'écoute, intro non pilotable, 15 à 30 s) est dans le skill `generation-morceaux`. Retenus : `TEXTES/artistes/Marie/tops_instrus/` (graines 2026 et 31415, copiés aussi dans Téléchargements) et 2 instrus à la racine de `TEXTES/artistes/Marie/`. Mot « garde » d'un morceau = le ranger chez l'artiste (`.claude/memory.md`).
- `ace_worker.py` écrit un sidecar `.metadata.json` et un manifeste par test ; le nom du WAV porte horodatage et graine ; `lyrics` est lu pour un cas instrumental. Services `analyse` et `compression` actifs, `generation` arrêté.
- Avant une nouvelle génération GPU, consulter l'état des services et la VRAM libre. Toute nouvelle création destinée à la radio passe par les Tests puis une demande explicite avant diffusion.

# Session du 2026-10-10

## Décisions prises
- Graine toujours imposée (>= 0) pour les tests ; passage obligatoire par les Tests ajouté au skill (étapes 6 et 7).
- « Garde » = ranger le MP3 et son sidecar chez l'artiste (mémoire projet).
- Instrus de Marie : générer 5 graines, trier à l'écoute ; l'intro courte n'est pas le critère décisif.
- Nom d'artiste cité en inspiration jamais dans le caption ni le titre d'un test.

## Livrables produits ou modifiés
- `webradio/ace_worker.py`, `tools/cover_gen.py`, `tools/cover_batch.py`, `.claude/commands/generate_covers.md` : changements antérieurs identifiés (traçabilité, pochettes sans texte), commités, test complet en attente ; `ace_worker.py` lit `lyrics` pour un instrumental.
- `.claude/skills/generation-morceaux/SKILL.md`, `.claude/memory.md`, `tests_manuels.md`, `TEXTES/artistes/Marie/INDEX.md` : mis à jour.
- `TEXTES/artistes/Marie/` : 2 instrus et `tops_instrus/` (MP3 non commités) ; tests Funky Yogi, Marie rap et instrus dans `webradio/tests_ace/`.

## Hypothèses validées / invalidées
- VALIDE : sidecar et manifeste écrits pour chaque génération ; 150 s sans décodage VAE sur CPU (graines testées).
- INVALIDE : intro de 10 s réglable (beat entre 14 et 30 s selon graine et tempo) ; premier style Funky Yogi (electro-funk, 3 graines) rejeté et supprimé.
- EN ATTENTE : avis sur les tests 45 et 46 ; effet réel de 70 contre 130 BPM, de « binaire » et du piano à graine égale.

## Prochaine étape exacte
Tester les pochettes sans texte et la reprise de piste d'`ace_worker.py`, puis appliquer techniquement la validation préalable dans le pipeline automatique.

## Question bloquante pour la session suivante
Aucune
