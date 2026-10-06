import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEBRADIO = ROOT / "webradio"
PORT = 5000
URL = f"http://localhost:{PORT}/ui.html"


def port_open():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def main():
    if port_open():
        print(f"Serveur deja actif : {URL}")
        webbrowser.open(URL)
        return
    proc = subprocess.Popen([sys.executable, "server.py", "--port", str(PORT), "--no-browser"], cwd=WEBRADIO)
    for _ in range(40):
        if port_open():
            break
        if proc.poll() is not None:
            sys.exit(proc.returncode)
        time.sleep(0.25)
    webbrowser.open(URL)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
