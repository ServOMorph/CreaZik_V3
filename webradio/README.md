# 🎵 CreaZik Benchmark Suite

Benchmark complet pour tester les modèles de génération musicale avec IA, en commençant par ACE-Step 1.5.

## Structure

```
benchmark/
├── config.json           # Configuration des tests
├── benchmark.py          # Runner principal
├── ace_wrapper.py        # Wrapper ACE-Step
├── model_updater.py      # Gestionnaire de modèles
├── ui.html              # Interface web explorer
├── README.md            # Cette documentation
└── outputs/             # Résultats générés (créé automatiquement)
    ├── benchmark_results.json
    ├── BENCHMARK.md
    └── *.wav            # Fichiers audio générés
```

## Configuration Initiale

### 1. Localiser ACE-Step 1.5

Mets à jour le chemin dans [config.json](config.json) :
```json
{
  "ace_step_path": "CHEMIN_VERS_ACE_STEP_1_5",
  ...
}
```

### 2. Intégrer l'appel ACE-Step

Modifie [ace_wrapper.py](ace_wrapper.py) ligne ~50 avec la commande réelle d'ACE-Step :
```python
# À décommenter et adapter avec la vraie commande ACE-Step
command = [
    str(self.ace_step_path / "generate.py"),
    "--prompt", prompt,
    "--output", output_path,
    "--duration", str(duration),
]
```

## Utilisation

### Lancer le benchmark complet
```bash
python benchmark/benchmark.py benchmark/config.json
```

Génère 10 musiques avec les prompts définis dans `config.json`.

### Explorer les résultats
```bash
# Ouvrir l'interface web (simplement ouvrir ui.html dans un navigateur)
start benchmark/ui.html
```

L'UI propose :
- 🎵 Lecteur audio pour chaque génération
- 📊 Statistiques (total, générées, échouées)
- 🏷️ Filtres par statut
- 📥 Export des résultats
- 📋 Copie des prompts

### Gérer les modèles

```bash
# Lister tous les modèles disponibles
python benchmark/model_updater.py list

# Mettre à jour le registre
python benchmark/model_updater.py update

# Vérifier le cache local
python benchmark/model_updater.py status

# Télécharger un modèle
python benchmark/model_updater.py download facebook/musicgen-medium

# Supprimer un modèle du cache
python benchmark/model_updater.py remove facebook/musicgen-medium
```

## Fichiers de Configuration

### config.json

Définit :
- `ace_step_path` : Chemin vers ACE-Step 1.5
- `output_dir` : Dossier des résultats
- `models` : Liste des modèles à tester
- `test_cases` : 10 prompts de test (genres, styles, tempo)

Exemple d'ajout d'un test :
```json
{
  "id": "11",
  "name": "Votre Genre",
  "prompt": "votre description musicale",
  "type": "instrumental",
  "duration": 30
}
```

## Workflow Complet

### Phase 1 : Benchmark ACE-Step ✓ (Actuellement)
1. Configuration
2. Lancer benchmark
3. Explorer résultats
4. Évaluer qualité

### Phase 2 : Tester autres modèles (Futur)
- MusicGen (Medium, Large)
- Stable Audio Open
- Autres modèles HuggingFace

### Phase 3 : Intégration FL Studio
- Export MIDI
- Couches audio
- Contrôle en temps réel

## Résultats & Exports

Les résultats sont sauvegardés dans `outputs/` :

- **benchmark_results.json** : Métadonnées complètes (JSON)
- **BENCHMARK.md** : Rapport texte lisible
- **{id}_{name}.wav** : Fichiers audio générés

Export possible depuis l'UI :
- JSON pour traitement ultérieur
- Fichiers individuels
- Comparaisons multi-modèles (futur)

## Notes Techniques

### Contraintes
- Génération sur machine locale (pas de cloud)
- Durée max : 30s par track (configurable)
- Format : WAV (sans perte)

### Performance
- 10 tracks ≈ 5-10 min selon la machine
- Cache HuggingFace (D:/HuggingFaceCache)
- Pas de limitation GPU (adaptive)

### Extensibilité
- Ajouter nouveaux modèles via `config.json`
- Wrapper générique pour chaque model type
- API JSON pour intégrations futures

## Troubleshooting

| Problème | Solution |
|----------|----------|
| ACE-Step non trouvé | Mettre à jour le chemin dans `config.json` |
| Pas de son généré | Vérifier intégration dans `ace_wrapper.py` |
| UI ne charge pas | Ouvrir `ui.html` localement, pas via serveur |
| Erreur modèle HF | Vérifier connexion internet, cache |

## Commandes Rapides

```bash
# Setup complet
cd benchmark
python model_updater.py update

# Lancer benchmark
python benchmark.py config.json

# Voir résultats
start ui.html

# Exporter pour comparaison
# (Via l'UI → Export Results)
```

## Prochaines Étapes

1. **Intégrer ACE-Step** : Tester génération réelle
2. **Comparer modèles** : MusicGen vs ACE-Step vs Stable Audio
3. **Créer FL Studio plugin** : Intégrer dans DAW
4. **Améliorer prompts** : Refiner via feedback utilisateur

---

**Version** : 1.0  
**Dernière mise à jour** : 2026-10-05  
**Statut** : Benchmark framework prêt, intégration ACE-Step en attente
