"""Run automatique : une version par entree de plan_run.json, publiee dans la section Tests.

Lit DOCUMENTATION/apprentissage/plan_run.json (choix de l'utilisateur) et regles_modeles.json.
Ecrit seulement dans webradio/tests_ace/funky_yogi_textes/ et webradio/playlists/tests-ace/,
plus run_state.json. Echec technique (erreur, delai, fichier absent, duree incoherente) :
nouvelle graine de regles_modeles.json, 3 tentatives au plus, puis statut ECHEC.

Usage : python OUTILS/run_textes/run_textes.py [--racine <dossier>] [--simulation] [--texte <id>]
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import wave
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
FFMPEG = Path(r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe")
BITRATE = "192k"
TENTATIVES = 3
DELAI_S = 3600
VRAM_MIN_MO = 2048
DOSSIER_TESTS = "tests_ace/funky_yogi_textes"
FOLDER = "Funky Yogi"


class Arret(Exception):
    pass


def lire(chemin, defaut=None):
    try:
        return json.loads(Path(chemin).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defaut


def ecrire_json(chemin, data):
    chemin = Path(chemin)
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for _ in range(40):
        try:
            return os.replace(tmp, chemin)
        except PermissionError:
            time.sleep(0.25)
    os.replace(tmp, chemin)


def verifier_ecriture(racine, chemin):
    web = (racine / "webradio").resolve()
    autorises = [web / DOSSIER_TESTS, web / "playlists" / "tests-ace",
                 racine.resolve() / "DOCUMENTATION" / "apprentissage" / "run_state.json"]
    p = Path(chemin).resolve()
    if not any(p == a or a in p.parents for a in autorises):
        raise Arret(f"ecriture refusee hors zone autorisee : {p}")


def vram_libre_mo():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout
        return int(out.strip().splitlines()[0])
    except Exception:
        return None


def prochain_numero(racine):
    res = lire(racine / "webradio" / "playlists" / "tests-ace" / "outputs" / "playlist_results.json", {"generations": []})
    nums = [int(m.group(1)) for g in res.get("generations", []) if (m := re.match(r"\s*(\d+)\s", str(g.get("name", ""))))]
    return max(nums, default=0) + 1


def controle_paroles(racine, fichier, caption, duree):
    r = subprocess.run([sys.executable, str(racine / "TEXTES" / "tools" / "check_lyrics.py"), str(fichier),
                        "--caption", caption, "--duree", str(duree)], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def duree_wav(chemin):
    with open(chemin, "rb") as f:
        tete = f.read(65536)
    pos, debit = 12, None
    while pos + 8 <= len(tete):
        cid = tete[pos:pos + 4]
        taille = struct.unpack("<I", tete[pos + 4:pos + 8])[0]
        if cid == b"fmt ":
            debit = struct.unpack("<I", tete[pos + 16:pos + 20])[0]
        elif cid == b"data" and debit:
            return (Path(chemin).stat().st_size - (pos + 8)) / debit
        pos += 8 + taille + (taille & 1)
    raise ValueError(f"en-tete wav illisible : {chemin}")


def generer_reel(racine, config_rel, delai):
    web = racine / "webradio"
    cmd = [sys.executable, str(web / "generate.py"), config_rel, "--only", "1"]
    try:
        r = subprocess.run(cmd, cwd=web, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=delai)
    except subprocess.TimeoutExpired:
        return "delai de {} s depasse".format(delai)
    return None if r.returncode == 0 else f"generate.py code {r.returncode} : {(r.stderr or r.stdout)[-300:]}"


def generer_simulation(racine, config_rel, delai):
    web = racine / "webradio"
    cfg = lire(web / config_rel)
    case = cfg["test_cases"][0]
    sortie = web / cfg["output_dir"]
    sortie.mkdir(parents=True, exist_ok=True)
    nom = f"01_{case['name']}_sim_s{case.get('seed', 0)}.wav"
    with wave.open(str(sortie / nom), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 8000 * int(case["duration"]))
    ecrire_json(sortie / "playlist_results.json", {"model": "ACE-Step 1.5 turbo (simulation)", "generations": [{
        "test_case_id": "1", "name": case["name"], "prompt": case["prompt"], "type": case["type"],
        "duration": case["duration"], "output_file": f"{cfg['output_dir'].lstrip('./')}/{nom}",
        "seed": case.get("seed", 0), "seed_source": "config", "status": "generated",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "model": "ACE-Step 1.5 turbo (simulation)"}]})
    return None


def convertir_mp3(wav, mp3):
    tmp = mp3.with_name(mp3.stem + ".tmp.mp3")
    r = subprocess.run([str(FFMPEG), "-y", "-loglevel", "error", "-i", str(wav), "-vn", "-codec:a", "libmp3lame",
                        "-b:a", BITRATE, "-ar", "44100", "-id3v2_version", "3", str(tmp)], capture_output=True, text=True)
    if r.returncode != 0 or not tmp.exists():
        tmp.unlink(missing_ok=True)
        return f"conversion mp3 echouee : {r.stderr.strip()[:200]}"
    os.replace(tmp, mp3)
    return None


def une_tentative(racine, texte, version, seed, simulation, duree_max, delai):
    web = racine / "webradio"
    vid = f"{texte['id']}_{version['id']}"
    base = web / DOSSIER_TESTS / vid
    verifier_ecriture(racine, base)
    (base / "outputs").mkdir(parents=True, exist_ok=True)
    paroles = racine / version["paroles"]
    if not paroles.is_file():
        raise Arret(f"fichier de paroles absent : {paroles}")
    copie = base / "paroles.md"
    shutil.copyfile(paroles, copie)
    duree = min(int(version["duree_s"]), duree_max)
    case = {"id": "1", "name": vid, "prompt": version["caption"], "type": "vocal", "duration": duree,
            "lyrics_file": f"{DOSSIER_TESTS}/{vid}/paroles.md", "fit_lyrics": False,
            "language": version.get("langue", "fr"), "seed": seed}
    if version.get("bpm"):
        case["bpm"] = int(version["bpm"])
    ace = lire(web / "playlists" / "tests-ace" / "config.json", {}).get("ace_step_path", "D:/ServOMorph/ACE-Step-1.5")
    config_rel = f"{DOSSIER_TESTS}/{vid}/config.json"
    ecrire_json(web / config_rel, {"playlist_name": f"Funky Yogi {vid}", "ace_step_path": ace,
                                   "output_dir": f"./{DOSSIER_TESTS}/{vid}/outputs", "test_cases": [case]})
    for ancien in (base / "outputs").glob("*.wav"):
        ancien.unlink()
    erreur = (generer_simulation if simulation else generer_reel)(racine, config_rel, delai)
    if erreur:
        return None, erreur
    res = lire(base / "outputs" / "playlist_results.json", {})
    gens = res.get("generations", [])
    if not gens or gens[0].get("status") != "generated":
        return None, f"statut {gens[0].get('status') if gens else 'absent'} : {gens[0].get('error', '') if gens else ''}"
    g = gens[0]
    wav = web / g["output_file"]
    if not wav.is_file():
        return None, f"fichier audio absent : {wav}"
    try:
        reel = duree_wav(wav)
    except Exception as e:
        return None, str(e)
    if reel < 0.6 * duree or reel > duree + 5:
        return None, f"duree incoherente : {reel:.1f} s pour {duree} s demandees"
    return {"generation": g, "wav": wav, "duree_reelle_s": round(reel, 1)}, None


def publier(racine, texte, version, res):
    web = racine / "webradio"
    sortie = web / "playlists" / "tests-ace" / "outputs"
    verifier_ecriture(racine, sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    num = prochain_numero(racine)
    g = res["generation"]
    nom_aff = f"{num:02d} · {texte['titre']}, {version['label']}, {res['duree_reelle_s']:.0f} s, graine {g['seed']}"
    fichier = f"{num:02d}_{texte['id']}_{version['id']}_seed{g['seed']}.mp3"
    mp3 = sortie / fichier
    erreur = convertir_mp3(res["wav"], mp3)
    if erreur:
        return None, erreur
    d_mp3 = mp3.stat().st_size * 8 / (int(BITRATE[:-1]) * 1000)
    if abs(d_mp3 - res["duree_reelle_s"]) > max(1.5, res["duree_reelle_s"] * 0.03):
        mp3.unlink(missing_ok=True)
        return None, f"duree mp3 incoherente : {d_mp3:.1f} s pour {res['duree_reelle_s']} s"
    chemin_res = sortie / "playlist_results.json"
    data = lire(chemin_res, {"playlist": "Tests ACE", "mode": "real", "model": "ACE-Step 1.5 turbo", "generations": []})
    entree = {
        "test_case_id": str(num), "name": nom_aff, "prompt": g["prompt"], "type": g["type"], "duration": res["duree_reelle_s"],
        "output_file": f"playlists/tests-ace/outputs/{fichier}", "status": "generated",
        "generated_at": g.get("generated_at"), "model": g.get("model", "ACE-Step 1.5 turbo"),
        "seed": g["seed"], "seed_source": g.get("seed_source"), "folder": FOLDER, "reference": texte["source"],
        "metadata_file": g.get("metadata_file", ""),
    }
    plan_id = f"{texte['id']}_{version['id']}"
    data["generations"] = [x for x in data["generations"] if not (x.get("status") == "planned" and x.get("plan_id") == plan_id)]
    data["generations"].append(entree)
    ecrire_json(chemin_res, data)
    res["wav"].unlink(missing_ok=True)
    return entree, None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--racine", default=str(RACINE))
    p.add_argument("--simulation", action="store_true", help="aucun GPU : WAV silencieux ; exige --racine hors projet")
    p.add_argument("--texte", default="")
    a = p.parse_args()
    racine = Path(a.racine)
    if a.simulation and racine.resolve() == RACINE.resolve():
        sys.exit("simulation refusee sur la racine reelle du projet : donner --racine")
    dossier = racine / "DOCUMENTATION" / "apprentissage"
    plan = lire(dossier / "plan_run.json")
    regles = lire(dossier / "regles_modeles.json")
    if not plan or not regles:
        sys.exit("plan_run.json ou regles_modeles.json absent")
    graines = regles["graines_de_reprise"]
    duree_max = regles["modeles"]["ace-step-1.5-turbo"]["duree_max_s"]
    etat_chemin = dossier / "run_state.json"
    etat = lire(etat_chemin, {"versions": {}})
    for texte in plan["textes"]:
        if a.texte and texte["id"] != a.texte:
            continue
        for version in texte["versions"]:
            cle = f"{texte['id']}_{version['id']}"
            if etat["versions"].get(cle, {}).get("statut") in ("TERMINE", "ECHEC"):
                continue
            ent = etat["versions"].setdefault(cle, {"statut": "EN_COURS", "tentatives": []})
            utilisees = {t["graine"] for t in ent["tentatives"]}
            premiere = version.get("graine") if version.get("graine") is not None else -1
            candidates = [premiere] + [s for s in graines if s != premiere]
            restant = TENTATIVES - len(ent["tentatives"])
            fini = False
            for seed in [s for s in candidates if s not in utilisees][:restant]:
                if not a.simulation:
                    libre = vram_libre_mo()
                    if libre is not None and libre < VRAM_MIN_MO:
                        ecrire_json(etat_chemin, etat)
                        sys.exit(f"ARRET : VRAM libre {libre} Mo < {VRAM_MIN_MO} Mo avant {cle}")
                    cr, sortie = controle_paroles(racine, racine / version["paroles"], version["caption"], int(version["duree_s"]))
                    if cr != 0:
                        ecrire_json(etat_chemin, etat)
                        sys.exit(f"ARRET : check_lyrics signale une ERREUR pour {cle}\n{sortie}")
                debut = time.time()
                res, erreur = une_tentative(racine, texte, version, seed, a.simulation, duree_max, DELAI_S)
                entree = None
                if res:
                    entree, erreur = publier(racine, texte, version, res)
                trace = {"graine": seed, "duree_calcul_s": round(time.time() - debut, 1)}
                if entree:
                    trace.update(resultat="OK", graine_reelle=entree["seed"], test=entree["name"])
                    ent["tentatives"].append(trace)
                    ent.update(statut="TERMINE", fichier=entree["output_file"], graine=entree["seed"])
                    fini = True
                else:
                    trace.update(resultat="ECHEC", cause=erreur)
                    ent["tentatives"].append(trace)
                    print(f"{cle} graine {seed} : ECHEC {erreur}", flush=True)
                ecrire_json(etat_chemin, etat)
                if fini:
                    print(f"{cle} : TERMINE ({ent['fichier']})", flush=True)
                    break
            if not fini:
                ent["statut"] = "ECHEC"
                ent["cause"] = ent["tentatives"][-1]["cause"] if ent["tentatives"] else "aucune tentative"
                ecrire_json(etat_chemin, etat)
                print(f"{cle} : ECHEC apres {len(ent['tentatives'])} tentative(s) : {ent['cause']}", flush=True)


if __name__ == "__main__":
    main()
