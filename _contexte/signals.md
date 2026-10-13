# Signals — CreaZik_V3   (MAJ 2026-10-12, fin de session)

## Actions ouvertes
- [P1|ouvert] Écouter les 19 versions Funky Yogi (tests 47 à 65 : 10 textes en 3 styles, dont 3 textes avec chœurs base/v1/v2/v3) et voter ; juger les chœurs ; la première boucle d'apprentissage en dépend
  - fait quand: les 19 versions sont votées, les moyens de chœurs notés `teste` ou `echec` dans `regles_modeles.json` après accord, un bilan par texte rédigé (roadmap phase 6)
  - réf: `roadmap_ecriture_humaine.md` phase 6, `DOCUMENTATION/apprentissage/plan_run.json`, `DOCUMENTATION/apprentissage/propositions/textes-funky-yogi-photos.md`, `webradio/tests_state.json`
- [P1|ouvert] Valider le premier calcul de préférences (851 votes pris en compte ; 395 différences, premier calcul) : `diff_preferences.py --appliquer` seulement après accord
  - fait quand: l'utilisateur a relu le diff et accepte ou corrige `preferences.proposition.json`, puis `preferences.json` existe
  - réf: `OUTILS/apprentissage/diff_preferences.py`, `DOCUMENTATION/apprentissage/preferences.proposition.json`, `DOCUMENTATION/APPRENTISSAGE.md`
- [P1|ouvert] Clip promo L'Invariable (17 octobre 2026) : retenus dans le dossier `clip_promo\musique\retenus\` de SerenIATech (Eurodisco graine 2026, cover « Ça m'énerve » graine 42) ; écouter, améliorer refrain et variations mélodiques, choisir pour le clip ; droits du morceau de Helmut Fritz à trancher avant tout usage public du cover
  - fait quand: un morceau est choisi pour le clip, ses paroles finalisées dans `paroles_clip.md`, et la question des droits du cover tranchée
  - réf: `webradio/tests_ace/clip_atelier_invariable/config.json` (cas 7 à 22), `webradio/playlists/creation-francaise/`
- [P2|ouvert] Tester `src_audio` (cover) et `reference_audio` de `ace_worker.py` sur un cas réel suivi d'une écoute, et contrôler qu'un cas sans ces champs se comporte comme avant (pytest `webradio/tests`)
  - fait quand: pytest `webradio/tests` passe et le cover est écouté
  - réf: `webradio/ace_worker.py` (`prepare_audio`, `task_type`), `webradio/tests_ace/clip_atelier_invariable/outputs/`
- [P2|ouvert] Supprimer ou non du catalogue les 8 versions françaises « négatives » conservées (tri du 2026-10-12) ; aligner les descriptions de playlist (`instrumental` dit encore « 21 morceaux », `disco-en` inchangée)
  - fait quand: décision prise et appliquée, descriptions de `playlists.json` alignées
  - réf: `DOCUMENTATION/apprentissage/retrait_fr.json`, `webradio/playlists.json`, `webradio/catalog_overrides.json`
- [P2|ouvert] Contrôler dans le navigateur l'UI Tests (texte sur plusieurs lignes, plier/déplier) et la diffusion de `instrumental:22` et `creation-francaise:1` (serveur relancé le 2026-10-13, lecture confirmée sur téléphone par l'utilisateur)
  - fait quand: UI Tests contrôlée, les deux morceaux entendus à l'antenne ou signalés défaillants
  - réf: `tests_manuels.md` n°9 à 13, `webradio/listen.js`, `webradio/services.ps1`
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
- [P3|ouvert] Faire sauter le moteur radio à l'heure réelle au démarrage : après un arrêt prolongé il rejoue en accéléré les morceaux manqués (environ 20 min pour 23 h) et la lecture ne démarre pas sur téléphone pendant ce temps
  - fait quand: une relance après plusieurs heures d'arrêt donne un morceau en cours synchronisé en moins d'une minute
  - réf: `webradio/radio_engine.py`, `webradio/radio_state.json`
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
- Roadmap écriture humaine : phases 1 à 5 faites (outils, apprentissage, retrait des morceaux français, propositions, run) ; phase 6 en cours (attente des écoutes). Les 19 versions Funky Yogi sont dans les Tests ; `paroles.md` pas encore dans le run.
- `ace_worker.py` accepte `reference_audio`, `src_audio`, `task_type` (cover), `audio_start_s`/`audio_duration_s`, `audio_cover_strength`, `cover_noise_strength` ; seuls une référence audio et un cover ont été essayés.
- Radio : boucle désactivée, serveur du port 5000 relancé le 2026-10-13 et écouté par le tunnel (`vertia-test.serenia-tech.fr` vers `localhost:5000`, vérifié) ; après un arrêt prolongé le moteur rattrape son retard en accéléré (environ 20 min pour 23 h d'arrêt), pendant lequel la lecture ne démarre pas sur téléphone ; `instrumental:22` et `creation-francaise:1` ajoutés avec leurs JSON (règle mémoire : à chaque ajout, prendre les JSON).
- Section Tests : entrées `status: planned` possibles (sans MP3) ; UI avec plier/déplier. Dossier du clip : `webradio/tests_ace/clip_atelier_invariable/`.
- Avant une génération GPU, vérifier la VRAM libre (environ 1 Go pris par Windows et les applications).

# Session du 2026-10-12

## Décisions prises
- Réorientation vers l'écriture humaine : Funky Yogi mis en musique (electro, funk, disco, soul ; ~120 BPM, un à 100 et un à 95), ACE seul, 150 s au plus, échec technique = nouvelle graine.
- Apprentissage fondé sur les seuls votes radio ; `preferences.json` mis à jour seulement avec accord, diff présenté par `/close`.
- Chansons françaises retirées de la diffusion (14 versions gardées) ; boucle désactivée.
- Clip L'Invariable : disco funk puis groupe vocal Eurodisco ; retenus dans `clip_promo/musique/retenus/` ; playlist `creation-francaise` créée.
- À chaque ajout de morceau à la WebRadio : prendre les JSON avec (mémoire projet).

## Livrables produits ou modifiés
- `OUTILS/` (extraction, apprentissage, run_textes), `DOCUMENTATION/apprentissage/`, `DOCUMENTATION/APPRENTISSAGE.md` : outils et données, 15 tests passés ; `roadmap_ecriture_humaine.md` : statuts à jour.
- `TEXTES/artistes/funky-yogi/textes/` : 10 textes `RELU` ; 19 versions générées (tests 47 à 65).
- `webradio/ace_worker.py`, `server.py`, `listen.js`, `listen.css`, `radio_engine.py` : graine effective, entrées `planned`, UI Tests, référence audio et cover.
- `webradio/playlists/instrumental/` (morceau 22), `playlists/creation-francaise/` (nouvelle), `webradio/tests_ace/clip_atelier_invariable/` (cas 1 à 22).

## Hypothèses validées / invalidées
- VALIDE : run automatique de 19 versions ; graine enregistrée sur génération réelle ; cover et référence audio s'exécutent (journal « cover task », référence dans le sidecar).
- VALIDE : serveur du port 5000 relancé, tunnel atteint, lecture confirmée sur téléphone après le rattrapage du moteur ; serveur Eleventy parasite du port 5000 arrêté sur demande.
- EN ATTENTE : écoute des 19 versions, des chœurs, du clip, du cover et des voix Eurodisco ; effet réel de la référence audio.
- INVALIDE : aucune.

## Prochaine étape exacte
Écouter et voter les 19 versions Funky Yogi, valider le diff des préférences, puis rédiger le bilan par texte (phase 6).

## Question bloquante pour la session suivante
Quel morceau du clip L'Invariable est retenu, et les droits du cover de Helmut Fritz sont-ils réglés ?
