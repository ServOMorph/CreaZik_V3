---
name: generation-morceaux
description: Prépare, lance et évalue une génération de morceau avec ACE-Step 1.5 (caption, paroles balisées, paramètres, config de test). À utiliser pour écrire un caption, adapter des paroles, créer des versions de test ou comprendre ce qu'ACE peut ou non faire.
---

# Génération de morceaux avec ACE-Step 1.5

Sources : doc locale `D:\ServOMorph\ACE-Step-1.5\docs\en\Tutorial.md` et `ace_step_musicians_guide.md`, plus deux guides web. Les points marqués (hypothèse) n'ont pas été testés dans ce projet.

## Pipeline du projet
- Worker : `webradio/ace_worker.py`, lancé par `webradio/generate.py <config.json> [--only ids] [--lm] [--steps N]`.
- Modèle : turbo (8 pas), sans LM par défaut (`thinking=False`). `guidance_scale` n'agit que sur les modèles base et SFT : sans effet en turbo.
- Config : `test_cases[]` avec `id`, `name`, `prompt` (caption), `type`, `duration`, `lyrics_file` ou `lyrics`, `language`, `seed`, `fit_lyrics`.
- Ne pas lancer en même temps que ComfyUI (GPU 8 Go). Ne jamais tuer ni relancer un worker sans accord de l'utilisateur.
- Pour les tests : dossier à part (`webradio/tests_ace/<sujet>/`), jamais les playlists ni la rotation. `fit_lyrics: false` pour garder les paroles complètes (sinon des sections sont retirées).

## Ce qu'on contrôle
- Caption : facteur principal. Mots-clés séparés par des virgules, 5 à 12, genre en premier, 2 à 3 instruments précis, type de voix, style de production, ambiance. Précis plutôt que vague (« grand piano » plutôt que « piano »).
- Pas de termes contradictoires, pas d'empilement de genres de niche. Pour un mélange, écrire une évolution dans le temps.
- Tempo, tonalité, signature : en paramètres (`bpm`, `keyscale`, `timesignature`), pas dans le caption. Ce sont des ancres : le résultat peut dévier. Plage fiable : 60 à 180 BPM, tonalités courantes, 4/4.
- Durée : courte (30 à 60 s) et moyenne (2 à 4 min) annoncées stables par la doc. Dans ce projet, aucun morceau de 150 s ou plus n'a été généré ; un test à 180 s a bloqué plus de 45 minutes en décodage VAE sur CPU. Rester à 135 s ou moins tant qu'un autre réglage n'est pas validé. Le blocage du décodage dépend de la VRAM libre, pas seulement de la durée : dans le test Marie, v8 (40 s) a mis 12 373 s car il restait 0,01 Go avant le décodage, ce qui a basculé le décodage sur processeur (ligne `auto-enabling CPU VAE decode` du journal), alors que v7 et v9 (40 s, environ 2,1 Go libres) ont pris 15 s. Lancer une version par worker (`--only <id>`) et surveiller cette ligne.
- Seed : fixer pour comparer des réglages, varier pour explorer. La graine n'est réellement appliquée que depuis le 2026-10-09 (`use_random_seed=False` dans `ace_worker.py`) ; avant, elle était ignorée. Une même graine redonne un audio presque identique (corrélation 0,99997 mesurée), pas bit à bit.

## Paroles
- Balises de section : `[intro]`, `[verse]`, `[pre-chorus]`, `[chorus]`, `[bridge]`, `[outro]`, `[instrumental]`. Une section de chant (verse, chorus, bridge) sans paroles est inutile. Pour un passage sans voix, la doc ACE (Tutorial, section Lyrics) emploie des balises sans paroles : `[Intro - piano]`, `[Outro - fade out]`, `[Instrumental]`, `[Breakdown]` (instrumentation réduite, espace), `[Guitar Solo]`, `[Piano Interlude]`, `[Build]`, `[Drop]`, `[Silence]`, `[Fade Out]`. Leur effet réel n'est pas testé dans ce projet (hypothèse) ; l'instrument d'un solo doit être cohérent avec le caption.
- Laisser du temps entre les paroles : pas de commande de pause dans la doc. Leviers (hypothèses à tester une variable à la fois) : insérer une section sans paroles entre deux sections chantées, allonger la durée à texte égal (ACE répartit les paroles sur la durée), baisser le `bpm`, mettre « laid-back » ou « slow tempo » dans le caption, garder des lignes courtes (6 à 10 syllabes).
- Descripteur après un tiret : `[Chorus - anthemic]`. Un seul ou deux mots, jamais d'empilement (le modèle peut chanter la balise).
- Balises de voix : `[spoken word]` (rap, récitation), `[whispered]`, `[raspy vocal]`, `[harmonies]`, `[ad-lib]`.
- Majuscules : plus d'intensité. Parenthèses : chœurs ou échos.
- Lignes de 6 à 10 syllabes (la doc web dit 4 à 8). Au-delà de 10 à 12, le rythme se brise. Garder une longueur voisine pour les lignes de même rang.
- Une langue non anglaise sans réglage peut être chantée avec une phonétique anglaise : fixer `language` (`fr`) ; marqueur de langue seulement en début de section.
- Cohérence : caption et paroles ne doivent pas se contredire (voix, instruments, énergie).
- Une métaphore par chanson ; éviter l'empilement d'adjectifs.

## Limites connues
- Musicalité et voix nettement en dessous des services commerciaux selon les avis consultés ; voix parfois grossière.
- Français : fait partie des langues les mieux gérées selon la documentation.
- Autotune (test Marie, seed 42, 120 s) : un caption sobre (« autotuned vocal ») donne un effet nul à léger ; « heavy hard-tuned autotune vocals, T-Pain and Future style, pitch-snapped robotic vocal effect » + rap trap donne un effet net.
- Voix : le timbre change au fil du morceau ; « single male vocalist » dans le caption ne l'a pas corrigé (v4).
- Voix de femme (démo T01, 135 s, un seul auditeur) : « playful female voice » a donné une voix d'homme (test 11), le duo homme/femme par section ne fonctionne pas (test 13, comme l'issue ACE-Step #398), « playful female vocal » avec balises de voix a donné une voix d'homme puis de femme (test 14) ; les graines n'étant alors pas appliquées, 15 et 19 sont deux tirages aléatoires du même réglage (15 jugée la meilleure, 15 et 19 instables). Grille avec graines appliquées (tests 26 à 31 et 39 à 44) à écouter avant de conclure.
- Un décodage VAE s'est figé 12 min à 120 s (v4) puis est passé en 47 s à la relance, mêmes paramètres. Cause probable (non démontrée) : VRAM libre insuffisante au moment du décodage.
- Intro avant l'entrée du beat (instrumental rap, mesure par énergie grave, 2026-10-10) : non réglable avec précision. Les balises de section n'ont pas d'effet net. Entrée mesurée : environ 30 s à 135 s et 130 BPM, 15 s à 45 s et 60 s, 24 à 32 s à 150 s selon le BPM ; à 150 s, 70 BPM a donné 14 à 15 s pour 2 graines sur 5 et 28 à 29 s pour 2 autres. Prévoir plusieurs graines et mesurer.
- Instrus rap mélodique minimaux (piano, violon, 150 s, 70 BPM, caption et balises du 2026-10-10, tests 51 à 55) : l'utilisateur a retenu les graines 2026 et 31415 (pouces haut, jugées parfaites) et rejeté 42, 101 et 777 (pouces bas). Les deux retenues ont un beat tardif (environ 29 s) ou très discret, les deux rejetées avec intro courte (14 à 15 s) ; l'intro de 10 à 15 s demandée n'était donc pas le critère décisif à l'écoute.
- Le résultat varie beaucoup d'une seed à l'autre : prévoir plusieurs versions.
- Hors du worker actuel : Cover, Repaint (3 à 90 s), score d'alignement des paroles, modèles SFT et XL.

## Procédure d'une série de versions
1. Fixer le point de départ avec l'utilisateur : paroles, durée, seed, LM oui ou non.
1b. Contrôler les paroles avant tout lancement : `python TEXTES/tools/check_lyrics.py <fichier> --caption "<caption>" --duree <s>`. Le script ne modifie rien. Les ERREUR (balise absente ou collée au texte, section vide, texte avant la première balise, encodage corrompu, caption instrumental avec paroles) sont à corriger avant de lancer. Les AVERT (balise inconnue, lignes de plus de 10 syllabes, durée de plus de 135 s, tempo dans le caption, texte probablement trop long pour la durée) sont à présenter à l'utilisateur. Le comptage de syllabes et l'estimation de durée sont approximatifs.
2. Créer ou compléter `config.json` dans `webradio/tests_ace/<sujet>/` : une entrée `test_cases` par version, un seul paramètre qui change à la fois.
3. Nommer chaque version de façon lisible (`vN_<style>_<voix>`). Dans la section Tests de l'UI, chaque test porte un numéro unique en début de nom (`NN · description`), jamais réutilisé : le suivant est le plus grand numéro existant plus un (le prochain libre au 2026-10-10 : 56). Avant d'ajouter un test à `webradio/playlists/tests-ace/outputs/playlist_results.json`, relire les noms existants pour trouver ce numéro.
4. Lancer `generate.py` en arrière-plan et suivre `outputs/playlist_results.json` (statut) et la sortie du process.
5. Donner à l'utilisateur le chemin des WAV et la durée de calcul ; noter ce qui a changé entre versions.
6. Toute génération (test ou nouveau morceau destiné à la radio) est publiée dans la section Tests (MP3 dans `webradio/playlists/tests-ace/outputs/`, entrée dans son `playlist_results.json` avec la clé `folder` et la référence éventuelle) et soumise à l'utilisateur pour écoute. Ne rien intégrer au catalogue, aux playlists ni à la rotation sans demande explicite, même après validation.
7. Toujours imposer une graine explicite (`seed` >= 0) : avec `-1` la graine tirée n'est pas relevée et le morceau n'est pas reproductible. Un sidecar `.metadata.json` et `generation_manifest.json` sont écrits par `ace_worker.py` dans le dossier de sortie du test.

## Règle : instrus de Marie (hypothèses issues des essais du 2026-10-10, petit échantillon)
- Rap mélodique minimal, 130 ou 70 BPM, 135 à 150 s, piano et violon, risers et habillage électro, `no vocals`, `type: instrumental`.
- Générer 5 graines sans autre changement, publier dans les Tests, garder celles qui plaisent (elles vont dans `TEXTES/artistes/Marie/tops_instrus/`). Un seul tirage ne suffit pas : 2 graines sur 5 retenues.
- Ne pas viser une intro précise : mesurer l'entrée du beat et accepter 15 à 30 s ; l'intro courte n'a pas été le critère décisif à l'écoute.
- Non testé à graine égale : 70 contre 130 BPM, effet du mot « binaire », piano contre cordes. Tester un seul paramètre à la fois.

## Suivi des textes (liste d'attente)
Quand la génération part d'un texte suivi dans `TEXTES/liste_attente.md` (identifiant `Txx`), tenir cette liste à jour pendant le travail.
- Ne jamais éditer le tableau à la main : utiliser le script.
  - `python TEXTES/tools/liste_attente.py set <ID> --statut <STATUT> --note "<remarque>"`
  - `python TEXTES/tools/liste_attente.py add --titre ... [--auteur --fichier --droits --statut --note]`
  - `python TEXTES/tools/liste_attente.py log "<message>"`
- Statuts : `A_PREPARER`, `PRET`, `EN_GENERATION`, `GENERE`, `VALIDE`, `REJETE`, `BLOQUE_DROITS`.
- Au lancement d'une série de versions : `EN_GENERATION`, avec en note le dossier de test et ce qui varie entre versions.
- Une fois les MP3 produits : `GENERE`, avec en note le chemin des MP3.
- `VALIDE` seulement après l'écoute et l'accord de l'utilisateur. `REJETE`, ou retour à `PRET`, seulement sur sa décision.
- Échec ou blocage : laisser `EN_GENERATION` et écrire la cause en note, sans rien inventer.
- Texte protégé (`TEXTES/usage_prive/`) : démo privée dans un dossier de test non versionné, jamais en playlist ni en rotation. Ne jamais mettre `VALIDE` ni autoriser un usage radio sans l'accord écrit de l'auteur.
- Ne pas lire d'état courant dans cette liste sans la relire : elle est mise à jour par plusieurs agents.

## Adaptation de paroles existantes
- Ne jamais modifier le fichier source : travailler sur une copie dans le dossier de test.
- Signaler les lignes de plus de 10 syllabes et les sections qui paraissent trop longues pour la durée visée ; proposer, ne pas réécrire sans accord.
