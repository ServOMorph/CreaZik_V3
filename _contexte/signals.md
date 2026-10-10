# Signals — CreaZik_V3   (MAJ 2026-10-10, fin de session)

## Actions ouvertes
- [P1|ouvert] Écouter et évaluer les 30 morceaux de la campagne comparative depuis les dossiers de l'UI Tests ; reporter l'évaluation humaine via l'UI.
  - fait quand: les 30 pistes ont un statut/commentaire d'écoute renseigné ou sont explicitement écartées par l'utilisateur
  - réf: `tests_manuels.md` n°7, `MODELES_LLM/sorties/campagne_2026-10-09/generation_manifest.json`
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
- Campagne comparative du 2026-10-10 : 30 pistes (10 ACE-Step 1.5, 10 MusicGen Small, 10 HeartMuLa OSS 3B) ; résultats et configurations dans `MODELES_LLM/sorties/campagne_2026-10-09/`.
- Les 30 nouvelles pistes sont exposées dans l'UI admin par dossiers de modèle ; dix pistes Stable Audio antérieures sont aussi dans la liste. Statut d'écoute initial `pending`. Ne pas modifier `webradio/tests_state.json` manuellement.
- ACE-Step : 10/10 techniquement passées ; MusicGen Small : 10/10 ; HeartMuLa : 5/10 passées et 5 invalides (écrêtage probable sur cinq, dont une aussi trop courte). Ces statuts n'évaluent pas la qualité artistique.
- Avant une nouvelle génération GPU, consulter l'état des services et éviter d'interrompre une piste en cours.

# Session du 2026-10-10

## Décisions prises
- Comparer ACE-Step 1.5, MusicGen Small et HeartMuLa OSS 3B sur dix briefs communs, en séparant les seuils techniques de l'écoute humaine.
- Garder les sorties techniquement invalides de HeartMuLa dans l'UI pour rendre leurs défauts observables.

## Livrables produits ou modifiés
- `MODELES_LLM/sorties/campagne_2026-10-09/` : 30 sorties comparatives, sidecars, manifest et journaux de tentatives.
- `webradio/playlists/tests-modeles/outputs/playlist_results.json` : 30 entrées de cette campagne exposées dans trois dossiers de modèles, en plus des dix pistes Stable Audio antérieures.
- `MODELES_LLM/registre_campagne.py` et `DOCUMENTATION/` : suivi reproductible et documentation des modèles et critères.

## Hypothèses validées / invalidées
- VALIDE : ACE-Step et MusicGen Small passent les contrôles techniques sur les dix briefs chacun ; écoute humaine en attente.
- VALIDE : HeartMuLa passe techniquement sur cinq briefs sur dix ; cinq sorties restent consultables comme invalides.
- INVALIDE : toutes les sorties HeartMuLa seraient techniquement recevables -> écrêtage probable sur cinq pistes, durée insuffisante sur l'une d'elles.
- EN ATTENTE : jugement artistique à l'écoute des 30 pistes dans l'UI.

## Prochaine étape exacte
Écouter les 30 pistes comparatives dans la section Tests et renseigner le résultat humain dans l'UI.

## Question bloquante pour la session suivante
Aucune
