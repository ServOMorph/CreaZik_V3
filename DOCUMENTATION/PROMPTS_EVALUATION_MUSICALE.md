# Prompts de la campagne comparative

Cette grille prépare dix générations sur chacun d’ACE-Step 1.5, HeartMuLa 3B, MusicGen Small et Stable Audio 3 Small-Music. Cela représente 40 sorties. Le but est de montrer des capacités variées, pas de produire dix chansons finies. Chaque essai dure 30 s. Les entrées sont adaptées à ce que chaque modèle sait lire; les sorties ne sont donc pas strictement équivalentes.

## Les dix briefs

| ID | Axe observé | Brief commun |
|---|---|---|
| 01 | Electro-pop et progression | Electro-pop mélodique, 116 BPM, synthé analogique, basse ronde, arpèges lumineux, couplet contenu puis refrain ample, nostalgique mais optimiste. |
| 02 | Ambient et texture | Ambient cinématique lent, piano feutré, nappes aériennes et cordes discrètes, montée douce, espace et mélancolie. |
| 03 | House et groove | House mélodique, 124 BPM, grosse caisse régulière, basse syncopée, accords de piano chaleureux, montée et relâchement dansant. |
| 04 | Jazz et instruments | Trio jazz intimiste, 92 BPM, piano acoustique, contrebasse ronde, batterie aux balais, échange mélodique naturel. |
| 05 | Folk acoustique | Folk acoustique, 98 BPM, guitare en arpèges, basse naturelle, percussion légère, sentiment de route et de liberté. |
| 06 | Beat hip-hop | Hip-hop instrumental, 88 BPM, kick profond, caisse claire sèche, basse souple, piano sombre et motif court, sans voix. |
| 07 | Orchestre et dynamique | Musique orchestrale de film, cordes en crescendo, cuivres retenus, percussion cinématique, tension puis résolution lumineuse. |
| 08 | Funk et timbres | Funk moderne, 108 BPM, basse slap, guitare rythmique étouffée, clavinet et section de cuivres, énergique et précis. |
| 09 | Voix française et émotion | Chanson française pop acoustique, voix masculine intime, piano et guitare légère, texte original sur le retour chez soi, refrain mémorisable, émotion retenue. |
| 10 | Voix française et rythme | Rap mélodique français, voix masculine, autotune modéré, 92 BPM, beat doux, piano nocturne et basse profonde, texte original sur la persévérance, refrain chanté. |

## Adaptation par modèle

### ACE-Step 1.5

Utiliser le brief en caption, ajouter une durée et un BPM cohérents et fournir des paroles structurées en français pour les IDs 09–10. Pour les IDs 01–08, sélectionner le paramètre instrumental; le caption décrit alors uniquement le son instrumental. Pour les morceaux chantés, préciser la langue `fr`, le timbre vocal et la structure. La seed doit être enregistrée; utiliser le LM pour les générations exploratoires, le désactiver quand les métadonnées et paroles sont déjà figées.

Exemple ID 10 :

```text
Caption: Rap mélodique français, 92 BPM, voix masculine avec autotune modéré, beat hip-hop doux, piano nocturne, basse profonde, couplets retenus et refrain chanté mémorisable, ambiance intime et déterminée, production studio moderne.
Language: fr

[Verse 1]
J’ai pris le temps de tomber
Pour mieux apprendre à rester
Les mains ouvertes sous la pluie
Je fais un pas, je dis oui

[Chorus]
Je tiens debout, je garde le cap
Même si la nuit me rattrape
Je vois demain dans le brouillard
Je marche encore, il n’est pas tard
```

Saisir le caption et les paroles dans leurs champs respectifs; ne pas envoyer les libellés `Caption:` et `Language:` comme paroles.

### HeartMuLa

Pour chaque ID : écrire les tags en liste séparée par des virgules, puis fournir des paroles originales en français balisées. Pour les IDs 01–08, ajouter `instrumental` aux tags et fournir les sections instrumentales indiquées dans le guide du dépôt. Pour 09–10, écrire des paroles françaises originales et utiliser `[Verse]`, `[Chorus]`, `[Bridge]`/`[Outro]` quand la durée le permet. Éviter de réutiliser un texte de chanson existant.

Exemple ID 10 :

```text
Tags: french,melodic rap,male vocal,moderate autotune,soft hip hop beat,92 bpm,night piano,deep bass,hopeful,modern production

[Intro]

[Verse]
J’ai pris le temps de tomber
Pour mieux apprendre à rester
Les mains ouvertes sous la pluie
Je fais un pas, je dis oui

[Chorus]
Je tiens debout, je garde le cap
Même si la nuit me rattrape
Je vois demain dans le brouillard
Je marche encore, il n’est pas tard

[Outro]
```

Utiliser le format de tags sans espaces après les virgules documenté par HeartMuLa. Si `instrumental` ne suffit pas à supprimer les voix, noter l’écart; ne pas inventer une option d’API qui n’est pas documentée.

### MusicGen Small

Une seule description en anglais concis ou français simple, format : style + BPM + instruments + groove + humeur + arrangement. N’y joindre aucune parole : l’API officielle Small est text-to-music, pas un contrôle paroles/chant. Pour les IDs 09–10, demander l’arrangement instrumental qui accompagnerait la chanson et noter le test vocal comme non applicable.

Exemple ID 10 :

```text
Instrumental backing track for French melodic rap, 92 BPM, soft hip-hop drums, nocturnal piano motif, deep warm bass, restrained modern production, emotional but determined progression, no vocals.
```

### Stable Audio 3 Small-Music

Composer un paragraphe descriptif. Le guide Stability recommande genre, instruments, mood/energy et BPM; `TrackType: Music`, `VocalType: Instrumental`, `Genre:` et `Instruments:` sont des tags reconnus de son guide. Les demandes de voix/lyrics sont converties en versions instrumentales pour éviter de juger le modèle sur une capacité non annoncée.

Exemple ID 10 :

```text
TrackType: Music, VocalType: Instrumental, Genre: melodic hip-hop, Instruments: soft electronic drums, nocturnal piano, deep bass. 92 BPM, a restrained verse groove building toward a memorable melodic hook, intimate and determined mood, polished modern studio mix, no speech, no vocals.
```

## Grille de tri à appliquer à chaque fichier

Avant écoute humaine, contrôler le décodage, la durée, le niveau/silence, les coupures et les artefacts grossiers; marquer « à écouter » si ces contrôles passent. Conserver la date, le modèle/révision, le prompt complet, les paroles/tags, la seed, tous les paramètres effectifs, l’environnement logiciel et les mesures dans le sidecar JSON et le manifeste, selon [la règle de traçabilité](TRACABILITE_GENERATIONS.md). La validation artistique finale nécessite l’écoute dans l’UI : l’automatisation de ces contrôles ne peut pas établir à elle seule que le morceau est agréable ou fidèle au brief.

Noter de 0 à 2 pour chaque critère (0 absent/défectueux, 1 partiel, 2 satisfaisant) :

1. adéquation au brief;
2. cohérence musicale et transitions;
3. lisibilité des timbres et qualité audio;
4. absence d’artefacts / clipping / silence non demandé;
5. voix intelligible et bien intégrée (HeartMuLa uniquement; autres modèles : N/A).

**Triage technique automatique** : décodage FFmpeg réussi, durée mesurée entre 20 et 35 s, volume moyen supérieur ou égal à −45 dBFS et crête inférieure à −0,05 dBFS. Enregistrer les silences d’au moins une seconde sous −45 dBFS comme indicateur à examiner; ne pas les assimiler automatiquement à un défaut artistique. Un échec de décodage, une durée hors plage, un niveau moyen sous le seuil ou un écrêtage probable invalide la sortie techniquement. Une sortie qui passe est classée « écoute requise »; cela ne valide ni son rendu musical ni son adéquation au brief.

Après écoute dans l’UI, noter de 0 à 2 pour chaque critère (0 absent/défectueux, 1 partiel, 2 satisfaisant) : adéquation au brief; cohérence musicale et transitions; lisibilité des timbres et qualité audio; absence d’artefacts / clipping / silence non demandé; voix intelligible et bien intégrée (HeartMuLa uniquement; autres modèles : N/A). Le score de 6/10 pour HeartMuLa ou 5/8 pour une sortie instrumentale est un seuil d’évaluation humaine, pas un résultat que l’analyse automatique peut attribuer. Consigner séparément résultat technique et résultat d’écoute.
