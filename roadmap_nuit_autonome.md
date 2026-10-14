# Roadmap nuit autonome — nettoyage, outils UI, playlist blues-rock

Exécutant : Haiku, seul, sans l'utilisateur (endormi). Début : 2026-10-15 00:01. Aucune confirmation n'est attendue : ne jamais poser de question, décider selon ce document. Pas de checkpoint `/compact` dans cette roadmap (décision explicite de l'utilisateur) : chaque phase est autoportante, relire ce fichier et le journal en tête de chaque phase.

## Règles d'exécution (à relire avant chaque phase)
- Langue française, ton synthétique, pas d'emojis ni de commentaires décoratifs dans le code. Ne jamais affirmer qu'une chose fonctionne sans l'avoir vérifiée par un outil (test, lecture de fichier, requête).
- Lire `webradio/REGLES_GENERATION_DEV.md` avant de commencer. Écrire les scripts de plusieurs lignes avec l'outil d'écriture de fichiers, pas avec des heredocs.
- Interdits : ajouter un morceau à la diffusion ou à la rotation en dehors de ce qui est écrit ici ; passer un texte protégé à `VALIDE` ; écrire dans `memory/` ou `.claude/memory.md` ; modifier `DOCUMENTATION/apprentissage/preferences.json` ou `regles_modeles.json` ; lancer `diff_preferences.py --appliquer` ; `git push` ; versionner un MP3, un WAV ou un fichier de `outputs/`.
- Redémarrer le serveur est autorisé sans demande : `.\services.ps1 restart -Only serveur` (depuis `webradio/`). Le faire seulement si du code Python a changé, une fois par phase au plus, et consigner l'heure dans le journal. Après un redémarrage, contrôler `/api/radio/state` : le moteur peut rattraper son retard en accéléré.
- GPU : ne jamais faire tourner la génération musicale et ComfyUI (pochettes) en même temps. Avant une génération, vérifier la VRAM libre (`nvidia-smi`). Surveiller dans le journal ACE la ligne `auto-enabling CPU VAE decode`.
- Chaque phase : coder, écrire et lancer les tests pertinents (`python -m pytest webradio/tests`), puis un commit en français (message `feat`/`fix`/`chore(<sujet>): ...`, fichiers sensibles ou volumineux exclus, avec la ligne d'attribution `Co-Authored-By` demandée par le système). Pas de push.
- Blocage : si une étape échoue deux fois, écrire le blocage dans le journal (cause, commande, sortie utile), ne pas improviser, et passer à la phase suivante qui n'en dépend pas. Les dépendances sont indiquées par phase.
- Ne rien supprimer hors de la liste figée en phase 1.
- Les statuts des phases ne sont pas modifiés par Haiku (tâche de `/close`) : seul le journal en fin de fichier est mis à jour.

## Phase 1 - Analyse des morceaux négatifs [EN COURS]
Dépend de : rien.
0. Avant tout calcul : copier `DOCUMENTATION/apprentissage/preferences.proposition.json` vers `DOCUMENTATION/apprentissage/propositions/preferences.proposition_avant_2026-10-15.json` (la proposition de 395 différences que l'utilisateur n'a pas encore relue ne doit pas être perdue). Mentionner dans le journal qu'une version recalculée la remplace.
1. Copier `webradio/votes.json` vers `DOCUMENTATION/apprentissage/votes_archive/votes_avant_remise_a_zero_2026-10-15.json` (créer le dossier ; c'est l'archive qui servira aux calculs futurs, voir phase 3).
2. Figer la liste : tous les morceaux du catalogue diffusé (`webradio/playlists.json` sans les jingles, sans `tests-ace`, `tests-modeles`, `test`) dont le score dans `votes.json` (`tracks[clé].score`) est strictement négatif, 8 versions françaises « négatives » comprises. Score nul ou positif : conservé. Écrire `DOCUMENTATION/apprentissage/negatifs_2026-10-15.json` : clé, playlist, titre, prompt, paroles (chemin), durée, graine si connue, score, haut/bas, commentaires, fichiers existants sur disque.
3. Lancer `python OUTILS/apprentissage/calculer_preferences.py` puis `python OUTILS/apprentissage/diff_preferences.py` (sans `--appliquer`). Enregistrer le diff dans `DOCUMENTATION/apprentissage/propositions/diff_2026-10-15.txt`.
4. Analyser les morceaux négatifs contre les positifs : caption et tags, tempo et durée (`.feat.json`), type vocal/instrumental, langue, longueur et structure des paroles, paramètres ACE effectifs (sidecar `.metadata.json` quand il existe, sinon `config.json` de la playlist), graine, modèle. Seules les différences avec effectif d'au moins 5 morceaux par groupe comptent comme règles ; le reste est une hypothèse. Écrire `DOCUMENTATION/apprentissage/propositions/regles_negatifs_2026-10-15.md` : règles proposées (« éviter / préférer »), effectif et preuve de chacune, limites. Ne modifier ni le skill `generation-morceaux` ni `regles_modeles.json` : ce sont des propositions, soumises à l'accord de l'utilisateur.
Fait quand : le fichier de liste figée, le diff et les règles proposées existent et le nombre de morceaux listés est consigné dans le journal.

## Phase 2 - Suppression des morceaux négatifs et des playlists vides [TODO]
Dépend de : phase 1 (liste figée).
1. Lire `webradio/radio_engine.py` (`edit_catalog`, actions `delete_track`, `delete_playlist`) et `webradio/server.py` (route `POST /api/catalog`). Supprimer chaque morceau de la liste en réutilisant ce chemin (il efface le MP3, la pochette et les dérivés, masque l'entrée via `catalog_overrides.json`, garde le statut `generated` et verse le morceau dans `webradio/learning/morceaux_rejetes.jsonl`). Ne pas écrire de code de suppression parallèle.
2. Lire `webradio/radio_state.json` / `/api/radio/state` : si le morceau est en cours de diffusion (le serveur refuse), le sauter, le noter dans le journal avec sa clé, et le retenter en phase 8.
3. Supprimer aussi tout WAV, `.wav.feat.json`, `.wav.viz.json`, `.cover.png` et sidecar résiduel de ces morceaux encore présent dans `webradio/playlists/<id>/outputs/` (vérifier par listage après suppression ; les chemins sont dans le fichier de liste de la phase 1). Ne rien supprimer d'autre.
4. Toute playlist du catalogue diffusé qui n'a plus aucun morceau visible : `delete_playlist`, puis retirer son identifiant de `webradio/series.txt` (fins de ligne LF uniquement) pour que la rotation ne la régénère pas.
5. Contrôler : aucun morceau supprimé n'apparaît dans l'API du catalogue (`library`) ni dans `/api/radio/state` ; compter MP3/WAV restants des morceaux supprimés (attendu 0 hors morceau en cours).
Fait quand : le bilan (supprimés, sautés, playlists supprimées, fichiers restants) est dans le journal.

## Phase 3 - Remise à zéro des scores [TODO]
Dépend de : phases 1 et 2.
1. Sauvegarder `webradio/votes.json` et la table de votes de `webradio/radio.db` (copie de `radio.db` vers `DOCUMENTATION/apprentissage/radio_db_avant_remise_a_zero_2026-10-15.db`), sans écraser une sauvegarde existante.
2. Remettre à zéro tous les scores : pour chaque clé de `tracks`, mettre `{"up":0,"down":0,"score":0}` et vider les votes individuels des votants, avec le même mécanisme que `reset_votes` de `server.py`. Ne pas toucher aux commentaires, favoris, avis Slow/Medium/High ni à l'historique de diffusion.
3. Faire lire l'archive par l'apprentissage : modifier `OUTILS/apprentissage/calculer_preferences.py` pour que les votes cumulés d'un morceau soient la somme (haut et bas) des fichiers de `DOCUMENTATION/apprentissage/votes_archive/*.json` et de `webradio/votes.json` courant, par clé. Ajouter l'option `--sans-archive` (désactive les archives) et mettre à jour la liste des sources dans le docstring. Un morceau supprimé dont la clé n'existe plus au catalogue garde ses votes d'archive uniquement via `learning/morceaux_rejetes.jsonl`, comme aujourd'hui. Étendre `OUTILS/apprentissage/test_apprentissage.py` : (a) sommation archive plus votes courants, (b) archive absente ou vide, (c) `--sans-archive`. Lancer les tests, puis relancer `calculer_preferences.py` sur l'état remis à zéro et contrôler que l'effectif retrouvé est celui d'avant (comparer aux chiffres de la phase 1, à noter dans le journal). Ne pas lancer `--appliquer`. Mettre à jour `DOCUMENTATION/APPRENTISSAGE.md` (section Sources) avec ce fonctionnement.
4. Contrôler dans `radio_engine.py` et dans `webradio/tests/test_radio_engine.py` qu'un morceau dont le score est négatif n'est plus choisi en diffusion automatique (règle 3.3, il reste programmable à la main par l'admin). Si aucun test ne le couvre, l'écrire. Si le test échoue, corriger puis relancer.
Fait quand : tous les scores valent 0, la sauvegarde existe, le test du score négatif passe, le calcul des préférences retrouve l'effectif d'avant la remise à zéro grâce à l'archive.

## Phase 4 - Playlist blues-rock guitare claire (10 morceaux vocaux anglais) [TODO]
Dépend de : phase 3 terminée (la génération démarre ici, en arrière-plan, pendant les phases 5 à 7 qui n'utilisent pas le GPU).
1. Lire `.claude/skills/generation-morceaux/SKILL.md` et la configuration d'une playlist vocale existante (`webradio/playlists/blues-vocal/config.json`, `lyrics/`, entrée dans `webradio/playlists.json`, entrée dans `webradio/scenes_spec.json`).
2. Créer la playlist `blues-rock-guitare` : label « Blues-rock guitare claire », description sans nom d'artiste. Prompt de base descriptif : blues rock, clean electric guitar fingerstyle, melodic bass, laid-back mid-tempo, deep spoken-sung male vocal, English lyrics. Aucun nom d'artiste dans le titre, le caption, les paroles, l'affichage. 10 morceaux vocaux, langue `en`, durées 90 s plus ou moins 45 s (`set_durations.py`).
3. Inspiration (consigne interne, jamais publique ni reprise dans un texte) : l'ambiance et le tempo de dix titres très connus d'un groupe de blues-rock britannique des années 1978-1991, à savoir « Sultans of Swing », « Money for Nothing », « Brothers in Arms », « Walk of Life », « Romeo and Juliet », « Telegraph Road », « So Far Away », « Once Upon a Time in the West », « Private Investigations », « Calling Elvis ». Chaque morceau a un titre original, des paroles originales en anglais, sans recopier ni paraphraser de près aucun texte existant. Un titre trop long en original (par exemple « Telegraph Road », très long) est réduit à 135 s maximum.
4. Chaque morceau : paroles balisées pour ACE contrôlées par `python TEXTES/tools/check_lyrics.py` avant lancement ; graine explicite >= 0 ; statut dans `playlist_results.json`.
5. Exclusion de la rotation normale : poids 0 pour `blues-rock-guitare` dans `radio_settings.json` (clé `weights`), et ne pas l'ajouter à `series.txt`. Les morceaux restent dans `webradio/playlists/blues-rock-guitare/outputs/` et ne passent que par le bouton Test (phase 7).
6. Lancer la génération par `generate.py` ou `run_queue.py` pour cette playlist seulement (ne pas lancer `run_rotation.py`), en arrière-plan, après contrôle de la VRAM. Chaque piste : 3 tentatives ; échec technique = nouvelle graine ; après 3 échecs, abandonner la piste et noter dans le journal.
Fait quand : 10 MP3 existent (ou les pistes abandonnées sont listées dans le journal), les services `analyse` et `compression` ont produit les `.feat.json` et `.viz.json`, aucun WAV ne reste.

## Phase 5 - Boutons plier/déplier [TODO]
Dépend de : rien. Pas de GPU.
1. `webradio/listen.html` : dans le panneau `progPanel` (« Programmation »), ajouter un bouton « Tout plier / Tout déplier » qui agit sur les quatre blocs `<details data-fold="prog-played|prog-now|prog-queue|prog-library">`, en s'appuyant sur le fonctionnement existant de `data-fold` dans `listen.js`.
2. `webradio/radio.html` : ajouter un bouton global « Tout plier / Tout déplier » pour les sections de premier niveau (`secProgram`, `secPlay`, `secTrans`, `secDynamics`, `secJingle`, `secVisuals`, `secWeights`, `secStats`, `secAccount`), modelé sur `catFoldBtn` / `toggleAllCards()` (libellé qui bascule selon l'état).
3. Vérifier au navigateur (Playwright, largeur 375 px puis bureau) : bouton visible, bascule correcte, état des sections conservé après rechargement si le mécanisme existant le fait déjà.
4. Ajouter à `tests_manuels.md` le contrôle sur iPhone de ces deux boutons.
Fait quand : les deux boutons fonctionnent dans le navigateur, le contrôle iPhone est dans `tests_manuels.md`.

## Phase 6 - Revue des pochettes : page locale et script de suivi [TODO]
Dépend de : phases 2 et 5 (catalogue final). Écriture du code seulement ; l'exécution de la régénération est en phase 8.
1. État : `webradio/covers_review_state.json` (non versionné, à ajouter au `.gitignore`) : par clé de morceau, `status` (`pending`, `validated`, `redo`, `abandoned`), `redo_count`, `seed`, fichier courant.
2. Serveur (`webradio/server.py`, routes réservées à l'admin comme `/api/tests*`) : liste des pochettes à relire (une à la fois, ordre stable), enregistrement du verdict `validated` ou `redo`, lecture de l'avancement.
3. UI : nouvelle section repliable « Pochettes » dans l'UI d'écoute admin (`listen.html`, `listen.js`, `listen.css`, à côté de « Tests »). Elle affiche la pochette en grand, une à la fois, avec le titre du morceau et le compteur « N / total », et deux boutons « Valider » et « À refaire ». Après verdict, passer à la suivante ; une pochette régénérée revient à la fin de la file en `pending`.
4. Script `webradio/tools/cover_review_watch.py` : surveille `covers_review_state.json` ; pour chaque `redo` avec `redo_count` < 3 : attendre que la génération musicale soit inactive, démarrer ComfyUI-Qwen si nécessaire, régénérer avec `webradio/tools/cover_gen.py` en tirant une nouvelle graine (sans texte sur l'image), enregistrer la nouvelle pochette, remettre `pending`, incrémenter `redo_count` ; au troisième refus, passer `abandoned` et le noter. Ne régénérer ni ne conserver un morceau au solde négatif. Aucune intervention de Haiku dans le choix des images : le script est déterministe.
5. Tests automatiques du script (état simulé, pas de GPU) et de la logique des routes. Redémarrer le serveur si nécessaire (règle d'exécution).
6. Ajouter à `tests_manuels.md` le contrôle de la section « Pochettes » (navigateur et iPhone).
Fait quand : tests passés, page contrôlée au navigateur avec un état simulé, script lancé en simulation sans erreur.

## Phase 7 - Bouton Test (boucle de la playlist blues-rock) [TODO]
Dépend de : phases 4 (au moins une piste générée) et 5. Pas de GPU.
1. Moteur (`webradio/radio_engine.py`) : réglage persistant `test_loop` (identifiant de playlist ou vide). Quand il est défini, la programmation ne choisit que dans cette playlist, en boucle (ordre des pistes). Ne rien changer d'autre : jingles et publicités gardent leur fonctionnement actuel. Quand il est vide, retour à la programmation normale sans perturber le morceau en cours.
2. Serveur : route admin `POST /api/test_loop` (activer/désactiver) et état dans `/api/radio/state` ; le bouton ne doit pas être accessible à un auditeur non admin.
3. UI (`listen.html`, `listen.js`) : bouton « Test » réservé à l'admin ; premier appui = boucle de `blues-rock-guitare`, second appui = programmation normale ; libellé et état visuel indiquent le mode actif.
4. Tests automatiques : en mode boucle, seuls des morceaux de la playlist sont choisis ; après désactivation, retour à la sélection pondérée normale ; la playlist (poids 0) n'est jamais choisie hors du mode boucle. Redémarrer le serveur, vérifier au navigateur.
5. Ajouter à `AMELIORATIONS.md` : retirer le bouton Test avant le déploiement ; ajouter à `tests_manuels.md` le contrôle iPhone.
Fait quand : tests passés, bascule contrôlée au navigateur dans les deux sens.

## Phase 8 - Finalisation [TODO]
Dépend de : toutes les autres (celles bloquées sont notées au journal).
1. Retenter les suppressions sautées en phase 2 (morceau qui était en cours de diffusion).
2. Quand la génération musicale est terminée et inactive : générer les pochettes de la playlist `blues-rock-guitare` (`webradio/tools/cover_batch.py --playlist blues-rock-guitare`), puis alimenter `covers_review_state.json` avec les pochettes à relire, puis lancer `cover_review_watch.py` en arrière-plan (ComfyUI arrêté si le script n'en a pas besoin). Si la génération musicale n'est pas finie, ne pas lancer les pochettes et le noter.
3. Relancer `python -m pytest webradio/tests` et `python OUTILS/apprentissage/test_apprentissage.py` ; relancer les services arrêtés (`analyse`, `compression`) si nécessaire.
4. Mettre à jour `AMELIORATIONS.md` (entrées terminées retirées, nouvelles entrées ajoutées) et `tests_manuels.md` (chaque contrôle manuel en attente listé).
5. Dernier commit, puis écrire en tête du journal un bilan : ce qui est fait, ce qui est bloqué, ce que l'utilisateur doit faire au réveil (juger la page « Pochettes », écouter la playlist blues-rock avec le bouton Test, valider ou refuser les règles proposées en phase 1, décider des sauvegardes de votes).
Fait quand : bilan écrit et dernier commit fait.

## Journal d'exécution (Haiku, ajouter une ligne datée par événement)
- 2026-10-15 00:01 démarrage de la roadmap (modèle de session non contrôlé).
- 2026-10-15 00:04 phase 1 faite : proposition précédente sauvegardée (propositions/preferences.proposition_avant_2026-10-15.json), votes archivés (votes_archive/), liste figée de 296 morceaux négatifs du catalogue diffusé (473 négatifs au total dans votes.json, dont 177 déjà supprimés) dans negatifs_2026-10-15.json, préférences recalculées (857 votes pris en compte, 395 différences, preferences.json inexistant), règles proposées dans propositions/regles_negatifs_2026-10-15.md.
