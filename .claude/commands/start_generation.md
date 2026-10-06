---
description: Démarre uniquement la file de génération musicale et reprend les pistes incomplètes
---

# /start_generation

Lance uniquement le service de génération musicale. La reprise se fait depuis les statuts `generated` par piste dans `webradio/playlists/<id>/outputs/playlist_results.json` ; les pistes déjà terminées sont ignorées.

1. Vérifier que `/generate_covers` et ComfyUI-Qwen ne sont pas en cours d'utilisation, afin d'éviter la concurrence sur le GPU. Si ComfyUI ou le batch de pochettes tourne, arrêter le batch avec `/stop_covers` avant de continuer.
2. Depuis la racine du projet, lancer :
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\webradio\services.ps1 start -Only generation
   ```
3. Indiquer que la génération tourne en arrière-plan et que `/stop_generation` permet de l'arrêter. L'ordre des playlists est dans `webradio/series.txt` ; le suivi détaillé est dans `webradio/logs/rotation.log`.
