# Signals — CreaZik_V3   (MAJ 2026-10-23, fin de session)

## Actions ouvertes
- [P1|ouvert] Contrôler la page auditeur v2 dans un navigateur et sur iPhone via `https://vertia-test.serenia-tech.fr/` : pouces à vote unique exclusif (le second pouce remplace le premier), absence de totaux et de pubs Traveling Sound, formulaire de commentaires, titre et pochette en lecture ; publier une capture dans l'onglet v2 de l'artefact (le navigateur de test s'est bloqué deux fois, aucune capture de la v2)
  - fait quand: la v2 est vue en vrai (navigateur et iPhone), une capture est publiée dans l'artefact et les défauts sont corrigés ou consignés
  - réf: https://claude.ai/artifact/SCjtgCNBYAQhEMr56zaFuU, `revue_ui_user/revue_ui_user.html`, `webradio/user.html`, `webradio/listen.js` (`USER_UI`, `sendVoteSingle`)
- [P1|ouvert] Trancher comment relire l'UI auditeur avec le son : une page d'artefact ne peut ni appeler la radio locale ni l'intégrer (option 1 : revue dans l'artefact et écoute sur `localhost:5000/user.html` ; option 2 : maquette jouant quelques morceaux téléversés, hors direct)
  - fait quand: l'utilisateur choisit une option et elle est appliquée ou écartée
  - réf: fil de commentaires de l'artefact, `revue_ui_user/revue_ui_user.html`
- [P1|ouvert] Arrêter le mode Test (bouton « Arrêter le test », admin) : `test_loop` était encore à `true` au dernier contrôle (2026-10-18) et la radio ne joue alors que la playlist blues-rock ; puis contrôler que cette playlist (6 morceaux, poids par défaut 5) passe avec les autres
  - fait quand: `/api/radio/state` indique `test_loop` à `false` et la playlist `blues-rock-guitare` passe à l'antenne dans la programmation normale
  - réf: `tests_manuels.md` n°17, `webradio/radio_engine.py` (`test_loop`)
- [P1|ouvert] Juger les pochettes dans la section « Pochettes » (admin) et relancer le script de suivi : `webradio/tools/cover_review_watch.py` avait été lancé en arrière-plan pendant la nuit, la session a été interrompue depuis (ComfyUI aussi peut être resté démarré, il occupe de la VRAM)
  - fait quand: les pochettes sont validées ou abandonnées, le script est arrêté (`webradio/logs/stop_cover_review.request`), ComfyUI est arrêté avant une génération musicale
  - réf: `tests_manuels.md` n°16, `webradio/covers_review.py`, `webradio/tools/cover_review_watch.py`
- [P1|ouvert] Valider ou refuser les règles tirées des morceaux négatifs (voix anglaise 9 % de négatifs contre 62 % en français, captions à éviter, styles) et relire le diff de préférences recalculé (867 votes pris en compte avec l'archive, 395 différences) : `diff_preferences.py --appliquer` seulement après accord
  - fait quand: règles acceptées (reportées dans le skill `generation-morceaux` ou `regles_modeles.json`), refusées ou corrigées, et `preferences.json` existe ou la proposition est écartée
  - réf: `DOCUMENTATION/apprentissage/propositions/regles_negatifs_2026-10-15.md`, `DOCUMENTATION/apprentissage/propositions/diff_2026-10-15.txt`, `DOCUMENTATION/APPRENTISSAGE.md`
- [P2|ouvert] Analyser les votes des auditeurs quand il y en aura (`python webradio/tools/user_votes_report.py --min-votes N`) : écarter les votes de l'appareil du développeur, comparer au score de gestion (colonne « désaccord »), décider suppression ou pondération ; ces votes n'agissent pas sur la rotation
  - fait quand: un rapport est produit sur de vrais votes et les décisions (suppression, poids) sont prises ou écartées
  - réf: `webradio/user_votes.json` (non versionné), `webradio/tools/user_votes_report.py`, `webradio/server.py` (`set_user_vote`)
- [P3|ouvert] Décider si le vote unique par cookie suffit (un auditeur qui efface ses cookies ou change d'appareil revote) et si les votes auditeurs doivent un jour influer sur la rotation
  - fait quand: décision prise et appliquée
  - réf: `webradio/server.py` (`_voter_id`, `VOTER_COOKIE_USER`)
- [P2|ouvert] Tester la régénération réelle d'une pochette par `cover_review_watch.py` (verdict « À refaire », graine différente, retour en fin de file) : jamais exécutée avec ComfyUI, seulement avec un générateur simulé
  - fait quand: une pochette marquée « À refaire » est régénérée, revient en attente de validation avec la mention « refaite 1/3 fois »
  - réf: `webradio/tools/cover_review_watch.py`, `webradio/tests/test_covers_review.py`
- [P2|ouvert] Rendre la suppression de morceau résistante au verrouillage Windows : `os.replace` de `catalog_overrides.json` a échoué (PermissionError) après la purge des fichiers du morceau (incident `electro-atmospherique:3`, 2026-10-15) ; marquer le morceau supprimé avant de purger ou relancer `os.replace`
  - fait quand: une suppression interrompue ne laisse ni morceau sans fichiers au catalogue ni enregistrement d'apprentissage perdu ou en double
  - réf: `webradio/radio_engine.py` (`edit_catalog`, `_purge_track`), `DOCUMENTATION/apprentissage/suppression_2026-10-15.json`
- [P3|ouvert] Décider du sort de la sauvegarde `DOCUMENTATION/apprentissage/radio_db_avant_remise_a_zero_2026-10-15.db` (1,7 Mo, non versionnée) : versionner, ajouter au `.gitignore` ou stocker ailleurs
  - fait quand: l'utilisateur tranche
  - réf: `DOCUMENTATION/apprentissage/votes_archive/`, `.gitignore`
- [P1|ouvert] Écouter les 19 versions Funky Yogi (tests 47 à 65 : 10 textes en 3 styles, dont 3 textes avec chœurs base/v1/v2/v3) et voter ; juger les chœurs ; la première boucle d'apprentissage en dépend
  - fait quand: les 19 versions sont votées, les moyens de chœurs notés `teste` ou `echec` dans `regles_modeles.json` après accord, un bilan par texte rédigé (roadmap phase 6)
  - réf: `roadmap_ecriture_humaine.md` phase 6, `DOCUMENTATION/apprentissage/plan_run.json`, `DOCUMENTATION/apprentissage/propositions/textes-funky-yogi-photos.md`, `webradio/tests_state.json`
- [P1|ouvert] Clip promo L'Invariable (17 octobre 2026) : retenus dans le dossier `clip_promo\musique\retenus\` de SerenIATech (Eurodisco graine 2026, cover « Ça m'énerve » graine 42) ; écouter, améliorer refrain et variations mélodiques, choisir pour le clip ; droits du morceau de Helmut Fritz à trancher avant tout usage public du cover
  - fait quand: un morceau est choisi pour le clip, ses paroles finalisées dans `paroles_clip.md`, et la question des droits du cover tranchée
  - réf: `webradio/tests_ace/clip_atelier_invariable/config.json` (cas 7 à 22), `webradio/playlists/creation-francaise/`
- [P2|ouvert] Tester `src_audio` (cover) et `reference_audio` de `ace_worker.py` sur un cas réel suivi d'une écoute, et contrôler qu'un cas sans ces champs se comporte comme avant (pytest `webradio/tests`)
  - fait quand: pytest `webradio/tests` passe et le cover est écouté
  - réf: `webradio/ace_worker.py` (`prepare_audio`, `task_type`), `webradio/tests_ace/clip_atelier_invariable/outputs/`
- [P2|ouvert] Aligner les descriptions de playlist avec le nombre réel de morceaux après les suppressions du 2026-10-15 (`instrumental` dit encore « 21 morceaux », `disco-en` inchangée, autres playlists amputées)
  - fait quand: les descriptions de `playlists.json` indiquent le nombre de morceaux réel
  - réf: `webradio/playlists.json`, `DOCUMENTATION/apprentissage/suppression_2026-10-15.json`
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
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (écran verrouillé avec Web Audio, section Tests, titrage, police, cycle visuel, pubs, jingles, admin, boutons plier/déplier n°15, section Pochettes n°16, bouton Test n°17)
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
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP`), la section « Tests » (ou la verrouiller), remplacer `DEV_UNIFIED = True` en dur par un réglage explicite, remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, refermer `/api/dynamics` avec une UI auditeur séparée, retirer ou verrouiller le bouton « Test » et la section « Pochettes », fermer `/listen.html` et `/radio.html` sur le port 5000 exposé par le tunnel (servis tant que `DEV_UNIFIED` est actif ; redirection de `/listen.html` vers `/user.html` pour les visiteurs sans cookie admin proposée, non faite)
  - fait quand: aucun saut public possible, `DEV_UNIFIED` piloté, aucun nom d'artiste public, dynamique et Tests refermés dans l'UI auditeur
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.4, 3.6, 3.7 et 5.5, `webradio/server.py`
- [P2|ouvert] Confirmer deux changements du répertoire de travail non faits pendant ces sessions : seuil `0.688` dans `jlayout` (`webradio/motion.js`) et suppression du formulaire de commentaires et du contact dans `webradio/listen.html` (formulaire remis dans `user.html` et bloc « musique humaine » retiré des deux pages à la demande du 2026-10-18)
  - fait quand: l'utilisateur confirme ou demande la correction
  - réf: `git diff webradio/motion.js webradio/listen.html`, `AMELIORATIONS.md`
- [P2|ouvert] Choisir parmi les propositions de réaménagement de l'UI admin et décider du sort de `ui.html`
  - fait quand: l'utilisateur a tranché et les choix retenus sont appliqués
  - réf: `webradio/radio.html`, `webradio/ui.html`
- [P3|ouvert] Décider du versionnage des MP3 conservés dans `TEXTES/artistes/Marie/` (2 instrus et `tops_instrus/`, environ 3 à 3,6 Mo chacun) : non commités à cette clôture car la règle est de ne pas versionner l'audio
  - fait quand: l'utilisateur tranche entre versionner, ajouter au `.gitignore` ou stocker ailleurs
  - réf: `TEXTES/artistes/Marie/INDEX.md`, `.gitignore`
- [P3|ouvert] Poursuivre la génération musicale en rotation (`/start_generation`, service `generation` arrêté ; `series.txt` nettoyé le 2026-10-15 des playlists supprimées ; contrôle automatique à la suppression d'une playlist encore à faire) et retirer de « idée de playlist.md » chaque entrée terminée
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md`
- [P3|ouvert] Mise en ligne permanente : VPS Linux (systemd, Caddy ou Cloudflare, sous-domaine `radio.serenia-tech.fr`, rsync des mp3) ; Vercel, Render gratuit et Netlify écartés ; fonctionnement du serveur sous Linux non testé
  - fait quand: décision de déployer prise et VPS commandé, ou piste abandonnée
  - réf: `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Roadmap écriture humaine : phase 6 en cours (attente des écoutes des 19 versions Funky Yogi) ; `paroles.md` pas encore dans le run. Roadmap `roadmap_nuit_autonome.md` : phases 1 à 8 exécutées le 2026-10-15 ; à archiver sur accord.
- UI auditeur : `webradio/user.html` (même `listen.js`, drapeau `CREAZIK_USER_UI`) est la page d'accueil du port 5000 ; le tunnel `vertia-test.serenia-tech.fr` pointe sur `localhost:5000` (contrôlé en HTTP : `/` et `/user.html` servent l'UI auditeur, `/listen.html` l'UI dev). Artefact de revue : onglet v1 avec capture, onglet v2 sans capture ; 5 questions répondues le 2026-10-17.
- Votes auditeurs à part : `webradio/user_votes.json`, cookie `creazik_voter_u`, en-tête `X-Creazik-Ui: user` ; sans effet sur `votes.json`, `radio.db` ni la rotation ; l'UI auditeur ne reçoit que ses propres votes.
- Pubs et jingles Traveling Sound supprimés (contenu, catégorie, bloc « musique humaine », image) ; fichiers récupérables dans git.
- Moteur : un morceau courant périmé est abandonné au chargement de l'état (test ajouté, 41 tests passent en 3 min 40) ; serveur relancé plusieurs fois les 17 et 18 octobre.
- Le navigateur de test (Playwright) ne répondait plus aux deux dernières tentatives ; ne pas en dépendre sans le relancer.
- Avant une génération GPU, vérifier la VRAM libre (environ 1 Go pris par Windows) et que ComfyUI est arrêté.

# Session du 2026-10-23

## Décisions prises
- UI auditeur séparée (`webradio/user.html`) servie à la racine du port 5000 ; sans Suivant, Slow/Medium/High, remise à zéro ni administration ; pouces à vote unique exclusif ; commentaires restaurés ; dev (`/listen.html`, `/radio.html`) inchangé.
- Votes auditeurs collectés à part, sans effet sur la rotation, pour analyse manuelle avant toute suppression ou pondération.
- Pubs et jingles Traveling Sound supprimés (demande de l'utilisateur : toutes les pubs).
- Revue de l'UI auditeur dans un artefact claude.ai (modèle SHORTS) ; lecture du son dans l'artefact impossible.

## Livrables produits ou modifiés
- `webradio/user.html`, `webradio/listen.js` (`USER_UI`), `webradio/server.py` (racine, `/user.html`, votes auditeurs séparés) : fonctionnels, vérifiés en HTTP, page v2 jamais chargée dans un navigateur.
- `webradio/radio_engine.py` + test : rattrapage en accéléré après arrêt corrigé.
- `webradio/tools/user_votes_report.py` + 3 tests : rapport des votes auditeurs (lecture seule), jamais lancé sur de vrais votes.
- `revue_ui_user/` : artefact de revue (https://claude.ai/artifact/SCjtgCNBYAQhEMr56zaFuU).
- `radio_content.json`, `playlists.json`, `jingles/traveling-sound/` : pubs Traveling Sound retirées.

## Hypothèses validées / invalidées
- VALIDE : `/` du port 5000 et du tunnel servent l'UI auditeur (HTTP) ; vote, remplacement et remise à zéro côté serveur sur un morceau réel ; `votes.json` inchangé ; 41 tests passent.
- INVALIDE : afficher le son de la radio dans l'artefact -> pivot vers écoute sur localhost ou maquette (choix en attente).
- EN ATTENTE : v2 jamais chargée dans un navigateur ni sur iPhone ; rapport de votes sur de vrais votes ; cause du téléphone qui affichait l'UI dev (URL `/listen.html` supposée, non confirmée).

## Prochaine étape exacte
Charger `user.html` dans un navigateur et sur iPhone via la racine du tunnel, contrôler pouces, commentaires et absence de pubs Traveling Sound, puis publier la capture v2 dans l'artefact.

## Question bloquante pour la session suivante
Écoute du son pour la revue : option 1 (localhost) ou option 2 (maquette dans l'artefact avec quelques morceaux téléversés) ?
