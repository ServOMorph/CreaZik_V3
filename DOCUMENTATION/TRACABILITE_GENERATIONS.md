# Traçabilité des générations musicales

Règle durable du projet : chaque morceau généré doit conserver sa date, son modèle précis, son prompt et tous les paramètres effectifs qui peuvent influencer le résultat. La campagne comparative de MODELES_LLM applique cette règle piste par piste.

## Fichiers de suivi

- Un MP3 lisible dans l’UI de test.
- Un fichier sidecar `nom_du_morceau.metadata.json` à côté du MP3 avec les entrées, paramètres, versions et résultats de contrôle détaillés.
- Un `generation_manifest.json` qui référence toutes les sorties et leur statut. Il est mis à jour après chaque essai pour permettre une reprise.
- Le fichier `playlist_results.json` de l’UI contient au minimum le nom, l’horodatage, le modèle, le prompt, la durée, la seed et le chemin MP3; il renvoie vers le sidecar complet.

Les fichiers générés restent hors Git. Les sidecars et manifests ne contiennent aucun secret ni jeton d’accès.

Le worker ACE produit ces métadonnées à chaque essai. Les campagnes de modèles externes les créent avec `MODELES_LLM/registre_campagne.py`; toute nouvelle intégration de génération doit appeler ce registre ou fournir les mêmes champs avant d’exposer sa piste dans l’UI.

## Champs obligatoires par morceau

| Champ | Contenu |
|---|---|
| `generated_at` | Date/heure ISO 8601 avec fuseau, idéalement `Europe/Paris`. |
| `model_name` / `model_version` | Nom public exact, variant, révision du dépôt et identifiant Hugging Face si applicable. |
| `runtime` | OS, version Python, versions Torch/Transformers/AudioCraft ou runtime TFLite, backend et appareil CPU/GPU. |
| `test_case_id` / `title` | ID stable du brief et nom lisible du fichier. |
| `prompt` | Texte exact envoyé au modèle, sans reformulation. |
| `lyrics` / `tags` / `input_files` | Paroles et tags exacts, ou fichiers audio d’entrée, lorsque le modèle en utilise. |
| `generation_config` | Tous les paramètres effectifs, y compris les valeurs par défaut appliquées : durée, seed, steps, CFG/guidance, top-k, température, dtype, appareils, quantification et paramètres propres au runtime. |
| `output` | Chemin, format, codec, fréquence, canaux, durée mesurée, taille et hash SHA-256 du MP3 livré. |
| `analysis` | Vérifications automatiques, mesures, score par critère et motif de validation/invalidation technique. |
| `listening_review` | Champ initialisé à `pending`; résultat d’écoute/vote et commentaires utilisateur ultérieurs. |

## Statuts

- `generated`: le moteur a fini et a créé une sortie audio.
- `invalid`: le fichier échoue à un contrôle technique reproductible; inscrire le motif et les mesures.
- `needs_listening`: les contrôles techniques passent; qualité artistique ou adhérence sémantique non décidée par un test automatique.
- `listened_valid` / `listened_invalid`: statut d’écoute humaine, à renseigner seulement après une écoute.

Ne jamais annoncer une validation artistique si seul le décodage, la durée ou le niveau ont été examinés. Garder prompts, configurations, tentatives et erreurs même après une génération invalide; ne pas écraser la configuration d’un résultat antérieur.
