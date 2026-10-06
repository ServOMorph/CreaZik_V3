import socket
import subprocess
import time
import webbrowser
from pathlib import Path

WEBRADIO = Path(__file__).resolve().parent / "webradio"
PORT = 5000
URL = f"http://localhost:{PORT}/ui.html"


def port_open():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def main():
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(WEBRADIO / "services.ps1"), "start"],
        cwd=WEBRADIO,
        check=False,
    )
    for _ in range(60):
        if port_open():
            break
        time.sleep(0.5)
    else:
        print("Le serveur ne repond pas sur le port", PORT)
        return
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(WEBRADIO / "services.ps1"), "status"],
        cwd=WEBRADIO,
        check=False,
    )
    webbrowser.open(URL)


if __name__ == "__main__":
    main()
