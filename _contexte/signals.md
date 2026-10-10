# Signals — CreaZik_V3   (MAJ 2026-10-10, fin de session)

## Actions ouvertes
- [P1|ouvert] Appliquer techniquement la validation préalable : envoyer les nouvelles générations vers les Tests et bloquer leur ajout à la diffusion ou à la rotation sans demande explicite.
  - fait quand: le pipeline automatique produit d'abord des fichiers accessibles dans les Tests et aucun chemin n'ajoute un nouveau contenu à la diffusion sans demande de l'utilisateur
  - réf: `AGENTS.md` section Spécificités projet, `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` section 2.6
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
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP`), la section « Tests » (ou la verrouiller ; le bouton « Test » est déjà supprimé), remplacer `DEV_UNIFIED = True` en dur par un réglage explicite, remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, refermer `/api/dynamics` avec une UI auditeur séparée
  - fait quand: aucun saut public possible, `DEV_UNIFIED` piloté, aucun nom d'artiste public, dynamique et Tests refermés dans l'UI auditeur
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
- Campagne comparative : 40 votes présents dans l'état des Tests (ACE-Step 10 positifs sur 10 ; MusicGen, HeartMuLa et Stable Audio 2 positifs sur 10 chacun). Les défauts techniques de cinq sorties HeartMuLa restent distincts du jugement d'écoute.
- Les variantes temporaires « Soul du matin » et « Funky Yogi » ont été retirées des Tests ; l'original « Soul du matin » reste dans la WebRadio. Le texte « Funky Yogi » est classé dans `TEXTES/artistes/funky-yogi/`.
- Section Tests : dossiers déterminés par `tests_folder` (`server.py`), clé `folder` optionnelle dans `playlist_results.json` ; commentaires par version dans `webradio/tests_state.json` (clé `comments`) et dans `/api/tests` (champ `comment`), à lire pour analyser les écoutes. Serveur relancé et actif (port 5000) en fin de session.
- Avant une nouvelle génération GPU, consulter l'état des services et éviter d'interrompre une piste en cours. Toute nouvelle création destinée à la radio passe par les Tests puis une demande explicite avant diffusion.

# Session du 2026-10-10

## Décisions prises
- Section Tests en dossiers avec badge des morceaux jamais écoutés ; nom du dossier par clé `folder` ou règles du serveur.
- Commentaire par version stocké dans `tests_state.json` pour l'analyse ; bouton « Test » supprimé.
- Toute nouvelle création destinée à la WebRadio passe par les Tests ; diffusion seulement sur demande explicite.
- Paroles Funky Yogi et Marie classées par artiste ; l'utilisateur déclare disposer des droits.

## Livrables produits ou modifiés
- `webradio/server.py`, `listen.js`, `listen.css`, `listen.html` : dossiers, `/api/tests/comment`, suppression du bouton Test ; serveur relancé.
- `webradio/REGLES_GENERATION_DEV.md`, `tests_manuels.md`, `AMELIORATIONS.md`, `CHANGELOG.md` (v1.9), `README.md` : mis à jour.
- `AGENTS.md`, `.claude/memory.md`, `TEXTES/artistes/`, `TEXTES/INDEX.md` : règle de validation et textes rangés ; chemins des tests Marie corrigés.
- Essais « Soul du matin » et « Funky Yogi » retirés des Tests après écoute ; original radio conservé.

## Hypothèses validées / invalidées
- VALIDE : regroupement en 5 dossiers côté serveur, enregistrement et effacement d'un commentaire (appel direct des fonctions).
- INVALIDE sur « Soul du matin » : `shift=3` n'a pas apporté le groove et la précision souhaités ; l'utilisateur préfère les essais « Funky Yogi » avec moins de styles mêlés, sans conclusion générale sur le modèle.
- EN ATTENTE : rendu et usage réels de l'UI (dossiers, commentaire) sur navigateur et iPhone.

## Prochaine étape exacte
Poursuivre les contrôles manuels restants et appliquer techniquement la validation préalable dans le pipeline automatique.

## Question bloquante pour la session suivante
Aucune
