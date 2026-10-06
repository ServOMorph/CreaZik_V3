import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:8189"
prompt_text = sys.argv[1]
out = sys.argv[2]

wf = {
    "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "qwen-image-2.1-Q4_K_M.gguf"}},
    "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_bf16.safetensors", "type": "qwen_image", "device": "cpu"}},
    "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
    "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["2", 0]}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "texte, lettres, logo, filigrane, flou, deformation", "clip": ["2", 0]}},
    "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
    "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
                                                "seed": 7, "steps": 20, "cfg": 4.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "creazik_cover"}},
}

req = urllib.request.Request(URL + "/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
try:
    pid = json.load(urllib.request.urlopen(req))["prompt_id"]
except urllib.error.HTTPError as e:
    print(e.read().decode()[:2000])
    raise
print("prompt", pid, flush=True)
t0 = time.time()
while True:
    h = json.load(urllib.request.urlopen(URL + "/history/" + pid))
    if pid in h:
        break
    time.sleep(3)
    if time.time() - t0 > 1500:
        print("timeout")
        sys.exit(1)
entry = h[pid]
print("statut", entry["status"].get("status_str"), round(time.time() - t0), "s")
for node in entry.get("outputs", {}).values():
    for im in node.get("images", []):
        data = urllib.request.urlopen(URL + "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"])).read()
        open(out, "wb").write(data)
        print("image", out)
if entry["status"].get("status_str") != "success":
    print(json.dumps(entry["status"])[:1500])
