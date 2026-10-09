---
description: Génère des paroles françaises balisées pour ACE-Step avec gemma4:12b (Ollama local)
---

# /generate_lyrics [thème] [options]

Génère des paroles avec le LLM local `gemma4:12b` via Ollama. Script : `TEXTES/tools/generate_lyrics.py`. Sortie : `TEXTES/<nom>.md`, au format ACE-Step (balises `[verse]`, `[chorus]`, etc.).

## Procédure

1. Lire `TEXTES/agent_role.md` et les règles de paroles de `webradio/REGLES_GENERATION_DEV.md` (section 2.2 et section 1 : pas de recopie, nom d'artiste = consigne interne, jamais dans le texte).
2. Obtenir du demandeur : thème (obligatoire), style musical, ton/point de vue, durée visée (défaut 90 s), nom du fichier. Si le thème manque, le demander ; ne pas inventer le reste.
3. Vérifier que le GPU n'est pas occupé par ComfyUI ou la génération musicale (8 Go de VRAM partagés) : `nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader`. En cas de doute, prévenir l'utilisateur avant de lancer.
4. Lancer :
   ```powershell
   python TEXTES/tools/generate_lyrics.py --theme "<thème>" --style "<style>" --ton "<ton>" --duree <secondes> --nom "<nom>" --notes "<consignes>"
   ```
   Options : `--model` (défaut `gemma4:12b`), `--temperature` (0,9), `--timeout` (600 s). Le modèle est déchargé de la VRAM à la fin (`keep_alive: 0`).
5. Lancer `python TEXTES/tools/check_lyrics.py <fichier> --caption "<caption>" --duree <s>` (contrôle automatique : balises, sections vides, syllabes, cohérence avec le caption, durée). Puis relire les paroles produites et signaler : lignes de plus de 10 syllabes, clichés, rimes pauvres, répétitions, incohérence avec le style. Proposer des corrections, ne pas réécrire sans accord.
6. Afficher le chemin du fichier créé. Ne jamais écraser un fichier existant (le script suffixe `-2`, `-3`).
7. Proposer le caption ACE associé (section « Caption ACE » ci-dessous) : un caption, un `bpm` en paramètre, la durée, la langue. Le soumettre à l'utilisateur, ne pas lancer de génération sans son accord.
8. Ne rien commiter hors de `TEXTES/`.

## Caption ACE

Sources : `docs/en/Tutorial.md` d'ACE-Step (section Caption, lignes 337-393, et métadonnées, lignes 655-700) et l'analyse des votes de la radio (`webradio/votes.json` croisé avec les `config.json` des playlists, 652 morceaux votés sur 940, état du 2026-10-08).

### Règles de la doc ACE à appliquer
- Le caption est le facteur principal. Précis plutôt que vague. Combiner plusieurs dimensions : genre, ambiance, instruments, texture (warm, crisp, airy, punchy, raw), époque, production (live, vintage, polished), voix (genre, timbre), rythme (slow, mid-tempo, groovy, laid-back).
- Pas de termes contradictoires. Pour un mélange de styles : écrire une évolution dans le temps, ou répéter ce qu'on veut renforcer.
- Caption et paroles racontent la même histoire (voix, instruments, énergie) : le modèle ne sait pas résoudre un conflit.
- La doc recommande tempo, tonalité et signature en paramètres (`bpm`, `keyscale`, `timesignature`), pas dans le caption. Le worker de ce projet (sans LM) ne les infère pas : sans paramètre, les métadonnées valent N/A.

### Ce que disent les votes (corrélations, pas des causes)
- Les pouces ne portent que sur des morceaux déjà générés. Les morceaux d'une même playlist partagent presque tout leur caption : l'échantillon réellement indépendant est d'environ 70 playlists, pas 940 morceaux. Un seul auditeur. Un pouce mesure un goût, pas une qualité technique.
- Morceaux vocaux : 70 % de positifs (207 sur 297 avec avis tranché). Instrumentaux : 40 % (138 sur 348).
- Voix (parts de positifs) : `female` 95 % (39 sur 41), `falsetto` 100 % (10 sur 10), `playful` 82 %, `gritty` 82 %, `soulful` 80 %. À éviter : `operatic` 25 % (3 sur 12).
- Genres très bien reçus (au moins 8 positifs sur 10) : disco (toutes langues), groove et funk, poésie en français, rap français mélodique, hard rock, annees-50 (doo-wop, chanson, valse), a cappella féminin, maghreb.
- Genres mal reçus : percussions (Afrique 1 sur 10, Amérique du Sud 2 sur 10), Caraïbes 0 sur 10, gospel 0 sur 6, soul Motown instrumental 0 sur 6, gamelan, médiéval, classique, harpe seule, tango, Polynésie, nordique.
- Anglais 94 % de positifs (82 sur 87), français 52 % (89 sur 170). Cet écart est en grande partie un effet de playlist : l'anglais vient de playlists disco, groove et doo-wop qui sont les mieux reçues. Ne pas en conclure que l'anglais chante mieux.
- Français mal reçu : captions de type rock puissant (`powerful raspy male baritone`, `stadium rock`, `clear high male tenor`, `heartfelt`) : esprit-hallyday 3 sur 10, esprit-goldman 4 sur 10, francais_tests-rock 2 sur 15. Français bien reçu : chanson légère (`playful male voice, acoustic guitar, upright bass, light jazz swing` : 6 sur 10 ; chanson années 50 : 5 sur 5), blues, rap mélodique.
- Mots les plus associés aux positifs (au moins 6 occurrences) : `groovy`, `wah`, `slap`, `falsetto`, `confident`, `thumping`, `crunchy`, `four-four`, `luminous`, `disco`, `funk`.
- Sans effet visible : durée (60 à 135 s), nombre de termes du caption (5 à 10), longueur et syllabes des paroles françaises (positifs : 10,9 syllabes par ligne en moyenne, négatifs : 10,4 ; comptage approximatif par groupes de voyelles).
- BPM : 85 % de positifs pour les vocaux dont le caption contient « N bpm », contre 59 % sans ; instrumentaux 56 % contre 34 %. Effet probablement mêlé à la playlist. Le paramètre `bpm` du worker n'a jamais été utilisé dans les playlists : le choix « caption ou paramètre » n'est pas tranché par les données. À tester sur un cas, une seule variable à la fois.

### Modèle de caption
Ordre : genre (et époque), voix (genre plus un timbre), 2 à 3 instruments précis (un instrument rythmique inclus), une texture ou production, une ambiance. 5 à 8 termes, séparés par des virgules, en anglais. Exemple pour une chanson française légère, construit à partir des captions les mieux reçues : `French chanson, playful male voice, acoustic folk guitar, upright bass, light jazz swing, warm vintage recording, ironic and lighthearted`.

### Garde-fous avant génération
- Une version par worker (`generate.py --only <id>`) : le blocage constaté (v8 du test Marie, 12 373 s) venait d'une VRAM libre de 0,01 Go avant le décodage VAE, qui a basculé le décodage sur processeur, pas de la durée. Surveiller la ligne `auto-enabling CPU VAE decode` dans le journal et prévenir l'utilisateur, sans tuer le worker sans son accord.
- Rester à 135 s ou moins.
