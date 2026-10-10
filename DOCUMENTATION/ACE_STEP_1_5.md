# ACE-Step 1.5

Rôle : modèle de référence déjà présent dans le projet. Cette fiche reprend les recherches antérieures de `MODELES_LLM/recherche_modeles_generation_musicale.md`, puis les complète avec le dépôt local et la documentation officielle consultés le 9 octobre 2026.

## Capacités et limites

ACE-Step 1.5 associe un modèle de planification linguistique (LM) et un DiT de génération audio. Le dépôt annonce des paroles en plus de 50 langues, la génération instrumentale, le contrôle de métadonnées (BPM, tonalité, durée), le remix/couverture et le repaint. Ces capacités sont celles déclarées par le projet, pas une garantie de qualité.

Le README actuel recommande le DiT 2B Turbo pour les GPU de 6 à 8 Go, avec le LM léger 0,6B configuré pour cette tranche. Il indique l’offload CPU et la quantification INT8 pour les petites cartes. Les modèles XL 4B nécessitent au minimum 12 Go avec offload selon le README; ils ne sont pas adaptés à la RTX 4060 8 Go du projet.

Le worker local `webradio/ace_worker.py` initialise `acestep-v15-turbo`, choisit `device="auto"`, active `offload_to_cpu=True`, et n’initialise le LM 0,6B que si l’option `--lm` est passée. Il transmet caption, paroles, instrumental, langue, durée, BPM et seed. Il règle actuellement 8 étapes d’inférence et `guidance_scale=1.0`. Ce comportement local prévaut sur les réglages d’exemples provenant d’autres versions du dépôt.

## Utilisation recommandée

1. Pour une demande courte et exploratoire, activer le mode de réflexion/LM et donner une intention claire; laisser le LM proposer le plan, les métadonnées et les paroles.
2. Pour une comparaison reproductible, désactiver le LM si le caption, les paroles et métadonnées sont déjà fixés; imposer une seed et enregistrer tous les paramètres.
3. Décrire dans le caption le genre, les instruments, le caractère rythmique, l’ambiance, le type de voix et le rendu de production. Éviter les demandes vagues ou contradictoires.
4. Structurer les paroles avec des sections sur des lignes seules : `[Intro]`, `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`. Mettre les paroles françaises entre les sections et préciser le français dans le champ de langue.
5. Pour un instrumental, utiliser le paramètre instrumental plutôt que d’ajouter des paroles fictives.

## Exemple prêt à adapter

**Caption**

```text
French melodic electro-pop, 116 BPM, warm analog synth bass, crisp electronic drums, bright arpeggiated synths, intimate male lead vocal, restrained verses opening into a wide memorable chorus, polished modern mix, bittersweet but hopeful mood.
```

**Paroles**

```text
[Intro]

[Verse 1]
La ville s’allume au bord du soir
Je garde un peu de ciel en moi
Les rues défilent sans parler
Je cherche où poser mes pensées

[Chorus]
On avance au milieu des lumières
Même quand la nuit revient derrière
Un pas de plus, le cœur ouvert
On fera danser la poussière

[Outro]
```

Régler séparément la langue `fr`, le BPM et la durée; les mots « autotune » ou « voix masculine » ne garantissent pas le résultat, ils doivent être évalués à l’écoute.

## Procédure et sources

- Procédure du projet : `webradio/generate.py <config>`, qui appelle `ace_worker.py`; consulter ces scripts avant de changer le pipeline.
- Dépôt local consulté : `D:/ServOMorph/ACE-Step-1.5`, révision `ca1e85f` au moment de la lecture.
- [README officiel](https://github.com/ace-step/ACE-Step-1.5)
- [Guide officiel d’inférence](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md)
- [Guide officiel de formulation pour musiciens](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md)
