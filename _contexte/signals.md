# Signals — CreaZik_V3   (MAJ 2026-10-06)

## Actions ouvertes
- [P1|ouvert] Valider la pochette de test (Qwen-Image via ComfyUI-Qwen) puis lancer le lot de pochettes quand la file de génération musicale est vide
  - fait quand: l'utilisateur valide le style de `creazik_cover_00001_.png` et le lot est lancé ou planifié
  - réf: webradio/tools/cover_test.py, D:\ServOMorph\ComfyUI-Qwen\output\creazik_cover_00001_.png, roadmap_webradio.md phase 7
- [P1|ouvert] Corriger le bug admin : un clic sur un morceau le joue tout de suite au lieu de le programmer après le morceau en cours
  - fait quand: en mode admin, un clic sur un morceau l'ajoute juste après le morceau courant sans le couper (test automatique + essai manuel)
  - réf: PLAN_WEBRADIO.md ligne 1.x, webradio/listen.js (actions front / play_index / now), webradio/radio_engine.py
- [P2|ouvert] Exécuter les contrôles manuels sur iPhone (fondus, lecture automatique, écran verrouillé, arc visuel, bandeau Traveling Sound, fins de morceaux)
  - fait quand: la section correspondante de tests_manuels.md est vide
  - réf: tests_manuels.md
- [P2|ouvert] Faire valider les textes des jingles parlés et changer le mot de passe admin par défaut
  - fait quand: textes validés dans webradio/voice_jingles.json et mot de passe admin changé
  - réf: webradio/voice_jingles.json, webradio/REGLES_GENERATION_DEV.md section 6
- [P3|ouvert] Poursuivre la génération en rotation (série en cours) et compléter les playlists éclectiques
  - fait quand: toutes les pistes de series.txt sont générées (ou abandonnées et listées)
  - réf: webradio/run_rotation.py, webradio/series.txt, PLAN_WEBRADIO.md 4.1 et 4.8
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: PLAN_WEBRADIO.md section 4.5

## Contexte chaud
- ComfyUI-Qwen tourne sur le port 8189 (lancé pour le test de pochette, peut être arrêté si la VRAM est nécessaire à la génération).
- Services : `.\services.ps1 restart -Only serveur|analyse|compression|generation` ; toujours relancer après un arrêt.
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`.

## Dernière session (2026-10-06)
# Session du 2026-10-06

## Décisions prises
- Dynamique de la journée : réglages et courbe dans la page de gestion, documentation en 5.4 de l'architecture.
- Visuels : arc narratif propre à chaque morceau (graine = clé du morceau).
- MP3 seul : tous les WAV supprimés (sauf silence.wav), le WAV est supprimé après conversion à chaque génération.
- Pochettes : IA locale ComfyUI-Qwen (Qwen-Image 2.1 GGUF), un test réalisé.
- Mode auditeur : bandeau et lien Traveling Sound Web Radio.
- Règles de génération et de développement consignées dans webradio/REGLES_GENERATION_DEV.md, lu par /start et mis à jour par /close.

## Livrables produits ou modifiés
- webradio/scenes.js, listen.js, listen.html, listen.css, traveling-sound.png : arc visuel et bandeau.
- webradio/radio_engine.py, compress_audio.py, ui.html, server.py, tests : MP3 seul, 18 tests passent.
- webradio/radio.html, ARCHITECTURE_WEBRADIO.md : dynamique de la journée.
- webradio/REGLES_GENERATION_DEV.md, .claude/commands/start.md, close.md : règles et branchements.

## Hypothèses validées / invalidées
- VALIDE : 868 WAV avaient un MP3 cohérent (durée, analyse) avant suppression.
- EN ATTENTE : rendu des pochettes à grande échelle (21 min pour une image, chargement des modèles inclus) ; comportements iPhone.

## Prochaine étape exacte
Faire valider le style de la pochette, puis corriger le bug du clic admin (programmer après le morceau en cours).

## Question bloquante pour la session suivante
La pochette de test convient-elle (style, couleurs, absence de texte) ?
