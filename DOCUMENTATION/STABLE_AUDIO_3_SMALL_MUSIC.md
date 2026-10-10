# Stable Audio 3 Small-Music

Modèle 433M prévu pour la génération musicale légère sur CPU, jusqu’à 120 s. Sur Windows, le dépôt Stability AI fournit le backend TFLite/LiteRT avec XNNPACK. L’installation locale de la zone a été relevée le 8 octobre 2026 : `D:\AI\Musique\stable-audio-3\optimized\tflite`, environnement `.venv` Python 3.11 et poids sous `models\tflite\`. La campagne doit relire l’état du dépôt et des poids avant usage.

## Capacités et limites

- `small-music` est conçu pour les morceaux instrumentaux et l’ambiance. La documentation indique que les modèles ne produisent pas de voix intelligibles; des textures vocales non intelligibles peuvent apparaître.
- Le modèle accepte une description textuelle; l’interface TFLite permet de régler la durée, les étapes, la seed, les threads et le chemin de sortie WAV.
- Durée réaliste : choisir une durée adaptée au brief. Pour les dix comparaisons, utiliser des extraits de 30 s afin de rester dans la limite MusicGen Small.
- Les modèles TFLite utilisent le CPU. Il n’y a donc pas de concurrence GPU directe avec ACE-Step ou ComfyUI, mais XNNPACK peut charger fortement le CPU.

## Écrire un prompt

La documentation officielle recommande de décrire genre, instruments, humeur/énergie et BPM. Pour ce modèle, ajouter le rôle des instruments, le groove et l’évolution sur la durée. Les tags AudioSparx officiels `TrackType: Music`, `VocalType: Instrumental`, `Genre:` et `Instruments:` peuvent renforcer la sémantique.

```text
TrackType: Music, VocalType: Instrumental, Genre: French electro-pop, Instruments: analog synth bass, crisp electronic drums, bright arpeggiated synthesizers. 116 BPM, bittersweet but hopeful, intimate opening that gradually builds into a wide melodic chorus, polished modern studio mix, no speech, no vocals.
```

Éviter les demandes de paroles, d’autotune ou de voix masculine : les résultats peuvent contenir des artefacts vocaux, mais pas un chant intelligible contrôlé.

## Commande TFLite installée

Depuis `D:\AI\Musique\stable-audio-3\optimized\tflite` :

```powershell
.\.venv\Scripts\python.exe .\scripts\sa3_tflite.py `
  --prompt "TrackType: Music, VocalType: Instrumental, Genre: French electro-pop, Instruments: analog synth bass, crisp electronic drums, bright arpeggiated synthesizers. 116 BPM, bittersweet but hopeful, intimate opening that builds into a wide melodic chorus, polished studio mix, no speech, no vocals." `
  --dit sm-music --decoder same-s --seconds 30 --seed 11601 `
  --threads 8 --out D:\ServOMorph\CreaZik_V3\MODELES_LLM\sorties\stable_audio_01.wav
```

La CLI écrit un WAV PCM stéréo 44,1 kHz. Pour l’UI de tests du projet, convertir le WAV en MP3 192 kbit/s, enregistrer le prompt et la seed dans le manifeste de résultats, puis supprimer le WAV après conversion/analyse, conformément aux règles de la webradio.

## Sources

- [README officiel Stable Audio 3](https://github.com/Stability-AI/stable-audio-3)
- [Guide officiel de prompting](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
- [Guide d’inférence TFLite Windows/macOS/Linux](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/tflite/README.md)
- [Guide d’inférence général](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)
