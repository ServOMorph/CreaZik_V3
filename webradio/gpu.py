import json
import subprocess
import threading
import urllib.request
from pathlib import Path

PAUSE_FLAG = Path(__file__).parent / "gpu_pause.flag"
COMFY = "http://127.0.0.1:8189"
OLLAMA = "http://127.0.0.1:11434"
LOCK = threading.Lock()
ROTATION_RE = r"run_rotation\.py|run_queue\.py|ace_worker\.py|generate\.py|run_series\.sh"
OWN_MARKER = "creations-auditeurs"


def paused():
    return PAUSE_FLAG.exists()


def rotation_running():
    command = ("$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|bash' -and "
               f"$_.CommandLine -match '{ROTATION_RE}' -and $_.CommandLine -notmatch '{OWN_MARKER}' }}; if ($p) {{ 'ACTIVE' }}")
    result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
    return "ACTIVE" in result.stdout


def own_worker_running():
    command = ("$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and "
               f"$_.CommandLine -match 'ace_worker\\.py' -and $_.CommandLine -match '{OWN_MARKER}' }}; if ($p) {{ 'ACTIVE' }}")
    result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
    return "ACTIVE" in result.stdout


def _post(url, body, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def free_comfy():
    try:
        _post(COMFY + "/free", {"unload_models": True, "free_memory": True})
        return True
    except OSError:
        return False


def comfy_queue_size():
    try:
        with urllib.request.urlopen(COMFY + "/queue", timeout=5) as r:
            q = json.load(r)
    except (OSError, ValueError):
        return 0
    return len(q.get("queue_running", [])) + len(q.get("queue_pending", []))


def loaded_ollama_models():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=5) as r:
            return [m.get("name") or m.get("model") for m in json.load(r).get("models", [])]
    except (OSError, ValueError):
        return []


def free_ollama():
    for name in loaded_ollama_models():
        try:
            _post(OLLAMA + "/api/generate", {"model": name, "keep_alive": 0}, timeout=30)
        except OSError:
            pass
