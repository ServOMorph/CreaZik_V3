# Propositions : 10 textes de Funky Yogi extraits des photos

Textes : `TEXTES/artistes/funky-yogi/textes/*.md`, tous `RELU` (relecture et passage à `RELU` demandés par l'utilisateur le 2026-10-11 ; « Cancer poumon et d'autres » supprimé par l'utilisateur).
Statut de ces propositions : A_VALIDER. Rien n'est appliqué, rien n'est lancé. La source de chaque texte n'est jamais modifiée : les adaptations acceptées sont écrites dans une copie balisée.
Base des styles : `preferences.proposition.json` du 2026-10-11 (provisoire tant que `preferences.json` n'est pas validé) : funk-soul 0,68 ; electro 0,54 ; voix d'homme 0,65 ; voix de femme 0,91 mais instable avec ACE ; folk 0,36 ; chœur 0,38. Consigne de l'utilisateur (2026-10-11) : pour Funky Yogi, privilégier les styles electro, funk, groove, soul et disco ; ni hip-hop, ni trap, ni ballade piano. Aucun nom d'artiste dans les captions.

## Sélection retenue (choix délégué par l'utilisateur le 2026-10-11)
Consigne : un ensemble dansant, tempo autour de 120 (110 à 130), varié mais dans un même style « Funky Yogi » : electro-funk, funk, disco, soul, groove. Une version par texte, voix d'homme sauf une voix de femme (texte 6, pour la variété ; instable avec ACE, à écouter). Les tempos ci-dessous remplacent ceux des tableaux.
| Texte | Style retenu | BPM | Voix | Durée |
|---|---|---|---|---|
| 1 Dans la figure | C Disco doux | 110 | homme | 105 s |
| 2 Faut que ça groove | A Funk groove | 118 | homme | 135 s |
| 3 Idées folles | C Disco | 120 | homme | 60 s |
| 4 Kes kis pas | C Electro-funk tendu | 122 | homme | 120 s |
| 5 Loin des papas | C Disco-soul (84 BPM proposé, porté à 95 sur ta demande) | 95 | homme | 75 s |
| 6 Mes bordels | B Electro-disco | 116 | femme | 90 s |
| 7 Mineur majeur | A Electro-funk joueur | 120 | homme | 80 s |
| 8 Miracle | C Disco-funk | 118 | homme | 120 s |
| 9 Pause | C House soul | 122 | homme | 80 s |
| 10 Truc | C Disco-soul | 100 | homme | 100 s |
Variation de tempo demandée par l'utilisateur : un morceau à 100 BPM (texte 10) et un à 95 BPM (texte 5, « Loin des papas », lent et triste) ; choix des deux morceaux par moi. Le texte « paroles.md » (styles A, B, C de `paroles-funky-yogi.md`) n'est pas dans cette sélection.
Adaptations : « tout le reste est ok » (2026-10-11) est lu comme acceptation de toutes celles listées dans chaque section, hypothèses comprises ; à corriger si ce n'est pas le sens. Rien ne part avant la validation du test des choeurs ci-dessous.

## Test des choeurs (backs de voix) : proposition
But : savoir si ACE-Step 1.5 produit des choeurs ou voix de soutien exploitables, et par quel moyen. Aucun de ces moyens n'est testé dans le projet (hypothèses de la doc ACE et du skill). Méthode : même texte, même style, même BPM, même graine, un seul paramètre qui change. Les 3 textes retenus ont un refrain net : 2 (Faut que ça groove), 4 (Kes kis pas), 8 (Miracle). Graine fixe 2026 pour la base et les 3 variantes de chaque texte ; les 7 autres textes ont une graine tirée et enregistrée.

| Version | Moyen | Changement par rapport à la base |
|---|---|---|
| Base | aucun | Version sélectionnée ci-dessus, sans choeurs |
| V1 Echo | parenthèses (hypothese) | Reprise en écho entre parenthèses de la fin de chaque ligne du refrain |
| V2 Harmonies | balise + caption (hypothese) | Balise `[chorus - harmonies]` sur le refrain, et `layered backing vocals, group harmonies` ajouté au caption |
| V3 Ad-lib | balise + parenthèses (hypothese) | Balise `[ad-lib]` après le refrain, avec réponses courtes entre parenthèses |

Lignes proposées pour le refrain :
- Texte 2 : V1 `Y faut que ça groove (que ça groove), Y faut que ça bouge (que ça bouge)` ; V3 `(hey)` / `(yeah)` après chaque ligne.
- Texte 4 : V1 `Mais qu'est ce qui se passe ? (qui se passe)` ; V3 `(hey)` / `(oh)` après chaque ligne.
- Texte 8 : V1 `Miracle (miracle)` en fin de refrain et `Et tous les jours je m'assois à mon tour (à mon tour)` ; V3 `(oh)` / `(hey)` après chaque ligne.

Total : 3 textes x 4 versions = 12 générations dont 3 bases (qui remplacent les versions normales de ces 3 textes), donc 9 générations en plus des 10 versions de base. Publication dans les Tests, dossier « Funky Yogi », nom `NN · titre, style, graine, base|V1|V2|V3`. Évaluation : tu écoutes les 4 versions de chaque texte ; je note pour chaque moyen si le choeur est audible, juste, et ne chante pas la balise ; le résultat alimente `regles_modeles.json` (état `teste` ou `echec`) après ton accord.

## Règles communes
- Balisage : `[verse]`, `[chorus]`, `[outro]` posés sur les groupes de lignes séparés par une ligne vide ; aucune ligne de contenu ajoutée ou retirée sans ton accord.
- Textes courts (4 à 20 lignes) : durée limitée pour ne pas étirer le texte ; une répétition de section est proposée quand elle est utile.
- Découpes de lignes trop longues : calculées par `check_lyrics.py` sur la copie balisée avant le lancement ; ERREUR = arrêt et question.
- Voix de femme : instable, à écouter ; graine tirée et enregistrée (ou donnée par toi).
- États : `teste` = `[Silence]` (démo T01, version 18) ; `hypothese` = majuscules, parenthèses, `[Breakdown]`, `[whispered]`.

## 1. Dans la figure (13 lignes, 105 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Electro-soul sobre | `French electro-soul, warm synth pads, soft drum machine, smooth bass, male vocal, introspective, hopeful` | 100 | homme |
| B | Funk-soul doux | `French funk-soul, smooth bass, warm Rhodes, brushed drums, female vocal, tender, laid-back` | 92 | femme |
| C | Disco doux | `French soft disco, warm strings, mellow bass groove, gentle four-on-the-floor, male vocal, bittersweet, shimmering` | 108 | homme |

Adaptations : (1) `[Silence]` avant la dernière ligne `Dans la figure` (teste) ; (2) `DANS LA FIGURE` en majuscules (hypothese) ; (3) découpe de `On m'avait jamais appris que la terre était aussi dure` en `On m'avait jamais appris` / `que la terre était aussi dure`.

## 2. Faut que ça groove (18 lignes, 135 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Funk groove | `French funk, slap bass, tight drums, clean guitar chops, warm synths, male vocal, groovy, energetic` | 112 | homme |
| B | Electro-funk | `French electro-funk, slap bass, analog synths, punchy drums, female vocal, groovy, playful` | 118 | femme |
| C | Nu-disco funk | `French nu-disco funk, filtered synths, groovy bass, four-on-the-floor, funky guitar, male vocal, danceable` | 116 | homme |

Adaptations : (1) `Y faut que ca groove, Y faut que ca bouge` en `[chorus]` à chaque occurrence ; (2) `x3` écrit en trois lignes `De coeur en fille, de coeur en fer` (la mention `x3` ne peut pas être chantée) ; (3) `ca` en `ça` et `coeur` en `cœur` pour la prononciation ; (4) `[Silence]` avant le dernier refrain (teste) ; (5) `BOUGE` en majuscules au dernier refrain (hypothese).

## 3. Idées folles (4 lignes, 60 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Electro-groove nocturne | `French electro-groove, dreamy synths, pulsing bass, light drum machine, male vocal, nocturnal, playful` | 108 | homme |
| B | Funk-soul | `French funk-soul, smooth bass, warm Rhodes, tight drums, female vocal, intimate, playful` | 100 | femme |
| C | Disco | `French disco, glittering synths, funky bass, four-on-the-floor, string stabs, male vocal, playful, dreamy` | 112 | homme |

Adaptations : (1) répétition du texte entier (2 passages) pour atteindre 60 s ; (2) `[Silence]` avant `Si ce soir je te faisais un album.` (teste) ; (3) `ALBUM` en majuscules (hypothese).

## 4. Kes kis pas (21 lignes, 120 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Electro sombre | `French dark electro, pulsing synth bass, tense arpeggios, driving drum machine, male vocal, anxious, building energy` | 118 | homme |
| B | Funk-soul tendu | `French funk-soul, tense bass groove, muted guitar, crisp drums, female vocal, urgent, restless` | 100 | femme |
| C | Electro-funk tendu | `French electro-funk, tense slap bass, synth stabs, driving drum machine, male vocal, urgent, restless` | 108 | homme |

Adaptations : (1) `Mais qu'est ce qui se passe ?` en `[chorus]` à chaque occurrence ; (2) `(en moi)` entre parenthèses (hypothese) ; (3) `[Silence]` avant le dernier `Mais qu'est ce qui se passe ?` / `En moi` (teste) ; (4) `[Breakdown]` avant `Alors j'allume l'ordinateur,` (hypothese).

## 5. Loin des papas (6 lignes, 75 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Soul lente | `French slow soul, warm Rhodes, soft bass, brushed drums, female vocal, tender, melancholic` | 70 | femme |
| B | Electro downtempo | `French downtempo electronic, ambient pads, soft pulsing bass, light beat, male vocal, melancholic, spacious` | 80 | homme |
| C | Disco-soul lent | `French slow disco soul, warm strings, soft bass groove, gentle beat, male vocal, melancholic, tender` | 84 | homme |

Adaptations : (1) répétition du premier couplet en fin de morceau ; (2) `[whispered]` sur `Je pleure, doucement` (hypothese) ; (3) `[Silence]` avant `Où sont passés les aînés ?` (teste).

## 6. Mes bordels (8 lignes, 90 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Funk-soul | `French funk-soul, slap bass, warm Rhodes, tight drums, male vocal, passionate, groovy` | 105 | homme |
| B | Electro-disco | `French electro-disco, bright synths, punchy drums, driving bass, female vocal, urgent, emotional` | 116 | femme |
| C | Groove-soul | `French groove soul, warm Rhodes, deep bass groove, crisp drums, male vocal, emotional, smooth` | 92 | homme |

Adaptations : (1) `Fais tes choix bordel, fais tes choix` en `[chorus]` (lignes 1 et 3) ; (2) répétition de ce refrain en fin de morceau ; (3) `BORDEL` en majuscules (hypothese).

## 7. Mineur majeur (8 lignes, 80 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Electro-funk joueur | `French electro-funk, slap bass, playful synths, tight drum machine, male vocal, quirky, upbeat` | 120 | homme |
| B | Funk joueur | `French funk, bouncy slap bass, drum machine, synth stabs, male vocal, humorous, rhythmic` | 100 | homme |
| C | Electro-disco | `French electro-disco, bright arpeggios, punchy drums, bouncy bass, female vocal, playful, catchy` | 124 | femme |

Adaptations : (1) `tique, tique, tique...` répété 4 fois en fin de morceau (hypothese) ; (2) `[Instrumental]` avant `Alors on fout de l'électronique` (hypothese) . Correction faite à ta demande : `Caméléon,calmer léon` dans le texte source.

## 8. Miracle (17 lignes, 120 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Funk-soul | `French funk-soul, warm bass, clean guitar, tight drums, male vocal, urgent, soulful chorus` | 100 | homme |
| B | Electro downtempo | `French downtempo electronic, deep synth bass, atmospheric pads, steady beat, female vocal, hypnotic, haunting` | 90 | femme |
| C | Disco-funk | `French disco-funk, driving bass, clean guitar chops, string stabs, four-on-the-floor, male vocal, intense, soulful` | 110 | homme |

Adaptations : (1) groupe `Et tous les jours je m'assois à mon tour...` en `[chorus]` (déjà repéré par `Ref :`) ; (2) répétition du `[chorus]` en fin de morceau, car le second couplet n'en est pas suivi ; (3) `[Silence]` avant `Miracle` (teste) ; (4) `MIRACLE` en majuscules (hypothese).

## 9. Pause (8 lignes, 80 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Electro-groove | `French electro-groove, soft synths, light drum machine, warm bass, male vocal, calm, hopeful` | 105 | homme |
| B | Funk-soul | `French funk-soul, smooth bass, warm Rhodes, brushed drums, female vocal, relaxed, groovy` | 95 | femme |
| C | House soul | `French deep house soul, dusty keys, soft four-on-the-floor, warm bass, male vocal, relaxed, late night` | 100 | homme |

Adaptations : (1) `[Silence]` après `Appuyer sur la barre espace` (illustre le texte ; teste) ; (2) `PAUSE` en majuscules sur `Je veux faire une pause` (hypothese) ; (3) répétition des 3 premières lignes en fin de morceau.

## 10. Truc (11 lignes, 100 s)
| | Style | Caption | BPM | Voix |
|---|---|---|---|---|
| A | Funk-soul | `French funk-soul, smooth bass, clean guitar, tight drums, male vocal, regretful, groovy` | 98 | homme |
| B | Electro-funk | `French electro-funk, bright synths, punchy drums, driving bass, female vocal, wistful, catchy` | 110 | femme |
| C | Disco-soul | `French disco soul, warm strings, groovy bass, steady four-on-the-floor, male vocal, reflective, bittersweet` | 104 | homme |

Adaptations : (1) découpe de `C'est assez dur à dire mais je dois l'assumer` en `C'est assez dur à dire` / `mais je dois l'assumer` ; (2) `[Silence]` avant `Maintenant je suis très mal` (teste) ; (3) `Fais pas ça, fais pas si` répété en écho entre parenthèses (hypothese).

## Choix attendus
Pour chaque texte : un ou plusieurs styles (A, B, C) et les adaptations acceptées ou refusées (par numéro). Un texte sans choix reste hors run. Une réponse globale est possible, par exemple « style A partout, toutes les adaptations teste, aucune hypothese ». Ensuite : `plan_run.json` rempli, copies balisées créées, `check_lyrics.py` sur chacune, puis `run_textes.py`.
