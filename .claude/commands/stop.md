---
description: Arrête tous les services de la WebRadio et libère le PC des IA locales (VRAM)
model: haiku
allowed-tools: PowerShell, Bash(nvidia-smi:*)
---

# /stop

Arrête tout ce qui tourne pour CreaZik_V3 et libère la carte graphique. Le tunnel Cloudflare n'est pas touché (lancé à la main par l'utilisateur).

## Procédure

1. Arrêter les services du projet (serveur, analyse, compression, génération, rotation, workers ACE-Step) :
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File D:\ServOMorph\CreaZik_V3\webradio\services.ps1 stop
   ```

2. Arrêter ComfyUI-Qwen (port 8189), l'environnement Kokoro et tout processus Python restant du projet qui occupe la carte :
   ```powershell
   Get-CimInstance Win32_Process | Where-Object {
     $_.Name -match 'python' -and $_.CommandLine -match 'ComfyUI-Qwen|main\.py --port 8189|TTS_Local|ace_worker|run_rotation|generate\.py|run_queue|analyze_viz|compress_audio|CreaZik_V3.webradio.server\.py'
   } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
   ```

3. Décharger les modèles Ollama chargés, sans arrêter l'application. Ne l'interroger que si elle tourne déjà (`ollama ps` la démarre sinon) :
   ```powershell
   if (Get-Process -Name 'ollama*','llama-server' -ErrorAction SilentlyContinue) { ollama ps }
   ```
   Pour chaque modèle listé : `ollama stop <modèle>`.

4. Contrôler le résultat et l'afficher :
   ```powershell
   nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
   powershell -NoProfile -ExecutionPolicy Bypass -File D:\ServOMorph\CreaZik_V3\webradio\services.ps1 status
   ```
   Si la VRAM utilisée reste élevée, lister les processus restants (`nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`) et les signaler sans les arrêter.

5. Terminer par : « Tout est arrêté. Pour relancer : `python run.py` dans D:\ServOMorph\CreaZik_V3 (ComfyUI-Qwen se lance à part avec lancer.bat). »

Ne rien commiter, ne rien modifier dans les fichiers du projet.
