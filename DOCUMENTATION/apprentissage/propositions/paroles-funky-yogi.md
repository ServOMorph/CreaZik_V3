# Proposition : texte « paroles.md » de Funky Yogi

Source : `TEXTES/artistes/funky-yogi/paroles.md` (texte fourni par l'auteur, 47 lignes ; copie balisée existante : `webradio/tests_ace/funky_yogi/paroles_ace.md`, 32 lignes de chant, 3 couplets, 3 refrains).
Statut de la proposition : A_VALIDER. Rien n'est appliqué, rien n'est lancé.
Base des styles : `preferences.proposition.json` du 2026-10-11 (provisoire : `preferences.json` n'est pas encore validé) et `regles_modeles.json`.

## Ce que disent les votes radio (indicatif, un vote par morceau)
| Critère | Pour / contre | Taux |
|---|---|---|
| Famille funk-soul | 65 / 30 | 0,68 |
| Famille hip-hop | 14 / 8 | 0,64 |
| Famille electro | 94 / 79 | 0,54 |
| Voix d'homme | 103 / 55 | 0,65 |
| Voix de femme | 40 / 4 | 0,91 |
| `slap bass` | 17 / 2 | 0,89 |
| `120 bpm` | 14 / 6 | 0,70 |
| Famille folk | 58 / 103 | 0,36 |
Limites : les votes portent sur des morceaux souvent instrumentaux et sur des captions différents ; la voix de femme reste instable avec ACE (voir `regles_modeles.json`) ; aucune graine n'était enregistrée avant le 2026-10-11.

## Trois styles proposés (durée 135 s chacun, maximum autorisé 150 s)
| | Style | Caption (sans nom d'artiste) | BPM | Voix |
|---|---|---|---|---|
| A | Funk groove | `French funk, slap bass, warm analog synths, tight drums, clean electric guitar chops, male vocal, groovy, uplifting` | 110 | homme |
| B | Funk à voix de femme | `French funk-soul, slap bass, warm Rhodes, crisp drums, female vocal, smooth, playful, groovy` | 105 | femme (instable : à écouter) |
| C | Rap parlé funk | `French funk rap, spoken word verses, slap bass, drum machine, synth stabs, male vocal, laid-back, rhythmic` | 95 | homme, couplets parlés |

## Adaptations de texte proposées (copie du texte ; la source reste intacte)
| # | Opération | Avant | Après | État de l'opération |
|---|---|---|---|---|
| 1 | Découpe, ligne trop longue (13 syllabes) | `Le web en ligne directe, j’fais mes courses dans l’infini` | deux lignes : `Le web en ligne directe,` / `j’fais mes courses dans l’infini` | règle du skill |
| 2 | idem | `ClaudeCode dans le studio, il code pendant qu’je groove` | `ClaudeCode dans le studio,` / `il code pendant qu’je groove` | règle du skill |
| 3 | idem | `Moi j’fais le Funky Yogi, lui, il m’pose tous les moves.` | `Moi j’fais le Funky Yogi,` / `lui, il m’pose tous les moves.` | règle du skill |
| 4 | idem (16 syllabes) | `Je danse avec les pixels comme en plein Funky Confinement` | `Je danse avec les pixels` / `comme en plein Funky Confinement` | règle du skill |
| 5 | idem | `Mais mon corps veut la scène, pas un écran tout le temps.` | `Mais mon corps veut la scène,` / `pas un écran tout le temps.` | règle du skill |
| 6 | idem | `Mais la star sur la track, maintenant, c’est plus mon cœur.` | `Mais la star sur la track,` / `maintenant, c’est plus mon cœur.` | règle du skill |
| 7 | Silence avant la phrase finale | `Funky Yogi, garde le funk, choisis` | ligne `[Silence]` insérée avant | testé (démo T01, version 18) |
| 8 | Mise en lumière | `Laisse ton cœur groover sans IA dans la vie.` | `Laisse ton cœur groover SANS IA dans la vie.` | hypothèse |
| 9 | Écho | `Funky Yogi, débranche un peu l’ordi` | `Funky Yogi, débranche un peu l’ordi (débranche)` | hypothèse |
Les lignes de 11 à 12 syllabes restent telles quelles (avertissements simples de `check_lyrics.py`). Je ne propose pas de réécriture de contenu.

## Choix attendus
1. Quels styles lancer (A, B, C, plusieurs) ?
2. Quelles adaptations accepter ou refuser (numéros 1 à 9) ?
3. Une version par style ; la graine est tirée et enregistrée, ou fixée si tu la donnes.
Une fois les choix faits, ils sont inscrits dans `plan_run.json` et `run_textes.py` lance le run.

## Autres textes extraits des photos
11 textes en `A_RELIRE` dans `TEXTES/artistes/funky-yogi/textes/`. Leur proposition se fera texte par texte après relecture (statut `RELU` sur ta demande).
