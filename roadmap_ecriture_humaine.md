# Roadmap - WebRadio de l'écriture humaine

Objectif : mettre en musique des textes écrits par des humains (d'abord ceux de Funky Yogi), avec un système d'apprentissage qui transforme les votes de l'utilisateur en réglages de génération. Statuts mis à jour par `/close` uniquement.

Spécification du système d'apprentissage : `DOCUMENTATION/APPRENTISSAGE.md`.

## Décisions de cadrage (2026-10-11)
- Diffusion : retirer tous les morceaux chantés en français (MP3 supprimés, données conservées pour l'apprentissage), sauf les 14 versions de « Les souliers de ma grand-mère » (`:7`) et « Les gars de la côte » (`:17`, le « Ho hisse les gars » cité par l'utilisateur) dans `perso` et les six `francais_tests-*`, et sauf `poesie-fr` (conservée pour le moment). Les votes des 14 versions sont remis à zéro (anciens votes : `DOCUMENTATION/apprentissage/votes_avant_remise_a_zero_2026-10-11.json`) ; l'utilisateur les réécoute, un score négatif les sort de la diffusion, les plus approuvées seront gardées.
- Graine : chaque génération, rotation comprise, utilise une graine connue (tirée par `ace_worker.py` si la configuration n'en donne pas) et l'enregistre dans `playlist_results.json` (`seed`, `seed_source`) et le sidecar.
- Textes : l'adaptation d'un texte (silences, mise en lumière de mots ou de phrases, répétitions) est toujours proposée, jamais appliquée sans validation.
- Extraction des textes photographiés : 100 % locale, relecture humaine obligatoire, annotations manuscrites ignorées.
- Préférences : tirées des seuls votes radio (`webradio/votes.json`). Les avis Slow/Medium/High, les pouces et les commentaires des Tests sont exclus.
- Style : 3 styles proposés par texte, l'utilisateur choisit, puis génération.
- Modèle : ACE-Step 1.5 uniquement pour le moment ; les structures restent multi-modèles (clé `modele` partout). Voix de femme non exclue.
- Durée : 150 s maximum (modifiable). Aucune contrainte de temps de calcul. Échec = échec technique seulement (erreur, délai, fichier absent, durée incohérente) ; en cas d'échec : changer de graine.
- Textes du run : ceux extraits des photos plus `TEXTES/artistes/funky-yogi/paroles.md`.
- Apprentissage : fichier JSON relu par script ; mise à jour seulement après accord ; le diff est montré en fin de session par `/close`.
- Auteurs externes (accord écrit, crédit, retrait) : reporté.
- Modèle d'exécution : Sonnet pour toutes les phases. Les consignes ci-dessous s'appliquent à chaque phase.

## Règles d'exécution
1. Lire cette roadmap, puis `DOCUMENTATION/APPRENTISSAGE.md`, avant toute action.
2. Ne jamais calculer, classer ou déduire à la main ce qu'un script du projet calcule : lancer le script et recopier sa sortie.
3. Ne jamais modifier : un texte source (`TEXTES/artistes/*/textes/*.md` validé), `webradio/playlists/*` hors `tests-ace`, `webradio/series.txt`, `webradio/playlists.json`, `DOCUMENTATION/apprentissage/preferences.json`.
4. Un texte à la fois. L'état du run est dans `DOCUMENTATION/apprentissage/run_state.json` ; le relire avant chaque texte pour reprendre au bon endroit.
5. Arrêt et question à l'utilisateur si : un script sort en erreur deux fois de suite, `check_lyrics.py` signale une ERREUR, la VRAM libre est inférieure à 2 Go avant un lancement, un fichier attendu est absent, ou une consigne paraît contradictoire.
6. Ne jamais tuer un worker ACE en cours sans accord de l'utilisateur.
7. Vocabulaire : écrire « généré » et non « validé ». Seul l'utilisateur valide.
8. En fin de phase : lister les fichiers produits, les échecs avec leur cause exacte (recopiée du journal), et ce qui attend l'utilisateur.

## Phase 1 - Outil d'extraction des textes photographiés [FAIT]
- Créer `OUTILS/extraction_paroles/` : script `extraire_paroles.py <image|dossier> --sortie <dossier>` avec un modèle vision local via Ollama (candidats installés : `qwen2.5vl`, `gemma4:12b` ; choix sur essai), et un `README.md` d'usage.
- Consigne d'extraction : texte imprimé seulement, annotations manuscrites ignorées (accords, flèches, mots ajoutés), un fichier `.md` par texte, même si une photo en contient plusieurs. « Ref : » devient `[chorus]`. Aucune correction d'orthographe ni reformulation.
- En-tête de chaque `.md` : titre, photo source, modèle utilisé, date, statut `A_RELIRE`.
- Premier lot : `TEXTES/artistes/funky-yogi/photos_textes/` (6 photos) vers `TEXTES/artistes/funky-yogi/textes/`.
- Relecture : l'utilisateur corrige ou valide chaque fichier ; le statut passe à `RELU` sur sa seule demande.
- Tests : contrôle sur une photo de référence relue à la main (taux de lignes identiques, aucune annotation manuscrite dans la sortie).
- Fait quand : tous les textes du lot sont en statut `RELU`.

## Phase 2 - Système d'apprentissage [FAIT]
- Scripts dans `OUTILS/apprentissage/`, données dans `DOCUMENTATION/apprentissage/`, schéma dans `DOCUMENTATION/APPRENTISSAGE.md`.
- `calculer_preferences.py` : lit `webradio/votes.json`, les `config.json` des playlists, `webradio/learning/morceaux_rejetes.jsonl` et les caractéristiques audio (`.feat.json`), puis écrit `preferences.proposition.json` (préférences de style, de caption, de tempo, de durée, de voix, avec effectifs et taux d'approbation).
- `regles_modeles.json` : capacités et limites par modèle (ACE-Step 1.5 renseigné à partir du skill `generation-morceaux` et de `DOCUMENTATION/ACE_STEP_1_5.md`), contraintes de formatage des paroles, catalogue des opérations d'adaptation de texte (silence, mise en lumière, écho, répétition, coupe), chacune marquée `teste` ou `hypothese`.
- `diff_preferences.py` : affiche les différences entre `preferences.json` (validé) et la proposition ; `--appliquer` copie la proposition et archive l'ancienne version dans `historique/`.
- `/close` : ajouter dans la section Spécificités projet de `.claude/commands/close.md` une étape qui lance `diff_preferences.py` et demande l'accord avant `--appliquer`.
- Tests : calcul sur un jeu de votes fictif à résultat connu, diff vide quand rien ne change, `--appliquer` refusé sans proposition.
- Fait quand : `preferences.json` est validé une première fois par l'utilisateur via le diff.

## Phase 3 - Retrait des morceaux en français de la diffusion [FAIT]
- Liste établie le 2026-10-11 : `DOCUMENTATION/apprentissage/retrait_fr.json` (222 morceaux à retirer, 14 conservés, `poesie-fr` hors liste).
- Accord explicite de l'utilisateur sur cette liste avant toute suppression.
- Retrait par le mécanisme du serveur (données copiées dans `webradio/learning/morceaux_rejetes.jsonl`, entrée masquée dans `catalog_overrides.json`) ; retrait des playlists vidées de `webradio/series.txt` pour éviter leur régénération.
- Tests : aucun morceau retiré n'apparaît dans le tirage du moteur ; chaque retiré a son enregistrement dans le corpus ; les morceaux conservés restent diffusables.
- Fait quand : la liste validée est appliquée et vérifiée.

## Phase 4 - Propositions par texte [FAIT]
- Pour chaque texte `RELU` : 3 styles proposés (caption, tempo, durée de 150 s au plus, type de voix), fondés sur `preferences.json` et `regles_modeles.json`, plus les adaptations de texte proposées (opérations du catalogue, avec la ligne avant et après).
- Contrôle de chaque version proposée par `TEXTES/tools/check_lyrics.py`.
- Sortie : `DOCUMENTATION/apprentissage/propositions/<texte>.md` lisible, et `plan_run.json` rempli au fur et à mesure des choix de l'utilisateur.
- Fait quand : chaque texte a un style choisi et des adaptations acceptées ou refusées.

## Phase 5 - Run automatique [FAIT]
- Script `OUTILS/run_textes/run_textes.py` : lit `plan_run.json`, crée la configuration dans `webradio/tests_ace/funky_yogi_textes/`, lance `generate.py --only <id>` une version à la fois, vérifie le statut et la durée du MP3, publie dans la section Tests (MP3 dans `webradio/playlists/tests-ace/outputs/`, numéro unique, `folder` « Funky Yogi », `reference` vers le texte), met à jour `run_state.json`.
- Échec (erreur, délai dépassé, fichier absent ou durée incohérente) : nouvelle graine, prise dans la liste fixe de `regles_modeles.json`, 3 tentatives au plus, puis statut `ECHEC` avec la cause.
- Le script refuse d'écrire hors de `tests_ace/` et `playlists/tests-ace/`.
- Tests : exécution à blanc (`--simulation`) sur deux textes sans GPU, puis un texte réel.
- Fait quand : chaque texte du plan a un morceau dans les Tests ou un `ECHEC` documenté.

## Phase 6 - Bilan d'écoute et boucle d'apprentissage [EN COURS]
- Après écoute dans les Tests, rapport par texte (style, graine, durée, pouces).
- Proposition de mise à jour de `preferences.json` ; diff présenté par `/close`, appliqué seulement après accord.
- Fait quand : une première boucle complète (génération, écoute, mise à jour validée) est faite.
