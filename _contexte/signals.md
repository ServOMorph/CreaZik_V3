# Signals — CreaZik_V3   (MAJ 2026-11-05, fin de session)

## Actions ouvertes
- [P1|ouvert] Lever la pause GPU et tester pour de vrai les plugins image (admin) et « Créer un morceau » : `webradio/gpu_pause.flag` suspend les files depuis le 2026-10-30 (entraînement v9 de la session LLM) ; le 2026-11-01 la carte n'affichait que 957 Mo utilisés, mais la fin de v9 n'est pas confirmée par la session LLM
  - fait quand: fin de v9 confirmée, `gpu_pause.flag` supprimé, une image admin et un morceau d'auditeur réels générés et diffusés
  - réf: `file_agents.md` (section Pause GPU), `webradio/gpu.py`, `tests_manuels.md` n°23
- [P1|ouvert] Contrôles manuels de l'UI unique et des plugins, navigateur puis iPhone, via `https://vertia-test.serenia-tech.fr/` : profils anonyme / Olive / admin, plugins image, morceau, jingle texte, boutons ⏮⏭ et Précédent/Suivant (tous), cartes admin, jingles urgents ; écouter la prononciation des jingles de plugins (Kokoro 52 s pour 6 s d'audio) ; la v2 de l'UI auditeur n'a jamais été vue sur iPhone
  - fait quand: les sections 1 à 4 et 18 à 24 de `tests_manuels.md` sont vidées par contrôles réels, défauts corrigés ou consignés
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/plugins/`, `webradio/profiles/`
- [P1|ouvert] Stop motion : piste « robot batteur » retenue (3 poses par seconde + images de transition générées, 6 images par seconde) ; décider où l'utiliser (visuel de l'UI auditeur, pub, autre) puis l'intégrer ; planche à jour : https://claude.ai/artifact/TpxwZoKDTNRPEc4qVBinoD
  - fait quand: l'utilisateur choisit l'usage et l'animation est intégrée ou la piste abandonnée
  - réf: `webradio/tests_visuels/stop_motion/4_robot_batteur/` (dossier ignoré par git), `assemble.py`, `run_transitions.py`, `webradio/REGLES_GENERATION_DEV.md` section 4
- [P1|ouvert] Trancher comment relire l'UI auditeur avec le son : une page d'artefact ne peut ni appeler la radio locale ni l'intégrer (option 1 : revue dans l'artefact et écoute sur `localhost:5000` ; option 2 : maquette jouant quelques morceaux téléversés, hors direct)
  - fait quand: l'utilisateur choisit une option et elle est appliquée ou écartée
  - réf: https://claude.ai/artifact/SCjtgCNBYAQhEMr56zaFuU, `revue_ui_user/revue_ui_user.html`
- [P1|ouvert] Arrêter le mode Test (bouton « Arrêter le test », admin) : `test_loop` était encore à `true` au dernier contrôle (2026-10-18) et la radio ne joue alors que la playlist blues-rock ; puis contrôler que cette playlist (6 morceaux, poids par défaut 5) passe avec les autres
  - fait quand: `/api/radio/state` indique `test_loop` à `false` et la playlist `blues-rock-guitare` passe à l'antenne dans la programmation normale
  - réf: `tests_manuels.md` n°17, `webradio/radio_engine.py` (`test_loop`)
- [P1|ouvert] Juger les pochettes dans la section « Pochettes » (admin) et relancer le script de suivi : `webradio/tools/cover_review_watch.py` avait été lancé en arrière-plan pendant la nuit du 2026-10-15, la session a été interrompue depuis
  - fait quand: les pochettes sont validées ou abandonnées, le script est arrêté (`webradio/logs/stop_cover_review.request`), ComfyUI est arrêté avant une génération musicale
  - réf: `tests_manuels.md` n°16, `webradio/covers_review.py`, `webradio/tools/cover_review_watch.py`
- [P1|ouvert] Valider ou refuser les règles tirées des morceaux négatifs (voix anglaise 9 % de négatifs contre 62 % en français, captions à éviter, styles) et relire le diff de préférences recalculé (867 votes pris en compte avec l'archive, 395 différences) : `diff_preferences.py --appliquer` seulement après accord
  - fait quand: règles acceptées (reportées dans le skill `generation-morceaux` ou `regles_modeles.json`), refusées ou corrigées, et `preferences.json` existe ou la proposition est écartée
  - réf: `DOCUMENTATION/apprentissage/propositions/regles_negatifs_2026-10-15.md`, `DOCUMENTATION/apprentissage/propositions/diff_2026-10-15.txt`, `DOCUMENTATION/APPRENTISSAGE.md`
- [P1|ouvert] Écouter les 19 versions Funky Yogi (tests 47 à 65 : 10 textes en 3 styles, dont 3 textes avec chœurs base/v1/v2/v3) et voter ; juger les chœurs ; la première boucle d'apprentissage en dépend
  - fait quand: les 19 versions sont votées, les moyens de chœurs notés `teste` ou `echec` dans `regles_modeles.json` après accord, un bilan par texte rédigé (roadmap phase 6)
  - réf: `roadmap_ecriture_humaine.md` phase 6, `DOCUMENTATION/apprentissage/plan_run.json`, `DOCUMENTATION/apprentissage/propositions/textes-funky-yogi-photos.md`, `webradio/tests_state.json`
- [P1|ouvert] Clip promo L'Invariable (17 octobre 2026) : retenus dans le dossier `clip_promo\musique\retenus\` de SerenIATech (Eurodisco graine 2026, cover « Ça m'énerve » graine 42) ; écouter, améliorer refrain et variations mélodiques, choisir pour le clip ; droits du morceau de Helmut Fritz à trancher avant tout usage public du cover
  - fait quand: un morceau est choisi pour le clip, ses paroles finalisées dans `paroles_clip.md`, et la question des droits du cover tranchée
  - réf: `webradio/tests_ace/clip_atelier_invariable/config.json` (cas 7 à 22), `webradio/playlists/creation-francaise/`
- [P1|ouvert] Appliquer techniquement la validation préalable : envoyer les nouvelles générations vers les Tests et bloquer leur ajout à la diffusion ou à la rotation sans demande explicite, sauf les annonces radio (jingles urgents) et les créations d'auditeurs, diffusées directement à la demande de l'utilisateur
  - fait quand: le pipeline automatique produit d'abord des fichiers accessibles dans les Tests et aucun chemin n'ajoute un nouveau contenu à la diffusion sans demande de l'utilisateur, hors les deux exceptions
  - réf: `AGENTS.md` section Spécificités projet, `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 2.6 et 3.11, `.claude/skills/generation-morceaux/SKILL.md` étapes 6 et 7
- [P1|ouvert] Écouter la grille de voix de femme (section Tests : tests 26 à 31 en 135 s et 39 à 44 en 60 s, texte corrigé) et trancher si une version garde la voix de femme du début à la fin ; en tirer la règle du skill `generation-morceaux`
  - fait quand: une version à voix de femme stable est retenue ou la piste est abandonnée, et le skill et `REGLES_GENERATION_DEV.md` section 6 sont mis à jour
  - réf: `webradio/playlists/tests-ace/outputs/playlist_results.json`, `.claude/skills/generation-morceaux/SKILL.md`, `tests_manuels.md` n°5
- [P1|ouvert] Démo T01 « Arroser Les Roses » : version 18 retenue (voix d'homme) ; écouter sa fin et décider quoi envoyer à l'auteur (texte adapté « posté », « zoublie », à lui signaler) ; l'accord écrit de l'auteur n'a pas été demandé et le statut `VALIDE` reste interdit
  - fait quand: la version à envoyer est confirmée à l'écoute (`tests_manuels.md` n°6) et l'envoi à l'auteur est décidé
  - réf: `webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3`, `TEXTES/liste_attente.md`, `TEXTES/usage_prive/INDEX.md`
- [P1|ouvert] Compléter la commande `/generate_lyrics` (agent `textes`) : grille rimes, répétitions, clichés en plus de `check_lyrics.py`, et lot de paroles écouté et jugé
  - fait quand: un lot test de paroles est généré dans `TEXTES/` puis écouté et jugé
  - réf: `.claude/commands/generate_lyrics.md`, `TEXTES/tools/check_lyrics.py`, `TEXTES/agent_role.md`
- [P1|ouvert] Écouter les jingles 1 à 5 de la catégorie WebRadio régénérés avec « IA » (Whisper entend « il y a ») et décider : valider puis régénérer les 14 autres (environ 17 min), ou changer la graphie
  - fait quand: prononciation validée et les 19 jingles WebRadio disent « CréaZik IA WebRadio » (ou graphie retenue appliquée)
  - réf: `D:\ServOMorph\TTS_Local\jingles_ia_batch.py`, `D:\ServOMorph\TTS_Local\jingles_ia_wav\`, `D:\ServOMorph\TTS_Local\jingles_old_mp3\`, `webradio/jingles/webradio/outputs/`
- [P1|ouvert] Valider les jingles SérénIA Tech (5 textes) et la prononciation « Sérénia Tèk » / « Traveling Sound Ouèbe Radio »
  - fait quand: textes et prononciation validés ou corrigés puis régénérés
  - réf: `D:\ServOMorph\TTS_Local\jingles_pub_texts.json`, `D:\ServOMorph\TTS_Local\jingles_pub_batch.py`, `D:\ServOMorph\TTS_Local\jingles_pub_finalize.py`
- [P2|ouvert] Profil « Olivier » : figer l'UI telle que développée pour la démo (partiellement couvert par le profil `traveling-sound`) ; chaque démo suivante = un nouveau profil dans `webradio/profiles/`
  - fait quand: l'utilisateur confirme que le profil `traveling-sound` suffit ou qu'une copie figée est créée
  - réf: `webradio/profiles/traveling-sound.json`, `file_agents.md`
- [P2|ouvert] Confirmation par la session VibeObs de l'intégration du template de délégation Codex/OpenCode (message envoyé le 2026-10-31, aucune réponse) ; aucun appel réel depuis une copie installée
  - fait quand: VibeObs confirme l'intégration ou l'utilisateur écarte le sujet
  - réf: `_templates/delegation/README.md`, `file_agents.md`
- [P2|ouvert] Mettre à jour `.claude/agents/ui-design.md` (cite encore `listen.html`, supprimée le 2026-10-31) et examiner l'octet NUL préexistant de `webradio/listen.js` (git le traite comme binaire)
  - fait quand: l'agent cite les pages actuelles et `listen.js` est lu comme texte par git
  - réf: `.claude/agents/ui-design.md`, `webradio/listen.js`
- [P2|ouvert] Analyser les votes des auditeurs quand il y en aura (`python webradio/tools/user_votes_report.py --min-votes N`) : écarter les votes de l'appareil du développeur, comparer au score de gestion, décider suppression ou pondération ; ces votes n'agissent pas sur la rotation ; un vote de test a été retiré de `user_votes.json` le 2026-10-31
  - fait quand: un rapport est produit sur de vrais votes et les décisions (suppression, poids) sont prises ou écartées
  - réf: `webradio/user_votes.json` (non versionné), `webradio/tools/user_votes_report.py`, `webradio/server.py` (`set_user_vote`)
- [P2|ouvert] Tester la régénération réelle d'une pochette par `cover_review_watch.py` (verdict « À refaire », graine différente, retour en fin de file) : jamais exécutée avec ComfyUI, seulement avec un générateur simulé
  - fait quand: une pochette marquée « À refaire » est régénérée, revient en attente de validation avec la mention « refaite 1/3 fois »
  - réf: `webradio/tools/cover_review_watch.py`, `webradio/tests/test_covers_review.py`
- [P2|ouvert] Rendre la suppression de morceau résistante au verrouillage Windows : `os.replace` de `catalog_overrides.json` a échoué (PermissionError) après la purge des fichiers du morceau (incident `electro-atmospherique:3`, 2026-10-15) ; marquer le morceau supprimé avant de purger ou relancer `os.replace`
  - fait quand: une suppression interrompue ne laisse ni morceau sans fichiers au catalogue ni enregistrement d'apprentissage perdu ou en double
  - réf: `webradio/radio_engine.py` (`edit_catalog`, `_purge_track`), `DOCUMENTATION/apprentissage/suppression_2026-10-15.json`
- [P2|ouvert] Tester `src_audio` (cover) et `reference_audio` de `ace_worker.py` sur un cas réel suivi d'une écoute, et contrôler qu'un cas sans ces champs se comporte comme avant (pytest `webradio/tests`)
  - fait quand: pytest `webradio/tests` passe et le cover est écouté
  - réf: `webradio/ace_worker.py` (`prepare_audio`, `task_type`), `webradio/tests_ace/clip_atelier_invariable/outputs/`
- [P2|ouvert] Aligner les descriptions de playlist avec le nombre réel de morceaux après les suppressions du 2026-10-15 (`instrumental` dit encore « 21 morceaux », `disco-en` inchangée, autres playlists amputées)
  - fait quand: les descriptions de `playlists.json` indiquent le nombre de morceaux réel
  - réf: `webradio/playlists.json`, `DOCUMENTATION/apprentissage/suppression_2026-10-15.json`
- [P2|ouvert] Contrôler dans le navigateur l'UI Tests (texte sur plusieurs lignes, plier/déplier) et la diffusion de `instrumental:22` et `creation-francaise:1`
  - fait quand: UI Tests contrôlée, les deux morceaux entendus à l'antenne ou signalés défaillants
  - réf: `tests_manuels.md` n°9 à 13, `webradio/listen.js`, `webradio/services.ps1`
- [P2|ouvert] Tester les modifications de pochettes sans texte et de traçabilité d'`ace_worker.py` commitées sans test complet : une pochette sur une playlist (`cover_batch.py --playlist`), puis la reprise d'une piste déjà générée avec le nouveau nom de fichier horodaté (risque de régénération), et la compatibilité avec `compress_audio.py` et la suppression de morceau
  - fait quand: une pochette est générée avec le nouveau prompt, une relance n'écrase ni ne régénère une piste `generated`, et la compression et la suppression retrouvent les fichiers nommés avec horodatage et graine
  - réf: `webradio/ace_worker.py` (`write_generation_trace`), `webradio/tools/cover_gen.py`, `webradio/tools/cover_batch.py`, `webradio/compress_audio.py`
- [P2|ouvert] Écouter et donner son avis sur le test 45 (Funky Yogi nu-disco) et le test 46 (Marie rap mélodique avec voix) de la section Tests
  - fait quand: avis donné et réglages ou graine retenus consignés, `tests_manuels.md` n°7 et n°8 vidés
  - réf: `tests_manuels.md` n°7 et n°8, `webradio/tests_ace/funky_yogi/`, `webradio/tests_ace/marie_rap/`
- [P2|ouvert] Câbler un protocole d'apprentissage : `webradio/learning/morceaux_rejetes.jsonl` n'est lu par aucun code de génération ; relier votes et commentaires des Tests, prompt et graine à des réglages recommandés dans le skill
  - fait quand: une procédure (script ou étape du skill) relit les votes des Tests et les rejets pour proposer les réglages d'une prochaine génération
  - réf: `webradio/tests_state.json`, `webradio/learning/morceaux_rejetes.jsonl`, `.claude/skills/generation-morceaux/SKILL.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP`), la section « Tests » (ou la verrouiller), remplacer `DEV_UNIFIED = True` en dur par un réglage explicite (le passer à faux coupe toute l'administration du port 5000 depuis l'UI unique), retirer cadenas et lien admin de l'UI auditeur, ajouter des quotas aux plugins image et morceau, renforcer les mots de passe admin et Olive, remplacer les noms d'artistes des titres de playlists par des genres, trancher l'exposition des boutons Renommer/Supprimer, refermer `/api/dynamics`, retirer ou verrouiller le bouton « Test » et la section « Pochettes »
  - fait quand: aucun saut public possible, `DEV_UNIFIED` piloté, aucun nom d'artiste public, dynamique, Tests et quotas en place, mots de passe renforcés
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.4, 3.6, 3.7, 3.12 et 5.5, `webradio/server.py`
- [P2|ouvert] Confirmer le seuil `0.688` de `jlayout` dans `webradio/motion.js` (corriger ou assumer)
  - fait quand: l'utilisateur confirme ou demande la correction
  - réf: `git diff webradio/motion.js`, `AMELIORATIONS.md`
- [P2|ouvert] Choisir parmi les propositions de réaménagement de l'UI admin et décider du sort de `ui.html`
  - fait quand: l'utilisateur a tranché et les choix retenus sont appliqués
  - réf: `webradio/radio.html`, `webradio/ui.html`
- [P3|ouvert] Décider si le vote unique par cookie suffit (un auditeur qui efface ses cookies ou change d'appareil revote) et si les votes auditeurs doivent un jour influer sur la rotation
  - fait quand: décision prise et appliquée
  - réf: `webradio/server.py` (`_voter_id`, `VOTER_COOKIE_USER`)
- [P3|ouvert] Décider du sort des fichiers non versionnés laissés volontairement hors du commit : sauvegarde `DOCUMENTATION/apprentissage/radio_db_avant_remise_a_zero_2026-10-15.db` (1,7 Mo), MP3 de `TEXTES/artistes/Marie/` (2 instrus et `tops_instrus/`), `_archive_docs/`, `ad.png`, `liste_musiques_queue.md`, `webradio/jingles/annonces/` (annonces diffusées), journaux et sorties de `webradio/tests_ace/clip_atelier_invariable/`, `TEXTES/Marie-1.md` : versionner, ajouter au `.gitignore` ou stocker ailleurs
  - fait quand: l'utilisateur tranche et `git status` ne montre plus de résidus sans décision
  - réf: `.gitignore`, `TEXTES/artistes/Marie/INDEX.md`, `DOCUMENTATION/apprentissage/votes_archive/`
- [P3|ouvert] Poursuivre la génération musicale en rotation (`/start_generation`, service `generation` arrêté ; `series.txt` nettoyé le 2026-10-15 ; contrôle automatique à la suppression d'une playlist encore à faire) et retirer de « idée de playlist.md » chaque entrée terminée
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md`
- [P3|ouvert] Mise en ligne permanente : VPS Linux (systemd, Caddy ou Cloudflare, sous-domaine `radio.serenia-tech.fr`, rsync des mp3) ; Vercel, Render gratuit et Netlify écartés ; fonctionnement du serveur sous Linux non testé
  - fait quand: décision de déployer prise et VPS commandé, ou piste abandonnée
  - réf: `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Le port 5000 est occupé par le serveur de cartes d'un autre projet (`challenge_magic/serveur_cartes/app.py`, session tierce) ; CréaZik n'est pas lancé. L'utilisateur a refusé qu'on le ferme (2026-11-01). Relancer CréaZik exige de libérer le port ou de le décider avec l'utilisateur.
- Pause GPU : `webradio/gpu_pause.flag` en place ; les files d'images et de morceaux d'auditeurs attendent. Une session « Fiches_IME » utilise aussi la carte (Qwen) : se coordonner par message avant toute génération.
- Roadmap écriture humaine : phase 6 en cours (écoute des 19 versions Funky Yogi). `roadmap_nuit_autonome.md` : phases 1 à 8 exécutées le 2026-10-15 ; à archiver sur accord.
- UI unique sur le port 5000 : profils, comptes (`user_accounts.json` hors git), plugins déclaratifs ; `/listen.html` et `/suivi.html` redirigent vers `/` ; le tunnel `vertia-test.serenia-tech.fr` pointe sur `localhost:5000`. Suivi des agents : `suivi_travail/etat.json` (carte admin « Suivi du travail ») et `file_agents.md`.
- Délégation : Codex via `_codex/run_codex.ps1`, OpenCode gratuit via `_codex/run_opencode.ps1` (briefs autonomes) ; jamais de génération d'image ou de musique par un service cloud.
- Commandes `/tel` et `/pc` (mode téléphone), `/jingle` (annonce) ; annonce radio uniquement pour un changement visible dans l'UI auditeur (règles 3.11).
- Avant une génération GPU, vérifier la VRAM libre (environ 1 Go pris par Windows) et que ComfyUI est arrêté.

# Session du 2026-11-05

## Décisions prises
- UI unique sur le port 5000 en plugins (profils `classique` et `traveling-sound`, comptes par identifiant, admin avec ses cartes et boutons Précédent/Suivant globaux) ; plugins image et morceau d'auditeurs, jingle texte en admin ; tout en file GPU sans quota (choix de l'utilisateur).
- Création d'auditeur diffusée à tous, précédée d'un jingle ; annonces radio = jingles urgents, hors gestion IA/code.
- Délégation à Codex et OpenCode gratuit, template réutilisable `_templates/delegation/`.
- Stop motion : piste « robot batteur » retenue, 3 poses par seconde + images de transition générées ; quatre autres pistes supprimées.
- Pause GPU maintenue à la fin de la session de travail ; port 5000 laissé à l'autre projet.

## Livrables produits ou modifiés
- Commit `7181805` (84 fichiers, sans push) : UI unique, profils, comptes, plugins, files image/morceau, délégation, commandes `/jingle` `/tel` `/pc` : 99 tests passés selon l'agent, smoke test admin 28/28 local et tunnel.
- `webradio/tests_visuels/stop_motion/` (ignoré par git) : robot batteur (7 poses, 7 transitions), `assemble.py`, `run_transitions.py` ; planche republiée.
- `file_agents.md`, `webradio/REGLES_GENERATION_DEV.md` (sections 3.10 à 3.12, 4, 6) : mis à jour.

## Hypothèses validées / invalidées
- VALIDE : connexion admin au formulaire, anonyme/Olive/admin au navigateur, routes admin refusées à Olive ; 35 transitions générées (65 s chacune) ; cadence de 3 poses par seconde convient à l'utilisateur.
- INVALIDE : fondu enchaîné entre poses -> pivot vers de vraies images générées, demandé par l'utilisateur.
- EN ATTENTE : rien écouté, iPhone non testé, plugins image et morceau jamais testés après la pause GPU, fin de v9 non confirmée.

## Prochaine étape exacte
Décider de l'usage du robot batteur animé, confirmer la fin de v9 avec la session LLM puis supprimer `gpu_pause.flag` et tester image admin et morceau d'auditeur ; ensuite contrôles manuels 18 à 24 sur iPhone.

## Question bloquante pour la session suivante
Où utiliser l'animation du robot batteur (visuel de l'UI auditeur, pub, autre) ?
