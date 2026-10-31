import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8189"
HERE = Path(__file__).resolve().parent.parent
NEGATIVE = "texte, lettres, mots, titre, écriture, typographie, chiffres, légende, filigrane, logo, signature, cadre, flou, deformation, visages deformes"


def build_prompt(title, style):
    return (
        f"Belle illustration artistique pour une pochette de morceau de musique, image carrée, composition soignée, "
        f"détails riches, lumière travaillée. Thème inspiré par « {title} ». Ambiance musicale : {style}. "
        f"Image uniquement visuelle : aucun texte, aucune lettre, aucun mot, aucun chiffre."
    )


MODEL = "qwen-image-2.1-Q4_K_M.gguf"


def _post(path, body):
    req = urllib.request.Request(URL + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10).read()


def queue_ids():
    q = json.load(urllib.request.urlopen(URL + "/queue", timeout=10))
    running = {item[1] for item in q.get("queue_running", []) if len(item) > 1}
    pending = {item[1] for item in q.get("queue_pending", []) if len(item) > 1}
    return running, pending


def cancel(pid, wait_s=120):
    try:
        running, pending = queue_ids()
        if pid in pending:
            _post("/queue", {"delete": [pid]})
        if pid in running:
            _post("/interrupt", {"prompt_id": pid})
        t0 = time.time()
        while time.time() - t0 < wait_s:
            running, pending = queue_ids()
            if pid not in running and pid not in pending:
                return True
            time.sleep(1)
    except (OSError, ValueError):
        pass
    return False


def generate(prompt, out, seed=7, size=768, negative=NEGATIVE, prefix="creazik_cover_gen", timeout=900):
    wf = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": MODEL}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_bf16.safetensors", "type": "qwen_image", "device": "cpu"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": size, "height": size, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
                                                    "seed": seed, "steps": 20, "cfg": 4.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }
    req = urllib.request.Request(URL + "/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]
    t0 = time.time()
    while True:
        h = json.load(urllib.request.urlopen(URL + "/history/" + pid, timeout=30))
        if pid in h:
            break
        time.sleep(2)
        if time.time() - t0 > timeout:
            cancel(pid)
            raise TimeoutError(pid)
    entry = h[pid]
    for node in entry.get("outputs", {}).values():
        for im in node.get("images", []):
            data = urllib.request.urlopen(URL + "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"]), timeout=60).read()
            Path(out).write_bytes(data)
            return out
    raise RuntimeError(json.dumps(entry["status"])[:500])


def main():
    title, style, seed, out = sys.argv[1:5]
    prompt = build_prompt(title, style)
    print(prompt)
    generate(prompt, out, int(seed))
    print("image", out)


if __name__ == "__main__":
    main()
