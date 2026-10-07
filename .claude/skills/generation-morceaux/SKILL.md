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
- Durée : courte (30 à 60 s) et moyenne (2 à 4 min) annoncées stables par la doc. Dans ce projet, aucun morceau de 150 s ou plus n'a été généré ; un test à 180 s a bloqué plus de 45 minutes en décodage VAE sur CPU. Rester à 135 s ou moins tant qu'un autre réglage n'est pas validé.
- Seed : fixer pour comparer des réglages, varier pour explorer.

## Paroles
- Balises de section : `[intro]`, `[verse]`, `[pre-chorus]`, `[chorus]`, `[bridge]`, `[outro]`, `[instrumental]`. Une section vide produit du silence.
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
- Un décodage VAE s'est figé 12 min à 120 s (v4) puis est passé en 47 s à la relance, mêmes paramètres.
- Le résultat varie beaucoup d'une seed à l'autre : prévoir plusieurs versions.
- Hors du worker actuel : Cover, Repaint (3 à 90 s), score d'alignement des paroles, modèles SFT et XL.

## Procédure d'une série de versions
1. Fixer le point de départ avec l'utilisateur : paroles, durée, seed, LM oui ou non.
2. Créer ou compléter `config.json` dans `webradio/tests_ace/<sujet>/` : une entrée `test_cases` par version, un seul paramètre qui change à la fois.
3. Nommer chaque version de façon lisible (`vN_<style>_<voix>`).
4. Lancer `generate.py` en arrière-plan et suivre `outputs/playlist_results.json` (statut) et la sortie du process.
5. Donner à l'utilisateur le chemin des WAV et la durée de calcul ; noter ce qui a changé entre versions.
6. Ne rien intégrer au catalogue ni aux playlists sans demande explicite.

## Adaptation de paroles existantes
- Ne jamais modifier le fichier source : travailler sur une copie dans le dossier de test.
- Signaler les lignes de plus de 10 syllabes et les sections qui paraissent trop longues pour la durée visée ; proposer, ne pas réécrire sans accord.
