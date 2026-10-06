---
description: Arrête uniquement la file musicale en préservant l'avancement par piste
---

# /stop_generation

Arrête la génération musicale sans arrêter les interfaces radio, l'analyse ni la compression. Les résultats de chaque piste sont enregistrés de façon atomique ; au prochain lancement, les pistes déjà `generated` seront ignorées et la piste interrompue sera retentée.

Depuis la racine du projet, lancer :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\webradio\services.ps1 stop -Only generation
```

Confirmer l'arrêt avec :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\webradio\services.ps1 status
```

Ne pas lancer `/generate_covers` avant d'avoir arrêté ACE-Step : les deux utilisent le GPU local.
