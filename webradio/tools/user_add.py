import argparse
import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import accounts

ENV_VAR = "CREAZIK_USER_PASSWORD"


def main():
    p = argparse.ArgumentParser(description="Crée ou remplace un compte de profil (jamais admin).")
    p.add_argument("user", help="identifiant (comparé sans tenir compte de la casse)")
    p.add_argument("profile", help="identifiant du profil (fichier webradio/profiles/<profil>.json)")
    a = p.parse_args()
    password = os.environ.get(ENV_VAR)
    if password is None:
        password = getpass.getpass("Mot de passe : ")
        if getpass.getpass("Confirmation : ") != password:
            sys.exit("Les mots de passe diffèrent.")
    try:
        uid = accounts.add_account(a.user, password, a.profile)
    except ValueError as e:
        sys.exit(f"Erreur : {e}")
    print(f"Compte « {uid} » enregistré avec le profil « {a.profile} » dans {accounts.ACCOUNTS_FILE.name}.")


if __name__ == "__main__":
    main()
