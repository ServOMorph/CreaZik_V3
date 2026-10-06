---
description: Arrête uniquement le batch de pochettes et ComfyUI-Qwen, puis libère la VRAM
allowed-tools: PowerShell, Bash(nvidia-smi:*)
---

# /stop_covers

Arrête la génération des pochettes en cours et ferme ComfyUI-Qwen pour libérer les ressources de l'IA locale. Ne pas arrêter les services de diffusion, d'analyse, de compression ou de génération musicale.

## Procédure

1. Créer le signal d'arrêt du batch, puis terminer uniquement les processus de génération des pochettes et ComfyUI-Qwen :
   ```powershell
   New-Item -ItemType Directory -Force -Path D:\ServOMorph\CreaZik_V3\webradio\logs | Out-Null
   Set-Content -Path D:\ServOMorph\CreaZik_V3\webradio\logs\stop_covers.request -Value 'stop' -NoNewline
   Get-CimInstance Win32_Process | Where-Object {
     ($_.Name -match 'python' -and $_.CommandLine -match 'webradio[\\/]tools[\\/](cover_batch|cover_gen)\.py') -or
     ($_.Name -match 'python' -and $_.CommandLine -match 'ComfyUI-Qwen.*main\.py --port 8189')
   } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
   ```
2. Contrôler que ComfyUI ne répond plus sur le port 8189 et afficher la VRAM :
   ```powershell
   Get-NetTCPConnection -State Listen -LocalPort 8189 -ErrorAction SilentlyContinue
   nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
   ```
3. La reprise se fait avec `/generate_covers` : les pochettes déjà créées sont conservées et ignorées.
