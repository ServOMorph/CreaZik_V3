import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "MODELES_LLM"
MASTER = ZONE / "sorties" / "campagne_2026-10-09"
CONFIG_PATH = ZONE / "configs" / "campagne_40.json"
REGISTRY = ZONE / "registre_campagne.py"
HEART_ENV = Path(r"D:\AI\Musique\heartlib\.venv\Scripts\python.exe")
HEART_ROOT = Path(r"D:\AI\Musique\heartmula\ckpt")
MUSICGEN_ROOT = Path(r"D:\AI\Musique\musicgen-small")
SA3_ROOT = Path(r"D:\AI\Musique\stable-audio-3\optimized\tflite")
SA3_PYTHON = SA3_ROOT / ".venv" / "Scripts" / "python.exe"
ACE_ROOT = Path(r"D:\ServOMorph\ACE-Step-1.5")
FFMPEG = Path(r"C:\Users\raph6\Documents\ServOMorph\ffmpeg\bin\ffmpeg.exe")


def registry(*args):
    subprocess.run([sys.executable, str(REGISTRY), *map(str, args)], check=True)


def model_runtime(model, python_exe=None, device="cpu"):
    packages = {"heartmula": ["torch", "transformers", "heartlib", "torchaudio", "tokenizers", "soundfile"],
                "musicgen": ["torch", "transformers", "soundfile"],
                "stable_audio": ["ai-edge-litert", "numpy"],
                "ace": ["torch", "torchaudio", "transformers", "acestep"]}[model]
    code = ("import importlib.metadata as m,json,platform,sys; names=" + repr(packages) + "; "
            "versions={}; "
            "[(versions.__setitem__(n,m.version(n))) for n in names if any(d.metadata['Name'].lower()==n.lower() for d in m.distributions())]; "
            "print(json.dumps({'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'versions':versions}))")
    command = [str(python_exe or sys.executable), "-c", code]
    proc = subprocess.run(command, capture_output=True, text=True, check=True)
    info = json.loads(proc.stdout)
    return {"os": platform.platform(), "python": info["python"], "device": device,
            "versions": {"python": info["python"].split()[0], **info["versions"]},
            "model_storage": str({"heartmula": HEART_ROOT, "musicgen": MUSICGEN_ROOT, "stable_audio": SA3_ROOT, "ace": ACE_ROOT}[model])}


def full_metadata(model, case, prompt, lyrics=None, tags=None, seed=None, config=None, runtime=None):
    def revision_of(path):
        try:
            return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            ref = path / ".cache" / "huggingface" / "refs" / "main"
            return ref.read_text(encoding="utf-8").strip() if ref.is_file() else "non disponible"

    revision_paths = {"heartmula": HEART_ROOT / "HeartMuLa-oss-3B", "musicgen": MUSICGEN_ROOT,
                      "stable_audio": SA3_ROOT, "ace": ACE_ROOT}
    revision = revision_of(revision_paths[model])
    component_revisions = {"primary_weights": revision}
    if model == "heartmula":
        component_revisions["codec_weights"] = revision_of(HEART_ROOT / "HeartCodec-oss")
        component_revisions["heartlib_repository"] = revision_of(HEART_ROOT.parent / "heartlib")
    return {"model_version": {"heartmula": "HeartMuLa-oss-3B-happy-new-year + HeartCodec-oss-20260123",
                               "musicgen": "facebook/musicgen-small (300M)",
                               "stable_audio": "stabilityai/stable-audio-3-optimized / sm-music",
                               "ace": "ACE-Step 1.5 / acestep-v15-turbo"}[model],
            "model_revision": revision,
            "component_revisions": component_revisions,
            "prompt": prompt, "lyrics": lyrics, "tags": tags,
            "generation_config": config or {}, "runtime": runtime or model_runtime(model),
            "test_case_id": case["id"], "title": case["title"], "seed": seed}


def save_metadata(model, case, data):
    folder = MASTER / "attempts"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{model}_{case['id']}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry("begin", model, case["id"], path)
    return path


def finish(model, case, raw, metadata):
    registry("finalize", model, case["id"], raw, metadata)


def fail(model, case, metadata, error):
    attempt = json.loads(metadata.read_text(encoding="utf-8"))
    attempt["generation_error"] = str(error)[-4000:]
    metadata.write_text(json.dumps(attempt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = MASTER / "generation_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for track in manifest["tracks"]:
        if track["model_key"] == model and track["test_case_id"] == case["id"]:
            track.update({"status": "failed", "error": str(error)[-4000:], "attempt": attempt})
            break
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_stable(cases):
    for case in cases:
        seed = 2026100900 + int(case["id"])
        prompt = case["stable_audio"]
        raw = MASTER / f"SA3_{case['id']}_{case['slug']}.raw.wav"
        config = {"dit": "sm-music", "decoder": "same-s", "seconds": 30.0,
                  "steps": 8, "seed": seed, "threads": 8, "out": str(raw),
                  "dit_precision": "fp32", "decoder_precision": "w8a8", "encoder_precision": "w8a8",
                  "cfg": 1.0, "apg": 1.0, "cfg_batched": True, "free_models": True,
                  "play": False, "negative_prompt": None, "init_audio": None}
        metadata = save_metadata("stable_audio", case, full_metadata(
            "stable_audio", case, prompt, tags=None, seed=seed, config=config,
            runtime=model_runtime("stable_audio", SA3_PYTHON, "CPU XNNPACK 8 threads")))
        command = [str(SA3_PYTHON), str(SA3_ROOT / "scripts" / "sa3_tflite.py"),
                   "--prompt", prompt, "--dit", "sm-music", "--decoder", "same-s",
                   "--seconds", "30", "--steps", "8", "--seed", str(seed),
                   "--threads", "8", "--out", str(raw)]
        try:
            subprocess.run(command, cwd=SA3_ROOT, check=True)
            finish("stable_audio", case, raw, metadata)
        except Exception as exc:
            fail("stable_audio", case, metadata, exc)


def run_musicgen(cases):
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import numpy as np
    import soundfile as sf
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    torch.set_num_threads(8)
    processor = AutoProcessor.from_pretrained(str(MUSICGEN_ROOT), local_files_only=True)
    model = MusicgenForConditionalGeneration.from_pretrained(str(MUSICGEN_ROOT), local_files_only=True).to("cpu").eval()
    for case in cases:
        seed = 2026100900 + int(case["id"])
        prompt = case["musicgen"]
        raw = MASTER / f"MG_{case['id']}_{case['slug']}.raw.wav"
        config = model.generation_config.to_dict()
        config.update({"max_new_tokens": 1500, "do_sample": True, "seed": seed,
                       "torch_num_threads": 8, "device": "cpu"})
        metadata = save_metadata("musicgen", case, full_metadata(
            "musicgen", case, prompt, seed=seed, config=config,
            runtime=model_runtime("musicgen", HEART_ENV, "CPU")))
        try:
            torch.manual_seed(seed)
            inputs = processor(text=[prompt], padding=True, return_tensors="pt")
            started = time.monotonic()
            with torch.inference_mode():
                audio = model.generate(**inputs, max_new_tokens=1500, do_sample=True)
            sample_rate = model.config.audio_encoder.sampling_rate
            sf.write(str(raw), audio[0, 0].cpu().numpy().astype(np.float32), sample_rate)
            attempt = json.loads(metadata.read_text(encoding="utf-8"))
            attempt["generation_config"]["elapsed_seconds"] = round(time.monotonic() - started, 2)
            attempt["generation_config"]["sample_rate_native"] = sample_rate
            metadata.write_text(json.dumps(attempt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            finish("musicgen", case, raw, metadata)
        except Exception as exc:
            fail("musicgen", case, metadata, exc)


def run_heartmula(cases):
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import soundfile as sf
    import torch
    import torchaudio
    from heartlib import HeartMuLaGenPipeline

    torch.set_num_threads(8)
    HeartMuLaGenPipeline._apply_compile = lambda self, model: None

    def save_heart_wav(uri, src, sample_rate, channels_first=True, **kwargs):
        audio = src.detach().to(torch.float32).cpu().numpy()
        if channels_first and audio.ndim > 1:
            audio = audio.transpose(1, 0)
        sf.write(str(uri), audio, int(sample_rate), format="WAV", subtype="PCM_16")

    torchaudio.save = save_heart_wav
    pipeline = HeartMuLaGenPipeline.from_pretrained(
        str(HEART_ROOT), version="3B", device={"mula": torch.device("cpu"), "codec": torch.device("cpu")},
        dtype={"mula": torch.bfloat16, "codec": torch.float32}, lazy_load=True)
    for case in cases:
        seed = 2026100900 + int(case["id"])
        tags = case["heartmula"]["tags"]
        lyrics = case["heartmula"]["lyrics"]
        raw = MASTER / f"HM3_{case['id']}_{case['slug']}.raw.wav"
        config = {"max_audio_length_ms": 30000, "topk": 50, "temperature": 1.0,
                  "cfg_scale": 1.5, "mula_device": "cpu", "codec_device": "cpu",
                  "mula_dtype": "bfloat16", "codec_dtype": "float32", "lazy_load": True,
                  "audio_writer": "soundfile 0.14.0, WAV PCM_16",
                  "seed": seed, "seed_method": "torch.manual_seed", "torch_compile": False,
                  "torch_num_threads": 8}
        metadata = save_metadata("heartmula", case, full_metadata(
            "heartmula", case, tags, lyrics=lyrics, tags=tags, seed=seed, config=config,
            runtime=model_runtime("heartmula", HEART_ENV, "CPU")))
        try:
            torch.manual_seed(seed)
            started = time.monotonic()
            pipeline({"lyrics": lyrics, "tags": tags}, max_audio_length_ms=30000,
                     save_path=str(raw), topk=50, temperature=1.0, cfg_scale=1.5)
            attempt = json.loads(metadata.read_text(encoding="utf-8"))
            attempt["generation_config"]["elapsed_seconds"] = round(time.monotonic() - started, 2)
            metadata.write_text(json.dumps(attempt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            finish("heartmula", case, raw, metadata)
        except Exception as exc:
            fail("heartmula", case, metadata, exc)


def run_ace(cases):
    ace_config_path = MASTER / "ace_campaign_config.json"
    ace_config = {"ace_step_path": str(ACE_ROOT), "output_dir": "../MODELES_LLM/sorties/campagne_2026-10-09/ace_raw",
                  "playlist_name": "Campagne comparative ACE-Step 1.5", "test_cases": []}
    jobs = {}
    for case in cases:
        seed = 2026100900 + int(case["id"])
        prompt = case["ace"]["caption"]
        lyrics = case["ace"]["lyrics"]
        ace_case = {"id": case["id"], "name": case["slug"], "prompt": prompt,
                    "type": "instrumental" if case["ace"]["instrumental"] else "vocal",
                    "duration": 30, "seed": seed, "lyrics": lyrics, "fit_lyrics": False,
                    "language": "fr", "bpm": case["bpm"]}
        ace_config["test_cases"].append(ace_case)
        details = full_metadata("ace", case, prompt, lyrics=lyrics, seed=seed,
                                config={"duration": 30, "seed": seed, "inference_steps": 8,
                                        "guidance_scale": 1.0, "task_type": "text2music",
                                        "instrumental": ace_case["type"] == "instrumental", "device": "CPU (CUDA_VISIBLE_DEVICES='')",
                                        "dit_checkpoint": "acestep-v15-turbo", "lm": False,
                                        "bpm": case["bpm"], "audio_format": "wav", "batch_size": 1},
                                runtime=model_runtime("ace", ACE_ROOT / ".venv" / "Scripts" / "python.exe", "CPU; CUDA désactivé pour préserver ComfyUI"))
        jobs[case["id"]] = (case, save_metadata("ace", case, details))
    ace_config_path.write_text(json.dumps(ace_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = MASTER / "ace_raw"
    results_path = out / "playlist_results.json"
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = ""
    command = [str(ACE_ROOT / ".venv" / "Scripts" / "python.exe"), str(ROOT / "webradio" / "generate.py"),
               str(ace_config_path), "--steps", "8"]
    log_path = MASTER / "ace_worker.log"
    consumed = set()
    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log_file, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        while proc.poll() is None:
            if results_path.is_file():
                results = json.loads(results_path.read_text(encoding="utf-8"))
                for entry in results.get("generations", []):
                    case_id = str(entry.get("test_case_id", "")).zfill(2)
                    if entry.get("status") != "generated" or case_id not in jobs or case_id in consumed:
                        continue
                    case, metadata = jobs[case_id]
                    raw = ROOT / "webradio" / Path(entry["output_file"])
                    if raw.is_file():
                        finish("ace", case, raw, metadata)
                        consumed.add(case_id)
            time.sleep(3)
    output = log_path.read_text(encoding="utf-8", errors="replace")
    if output:
        print(output[-5000:])
    if proc.returncode != 0:
        for case_id, (case, metadata) in jobs.items():
            if case_id not in consumed:
                fail("ace", case, metadata, f"ACE worker exit code {proc.returncode}")
    elif len(consumed) < len(jobs):
        for case_id, (case, metadata) in jobs.items():
            if case_id not in consumed:
                fail("ace", case, metadata, "Le worker ACE n'a pas produit de WAV pour ce cas")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", choices=["ace", "heartmula", "musicgen", "stable_audio"])
    parser.add_argument("--only", default="", help="IDs de cas séparés par des virgules")
    args = parser.parse_args()
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cases = data["cases"]
    if args.only:
        chosen = {v.zfill(2) for v in args.only.split(",")}
        cases = [c for c in cases if c["id"] in chosen]
    MASTER.mkdir(parents=True, exist_ok=True)
    if args.model == "ace":
        run_ace(cases)
    elif args.model == "heartmula":
        run_heartmula(cases)
    elif args.model == "musicgen":
        run_musicgen(cases)
    else:
        run_stable(cases)


if __name__ == "__main__":
    main()
