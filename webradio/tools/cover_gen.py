import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8189"
HERE = Path(__file__).resolve().parent.parent
NEGATIVE = "faute d'orthographe, lettres deformees, texte illisible, texte répété, mots coupés, lignes de texte mélangées, texte manquant, filigrane, logo, flou, deformation"


def build_prompt(charte, title, playlist_label, date):
    return (
        f"Pochette d'album carrée. Sujet : {charte['sujet']}. Technique : {charte['technique']}. "
        f"Palette : {charte['palette']}. "
        f"En bas à gauche, trois lignes de texte alignées à gauche, police {charte['typographie']}, "
        f"nettes, lisibles, sur un fond calme. Le texte est écrit exactement une seule fois, dans cet ordre, "
        f"chaque ligne complète sur une seule ligne :\n"
        f"Ligne 1 (très grande, en gras, occupant presque toute la largeur) : « {title} »\n"
        f"Ligne 2 (grande, en majuscules espacées) : « {playlist_label} »\n"
        f"Ligne 3 (très petite) : « {date} »\n"
        f"Aucun numéro ni chiffre devant le titre ; aucun autre texte que ces trois lignes."
    )


def generate(prompt, out, seed=7):
    wf = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "qwen-image-2.1-Q4_K_M.gguf"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_bf16.safetensors", "type": "qwen_image", "device": "cpu"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
                                                    "seed": seed, "steps": 20, "cfg": 4.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "creazik_cover_gen"}},
    }
    req = urllib.request.Request(URL + "/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req))["prompt_id"]
    t0 = time.time()
    while True:
        h = json.load(urllib.request.urlopen(URL + "/history/" + pid))
        if pid in h:
            break
        time.sleep(2)
        if time.time() - t0 > 900:
            raise TimeoutError(pid)
    entry = h[pid]
    for node in entry.get("outputs", {}).values():
        for im in node.get("images", []):
            data = urllib.request.urlopen(URL + "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"])).read()
            Path(out).write_bytes(data)
            return out
    raise RuntimeError(json.dumps(entry["status"])[:500])


def main():
    playlist_id, title, date, out = sys.argv[1:5]
    charte = json.load(open(HERE / "covers_charte.json", encoding="utf-8"))[playlist_id]
    label = next(p["label"] for p in json.load(open(HERE / "playlists.json", encoding="utf-8")) if p["id"] == playlist_id)
    label = label.removeprefix("Playlist ")
    prompt = build_prompt(charte, title, label, date)
    print(prompt)
    generate(prompt, out)
    print("image", out)


if __name__ == "__main__":
    main()
