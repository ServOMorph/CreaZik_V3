# MusicGen Small

Modèle `facebook/musicgen-small` (300M), text-to-music. AudioCraft documente aussi l’utilisation via Transformers; son exemple officiel pour Small ne requiert que `transformers` et les poids Hugging Face. Cette voie est utile pour l’environnement Windows du projet si l’installation AudioCraft complète n’est pas compatible.

## Capacités et limites

- Génère de la musique à partir d’une description textuelle; Small ne prend pas une mélodie en entrée (contrairement aux variantes Melody).
- L’implémentation AudioCraft fixe une durée maximale de 30 s pour MusicGen; la documentation montre aussi un réglage de durée dans l’API.
- Meta indique que la génération locale AudioCraft nécessite un GPU et recommande 16 Go, tout en précisant que des GPU moins dotés peuvent générer des séquences plus courtes avec Small. La RTX 4060 du projet a 8 Go; le temps et l’occupation GPU sont donc à mesurer.
- Les poids AudioCraft sont publiés sous CC-BY-NC 4.0. Ne pas les traiter comme librement réutilisables commercialement.
- L’API officielle Small est text-to-music, pas un contrôle dédié de paroles ou de langue. Ne pas utiliser ce modèle comme test de chant français.

## Prompt recommandé

Composer une description en une ou deux phrases : genre + tempo + instruments principaux + groove + évolution + ambiance + production. Décrire les sons souhaités au lieu de demander des paroles ou une voix. Garder un seul tempo et des consignes cohérentes.

```text
Melodic French electro-pop instrumental, 116 BPM, warm analog synth bass, steady electronic drums, bright arpeggiated synth hook, intimate opening that builds into a wide uplifting chorus, polished modern studio production, bittersweet mood, no vocals.
```

Pour les tests vocaux, utiliser le même brief d’arrangement, mais noter le résultat comme instrumental de comparaison; l’absence de contrôle lyric-to-song est une différence de capacité, pas une erreur d’exécution.

## Utilisation Transformers (exemple officiel adapté)

```python
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

model_id = "facebook/musicgen-small"
processor = AutoProcessor.from_pretrained(model_id)
model = MusicgenForConditionalGeneration.from_pretrained(model_id).to("cpu").eval()

prompt = "Melodic French electro-pop instrumental, 116 BPM, warm analog synth bass, steady electronic drums, bright synth hook, polished studio production, no vocals."
inputs = processor(text=[prompt], padding=True, return_tensors="pt")
with torch.inference_mode():
    audio = model.generate(**inputs, max_new_tokens=1500)
sample_rate = model.config.audio_encoder.sampling_rate
sf.write("musicgen-small.wav", audio[0, 0].cpu().numpy(), sample_rate)
```

Le nombre de tokens détermine la longueur effective avec cette API; l’exemple officiel montre 256 tokens. `1500` est une cible de réglage pour approcher le plafond de 30 s, à mesurer sur le fichier obtenu. Pour les essais, mesurer la durée réelle plutôt que supposer qu’un même nombre de tokens produit exactement 30 s. Convertir ensuite le WAV avec FFmpeg pour l’écoute dans l’UI.

## Installation, compatibilité et sources

La recommandation antérieure visait AudioCraft natif, mais son README officiel indique Python 3.9 et PyTorch 2.1.0; une installation récente peut échouer sous Windows ou Python plus récent. La voie Transformers est donc à valider séparément et doit être consignée dans le compte rendu. Le guide AudioCraft dit qu’un GPU est requis pour l’usage local; lancer l’API Transformers sur CPU constitue ici un repli pratique, non la configuration recommandée par Meta, et peut être très lent.

- [Documentation officielle MusicGen](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)
- [Dépôt officiel AudioCraft et prérequis](https://github.com/facebookresearch/audiocraft)
- [Fiche du modèle MusicGen Small](https://huggingface.co/facebook/musicgen-small)
