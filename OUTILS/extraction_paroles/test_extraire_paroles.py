import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import extraire_paroles as e

REPONSE = """### Miracle
Ligne un  
Ligne deux

Ref :
Refrain un

### TITRE : Mineur majeur
Ca c'est un accord mineur
"""


def test_decouper_deux_textes_et_chorus():
    t = e.decouper(REPONSE)
    assert [x[0] for x in t] == ["Miracle", "Mineur majeur"]
    assert "[chorus]\nRefrain un" in t[0][1]
    assert "  \n" not in t[0][1]


def test_slug():
    assert e.slug("Ça c'est : Déjà vu !") == "ca-c-est-deja-vu"


def test_ecrire_ne_jamais_ecraser(tmp_path):
    p = e.ecrire(tmp_path, "Miracle", "x", Path("photo.jpg"), "m")
    assert "Statut : A_RELIRE" in p.read_text(encoding="utf-8")
    try:
        e.ecrire(tmp_path, "Miracle", "y", Path("photo.jpg"), "m")
        assert False
    except FileExistsError:
        pass
