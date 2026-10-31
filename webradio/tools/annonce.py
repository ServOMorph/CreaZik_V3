import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TTS = Path(r"D:\ServOMorph\TTS_Local")
os.environ.setdefault("HF_HOME", str(TTS / "hf_cache"))

WEB = Path(__file__).resolve().parent.parent
FOLDER = "annonces"
PID = "jingles-annonces"
LABEL = "Annonces"
OUT = WEB / "jingles" / FOLDER / "outputs"
RESULTS = OUT / "playlist_results.json"
REQUESTS = WEB / "annonces_requests"
REF = TTS / "samples" / "kokoro_ff_siwis.wav"
MODEL = "Chatterbox multilingue (voix locale, timbre féminin)"
KOKORO_MODEL = "Kokoro ff_siwis (voix locale, processeur)"
KOKORO_VOICE = "ff_siwis"


def synthesize(text, wav_path):
    import soundfile as sf
    import torch
    torch.set_num_threads(6)
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    wav = model.generate(text, language_id="fr", audio_prompt_path=str(REF), exaggeration=0.4, cfg_weight=0.1, temperature=0.7)
    sf.write(str(wav_path), wav.squeeze().cpu().numpy(), model.sr)


def synthesize_kokoro(text, wav_path):
    import numpy as np
    import soundfile as sf
    import torch
    torch.set_num_threads(4)
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="f", device="cpu")
    chunks = [audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio)
              for _, _, audio in pipe(text, voice=KOKORO_VOICE, speed=1.0)]
    sf.write(str(wav_path), np.concatenate(chunks), 24000)


def finalize(wav_path, mp3_path):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path), "-af",
                    "adelay=1000:all=1,acompressor=threshold=0.05:ratio=4:attack=5:release=120:makeup=2,"
                    "loudnorm=I=-11:TP=-1:LRA=7,alimiter=limit=0.89",
                    "-ar", "44100", "-b:a", "192k", str(mp3_path)], check=True)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3_path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout)


def register(spoken, display, duration, n, model=MODEL):
    data = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {"playlist": LABEL, "model": MODEL, "generations": []}
    data["generations"].append({
        "test_case_id": str(n), "name": f"Annonce {n:02d}", "prompt": display, "spoken": spoken, "type": "voice",
        "duration": round(duration, 1), "output_file": f"jingles/{FOLDER}/outputs/{n:02d}_annonce.wav", "status": "generated",
        "generated_at": datetime.datetime.now().astimezone().isoformat(), "model": model})
    tmp = RESULTS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, RESULTS)
    cfg = OUT.parent / "config.json"
    if not cfg.exists():
        cfg.write_text(json.dumps({"playlist_name": LABEL, "engine": "chatterbox", "output_dir": f"./jingles/{FOLDER}/outputs"},
                                  indent=2, ensure_ascii=False), encoding="utf-8")
    reg_path = WEB / "playlists.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    if not any(p["id"] == PID for p in reg):
        reg.append({"id": PID, "label": LABEL, "results": f"jingles/{FOLDER}/outputs/playlist_results.json", "role": "jingle",
                    "category": FOLDER, "description": "Annonces parlées des nouveautés de la radio, diffusées à la demande, hors rotation."})
        tmp = reg_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, reg_path)


def main():
    p = argparse.ArgumentParser(description="Génère une annonce parlée et la programme juste après le morceau en cours.")
    p.add_argument("texte", help="Texte prononcé (graphie phonétique possible)")
    p.add_argument("--affiche", default=None, help="Texte affiché (par défaut, le texte prononcé)")
    p.add_argument("--sans-diffusion", action="store_true", help="Générer sans programmer la diffusion")
    p.add_argument("--moteur", choices=("chatterbox", "kokoro"), default="chatterbox",
                   help="chatterbox (voix CréaZik, plusieurs minutes) ou kokoro (rapide, voix ff_siwis)")
    p.add_argument("--json", action="store_true", help="Écrire le résultat en JSON sur la dernière ligne")
    a = p.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    existing = json.loads(RESULTS.read_text(encoding="utf-8"))["generations"] if RESULTS.exists() else []
    n = max([int(g["test_case_id"]) for g in existing] + [0]) + 1
    mp3 = OUT / f"{n:02d}_annonce.mp3"
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        wav = Path(tmpdir) / "voix.wav"
        (synthesize_kokoro if a.moteur == "kokoro" else synthesize)(a.texte, wav)
        duration = finalize(wav, mp3)
    (OUT / f"{n:02d}_annonce.wav.feat.json").write_text(json.dumps({"duration_s": duration}), encoding="utf-8")
    register(a.texte, a.affiche or a.texte, duration, n, KOKORO_MODEL if a.moteur == "kokoro" else MODEL)
    key = f"{PID}:{n}"
    elapsed = time.time() - t0
    print(f"annonce {key} : {duration:.1f} s, générée en {elapsed:.0f} s ({a.moteur})")
    if not a.sans_diffusion:
        REQUESTS.mkdir(exist_ok=True)
        req = REQUESTS / f"{int(time.time() * 1000)}.json"
        req.write_text(json.dumps({"key": key}), encoding="utf-8")
        print(f"diffusion demandée : {req.name}")
    if a.json:
        print(json.dumps({"key": key, "duration_s": round(duration, 2), "elapsed_s": round(elapsed, 1),
                          "engine": a.moteur, "broadcast": not a.sans_diffusion}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
