---
description: Génère un jingle parlé (annonce hors rotation ou entrée de rotation) avec Chatterbox
---

# /jingle annonce "<texte>" | /jingle rotation <categorie> "<texte>"

Génère un jingle parlé localement avec Chatterbox. Aucune diffusion n'est déclenchée.

## Règles

- Seulement pour un changement visible dans l'interface auditeur (`webradio/REGLES_GENERATION_DEV.md` section 3.11).
- Jamais de nom d'artiste dans le texte.
- Nom de la radio : prononcé « Créa Zique, I A, Ouèbe Radio », affiché « CréaZik IA WebRadio ».
- Ne jamais lancer sans le texte exact fourni par l'utilisateur ; ne rien inventer.

## `/jingle annonce "<texte>"`

Annonce ponctuelle, hors rotation.

1. Depuis `webradio/`, lancer en tâche de fond (environ 4 min) :
   ```powershell
   D:\ServOMorph\TTS_Local\chatterbox\.venv\Scripts\python.exe tools\annonce.py "<texte prononcé>" --affiche "<texte affiché>"
   ```
2. `--affiche` reprend le texte affiché validé avec l'utilisateur (nom « CréaZik IA WebRadio »).

## `/jingle rotation <categorie> "<texte>"`

Ajoute un jingle à une catégorie de rotation existante (`traveling-sound`, `serenia-tech`, `webradio`).

1. Depuis `webradio/`, lancer en tâche de fond (environ 4 min) :
   ```powershell
   D:\ServOMorph\TTS_Local\chatterbox\.venv\Scripts\python.exe tools\jingle_rotation.py <categorie> "<texte>" --affiche "<texte affiché>"
   ```
2. Le script refuse une catégorie absente ou `annonces`, numérote l'entrée, écrit le MP3 et met à jour `playlist_results.json`. Il ne diffuse rien.

## Après génération

1. Vérifier que le MP3 existe et lire sa durée (`ffprobe`).
2. Indiquer à l'utilisateur que le jingle est prêt et ce qu'il dit.
3. Ne rien ajouter aux playlists diffusées ni mettre en rotation sans demande explicite.
