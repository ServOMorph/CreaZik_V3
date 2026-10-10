# HeartMuLa OSS 3B

Rôle : génération de chansons à partir de paroles et de tags. Le dépôt recommande `HeartMuLa-oss-3B-happy-new-year` avec `HeartCodec-oss-20260123`. La licence annoncée du dépôt et des poids est Apache 2.0.

## Entrées et sorties

- `--lyrics` : fichier texte avec paroles et sections. Le format conseillé montre `[Intro]`, `[Verse]`, `[Prechorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`; chaque section précède les lignes correspondantes.
- `--tags` : fichier texte avec des tags séparés par des virgules, sans espaces après les virgules (exemple officiel : `piano,happy,wedding,synthesizer,romantic`). Décrire genre, instruments, humeur et langue.
- `--save_path` : fichier audio de sortie, MP3 par défaut dans l’exemple du dépôt.
- `--max_audio_length_ms` : limite de longueur; la valeur par défaut documentée est 240 000 ms.
- `--mula_device` et `--codec_device` : appareils de calcul distincts. Le dépôt recommande `--lazy_load true` sur une seule carte pour réduire la mémoire utilisée.

Le dépôt présente le modèle comme multilingue (« presque toutes les langues »), mais ne donne pas dans son guide une garantie de qualité spécifique au français. Les dix essais français de la campagne serviront précisément à mesurer cette limite.

## Installation et exécution officielle

Le dépôt recommande Python 3.10. Après installation locale de `heartlib` et téléchargement des dépôts de poids, l’arborescence doit réunir les fichiers racine de `HeartMuLaGen`, le dossier `HeartMuLa-oss-3B` et `HeartCodec-oss` dans le répertoire du modèle.

```powershell
python .\examples\run_music_generation.py `
  --model_path D:\AI\Musique\heartmula\ckpt `
  --version 3B `
  --lyrics D:\AI\Musique\heartmula\tests\lyrics.txt `
  --tags D:\AI\Musique\heartmula\tests\tags.txt `
  --save_path D:\AI\Musique\heartmula\tests\heartmula-test.mp3 `
  --max_audio_length_ms 30000 `
  --lazy_load true
```

Exécuter sur `cpu` lorsque le GPU est occupé ou qu’il n’y a pas assez de VRAM : `--mula_device cpu --codec_device cpu --mula_dtype fp32 --codec_dtype fp32`. Le dépôt montre explicitement les options CUDA mais ne publie pas de mesure de performance CPU; une génération CPU peut donc être lente. Utiliser les mêmes contrôles de prompt et de longueur sur tout le lot.

## Construire les tags et les paroles

Les tags sont des mots-clés séparés par des virgules, pas un paragraphe complet. Les paroles portent la structure temporelle et le texte à chanter. Pour un morceau en français, écrire les paroles en français et tester `french` comme tag de langue; le dépôt ne publie pas de taxonomie complète des tags ni de garantie spécifique au français. Limiter les lignes et fournir un refrain répété pour donner un repère mélodique.

**Exemple de tags**

```text
french,melodic rap,male vocal,analog synth bass,crisp electronic drums,autotune,bittersweet,modern studio production
```

**Exemple de paroles**

```text
[Intro]

[Verse]
La nuit s’étire au bout des rues
J’avance avec mes rêves perdus
Un feu s’allume dans le brouillard
Je sens le jour venir plus tard

[Chorus]
On garde le cap, on garde la flamme
Même si le vent secoue nos âmes
La ville résonne et nous répond
On fait du bruit, on tient bon

[Outro]
```

Le prompt est une direction, pas une garantie de prononciation, de timbre ou d’autotune. Écouter chaque résultat et noter les artefacts vocaux.

## Environnement et sources

- Dépôt cloné pour les essais : `D:\AI\Musique\heartlib`.
- [Dépôt officiel, déploiement local, paramètres et licence](https://github.com/HeartMuLa/heartlib)
- [Poids 3B recommandés](https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year)
- [Poids HeartCodec recommandés](https://huggingface.co/HeartMuLa/HeartCodec-oss-20260123)
