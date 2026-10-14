# Système d'apprentissage de la génération

Base de règles et de préférences relue par script avant chaque génération. Ce n'est pas un entraînement de modèle : ni Claude ni les modèles de génération n'apprennent entre deux sessions. Le système conserve des préférences mesurées et des règles par modèle, et ne change qu'avec l'accord de l'utilisateur.

Plan d'ensemble : `roadmap_ecriture_humaine.md`.

## Emplacements
| Fichier | Rôle | Écrit par |
|---|---|---|
| `DOCUMENTATION/apprentissage/preferences.json` | Préférences validées, seules utilisées pour proposer des styles | `diff_preferences.py --appliquer`, après accord |
| `DOCUMENTATION/apprentissage/preferences.proposition.json` | Préférences recalculées, en attente | `calculer_preferences.py` |
| `DOCUMENTATION/apprentissage/historique/` | Versions précédentes de `preferences.json` | `diff_preferences.py --appliquer` |
| `DOCUMENTATION/apprentissage/regles_modeles.json` | Capacités, limites et formatage par modèle, opérations d'adaptation de texte | Mise à jour proposée, appliquée après accord |
| `DOCUMENTATION/apprentissage/propositions/` | 3 styles et adaptations proposés par texte | Phase 4 |
| `DOCUMENTATION/apprentissage/plan_run.json` | Choix de l'utilisateur, entrée du run | Phase 4 |
| `DOCUMENTATION/apprentissage/run_state.json` | Avancement du run, reprise | `run_textes.py` |
| `OUTILS/apprentissage/` | `calculer_preferences.py`, `diff_preferences.py` (tests : `test_apprentissage.py`) | - |
| `OUTILS/extraction_paroles/` | Extraction locale des textes photographiés (Ollama, `qwen2.5vl`) | - |
| `OUTILS/run_textes/` | `run_textes.py` : run automatique depuis `plan_run.json`, avec `--simulation` | - |

## Sources des préférences
- Retenues : votes radio `webradio/votes.json` (872 morceaux votés au 2026-10-11 : 393 positifs, 463 négatifs, 16 nuls), avec les `config.json` des playlists (caption, type, langue, durée) et les caractéristiques audio (`.feat.json` : tempo, brillance, niveau, dynamique) ; morceaux supprimés via `webradio/learning/morceaux_rejetes.jsonl`.
- Archives de votes : `DOCUMENTATION/apprentissage/votes_archive/*.json` (photos de `webradio/votes.json` prises juste avant une remise à zéro des scores). `calculer_preferences.py` somme, par morceau, les pouces haut et bas des archives et de `votes.json` courant ; `--sans-archive` les ignore. Règle : une archive est une photo prise avant la remise à zéro ; ne jamais archiver une copie de `votes.json` sans remettre ensuite les scores à zéro, sinon les votes sont comptés deux fois. Première archive : `votes_avant_remise_a_zero_2026-10-15.json` (remise à zéro du 2026-10-15).
- Exclues : avis Slow/Medium/High, pouces et commentaires des Tests.
- Limites : un vote par morceau en général (signal binaire) ; les morceaux générés avant le 2026-10-11 en rotation ont une graine aléatoire non relevée, donc leurs préférences portent sur le style et le caption, pas sur la graine. Depuis le 2026-10-11, `ace_worker.py` tire et enregistre la graine (`seed`, `seed_source` dans `playlist_results.json`) ; des captions de playlists « esprit » contiennent des références d'artistes, à ne jamais reprendre dans un caption proposé.

## Schéma de `preferences.json` (à figer en phase 2)
```json
{
  "version": 1,
  "calcule_le": "AAAA-MM-JJTHH:MM:SS+02:00",
  "sources": {"votes": "webradio/votes.json", "morceaux_votes": 0},
  "modeles": {
    "ace-step-1.5-turbo": {
      "mots_cles_caption": [{"terme": "acoustic folk", "pour": 0, "contre": 0, "taux": 0.0}],
      "familles_style": [{"famille": "folk", "pour": 0, "contre": 0, "taux": 0.0}],
      "tempo": {"aime": [0, 0], "rejete": [0, 0]},
      "duree_s": {"aime": [0, 0]},
      "voix": [{"type": "male", "pour": 0, "contre": 0}]
    }
  },
  "effectif_minimum": 5
}
```
Une préférence dont l'effectif est inférieur à `effectif_minimum` est signalée comme indicative.

## Opérations d'adaptation de texte (catalogue de `regles_modeles.json`)
Chaque opération est proposée avec la ligne avant et après, et appliquée seulement si l'utilisateur l'accepte. Le texte source n'est jamais modifié : l'adaptation est écrite dans une copie.

| Opération | Moyen ACE-Step 1.5 | État |
|---|---|---|
| Silence avant une phrase | Balise `[Silence]` sur sa propre ligne | Testé (démo T01, version 18 retenue) |
| Mise en lumière d'un mot ou d'une phrase | Majuscules | Hypothèse (documentation ACE) |
| Écho ou chœur | Parenthèses | Hypothèse (documentation ACE) |
| Respiration entre sections | `[Instrumental]`, `[Breakdown]` | Hypothèse |
| Refrain | Balise `[chorus]` ; « Ref : » d'un texte imprimé devient `[chorus]` | Testé |
| Répétition d'un refrain | Recopie de la section `[chorus]` | Pratique courante du projet |
| Ligne trop longue (plus de 10 syllabes) | Signalement par `check_lyrics.py`, découpe proposée | Règle du skill |

## Mise à jour
1. `calculer_preferences.py` écrit la proposition.
2. `/close` lance `diff_preferences.py` et montre le diff.
3. L'utilisateur accepte ou refuse ; `--appliquer` seulement après acceptation.
Aucune mise à jour automatique.
