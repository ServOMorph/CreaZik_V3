import socket
import subprocess
import time
import webbrowser
from pathlib import Path

WEBRADIO = Path(__file__).resolve().parent / "webradio"
PORT = 5000
URL = f"http://localhost:{PORT}/"
ADMIN_PORT = 5001
ADMIN_URL = f"http://localhost:{ADMIN_PORT}/radio.html"


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(WEBRADIO / "services.ps1"), "start"],
        cwd=WEBRADIO,
        check=False,
    )
    for _ in range(60):
        if port_open(PORT) and port_open(ADMIN_PORT):
            break
        time.sleep(0.5)
    else:
        print("Les interfaces ne répondent pas sur les ports", PORT, "et", ADMIN_PORT)
        return
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(WEBRADIO / "services.ps1"), "status"],
        cwd=WEBRADIO,
        check=False,
    )
    webbrowser.open(URL)
    webbrowser.open(ADMIN_URL)


if __name__ == "__main__":
    main()
