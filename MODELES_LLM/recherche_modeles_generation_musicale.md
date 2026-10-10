# Recherche de modèles de génération musicale

Date : 2026-10-08
Configuration de référence : RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X, Windows. Sources contrôlées : dépôts officiels GitHub.

## Candidats

| Modèle | Usage et compatibilité | Décision |
|---|---|---|
| [HeartMuLa 3B](https://github.com/HeartMuLa/heartlib) | Génération de chansons à partir de paroles et tags. Le dépôt conseille le chargement différé sur GPU unique en cas de manque de mémoire, sans publier de mesure RTX 4060 8 Go. | À essayer avec prudence. La génération de paroles chantées en français et le besoin mémoire restent à mesurer. |
| [Stable Audio 3 Small-Music](https://github.com/Stability-AI/stable-audio-3) | Musique instrumentale, durée maximale 120 s, modèle 433M. Runtime CPU TFLite disponible pour Windows. | Candidat léger à tester ; pas adapté à la génération de voix. |
| [Stable Audio 3 Medium](https://github.com/Stability-AI/stable-audio-3) | Modèle 1,4B et durée maximale 380 s. Pic VRAM publié : 6,52 Go sur H200 ; backend CUDA/TensorRT. | Limite sur 8 Go, mesure publiée non représentative de la RTX 4060. La voie TensorRT du dépôt vise Linux. |
| [MusicGen Small](https://github.com/facebookresearch/audiocraft) | Modèle 300M, génération texte-vers-musique. Meta indique qu'une carte plus petite que 16 Go peut générer des séquences courtes avec le modèle Small. La carte de modèle signale que les voix réalistes ne sont pas son usage. | Baseline instrumentale pour comparer des prompts simples. |

## À écarter sur cette machine

- [YuE2](https://github.com/multimodal-art-projection/YuE) : prérequis officiel ciblant Linux et GPU NVIDIA 24 Go avec BF16.

## Référence du projet

ACE-Step 1.5 est déjà le modèle de référence du pipeline local. Son dépôt annonce moins de 4 Go de VRAM et une prise en charge de plus de 50 langues. Le worker de test existant appelle le DiT avec offload CPU et peut activer le LM 0,6B.

## Sources complémentaires

- [Stable Audio 3 — modèles, matériel, limites et installation](https://github.com/Stability-AI/stable-audio-3/blob/main/README.md) : Small-Music vise la musique, pas la voix ou la parole ; le runtime TFLite couvre Windows sur CPU.
- [Stable Audio 3 — TFLite](https://github.com/Stability-AI/stable-audio-3/tree/main/optimized/tflite)
- [YuE — prérequis YuE2](https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/models-and-setup.md)
- [AudioCraft — MusicGen](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)
- [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5)

Les valeurs de VRAM sont celles déclarées par les projets, pas des mesures effectuées sur la machine de référence.

## Installation et génération — 2026-10-08

- Dépôt installé dans `D:\AI\Musique\stable-audio-3` ; environnement Python 3.11 dans `optimized\tflite\.venv`.
- Runtime Windows LiteRT/TFLite CPU installé ; poids `sm-music` et encodeur T5Gemma présents sous `optimized\tflite\models\tflite\`.
- La récupération via Hugging Face Xet est restée bloquée ; téléchargement HTTP direct des fichiers publics du même dépôt utilisé à la place.
- Génération réalisée : 90 s, prompt rap mélodique français avec voix masculine et autotune, seed `1250643744`, durée de calcul `50,24 s` sur CPU.
- Fichier produit : `sorties/stable_audio_3_rap_melodique_fr_90s.wav`.
- Le moteur a terminé sans erreur. Le modèle Small-Music n'étant pas prévu pour générer la voix, présence de paroles chantées et effet d'autotune non confirmés à l'écoute ; le WAV reste à évaluer subjectivement.
