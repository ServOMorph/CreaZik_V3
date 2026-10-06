# Signals — CreaZik_V3   (MAJ 2026-10-06)

## Actions ouvertes
- [P1|ouvert] Générer 3 images d'exemple de pochettes avec charte graphique par playlist, les faire valider, puis lancer le lot quand la file de génération musicale est vide
  - fait quand: l'utilisateur valide les 3 exemples (flamenco "Rumba du matin", hard-tech "Rave souterraine", medieval-renaissance "Danse médiévale") et le lot est lancé ou planifié
  - réf: webradio/covers_charte.json (87 playlists), webradio/tools/cover_gen.py, tools/make_charte.py ; avant : tuer run_rotation.py, generate.py, ace_worker.py, lancer ComfyUI-Qwen (lancer.bat, port 8189), puis relancer la génération
- [P1|ouvert] Corriger `services.ps1 stop -Only generation` : il n'arrête pas run_rotation.py (la rotation continue et plante ComfyUI par manque de VRAM)
  - fait quand: `services.ps1 stop -Only generation` arrête run_rotation.py, generate.py et ace_worker.py
  - réf: webradio/services.ps1, webradio/run_rotation.py
- [P2|ouvert] Réécouter les 20 jingles « Créa Zik IA WebRadio » (voix, prononciation « Ouèbe Radio ») et tester run.py à la racine
  - fait quand: prononciation validée par l'utilisateur, run.py lance le serveur et ouvre l'UI
  - réf: webradio/voice_jingles.json, run.py
- [P2|ouvert] Exécuter les contrôles manuels sur iPhone (clic ▶ / Lire sans couper, Programmation lisible, noms de playlists sans « Playlist », fondus, écran verrouillé, arc visuel, bandeau Traveling Sound)
  - fait quand: la section correspondante de tests_manuels.md est vide
  - réf: tests_manuels.md
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé
  - réf: webradio/REGLES_GENERATION_DEV.md section 6
- [P3|ouvert] Poursuivre la génération en rotation (89 playlists dont 11 « Esprit ») et retirer de « idée de playlist.md » chaque entrée une fois sa playlist complète (10 morceaux)
  - fait quand: toutes les pistes de series.txt sont générées et les 11 entrées retirées de la liste
  - réf: webradio/run_rotation.py, webradio/series.txt, idée de playlist.md (restent : Rap Français autotuné, Hight Light Tribe, non traités)
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: PLAN_WEBRADIO.md section 4.5

## Contexte chaud
- La rotation de génération tourne (run_rotation.py) ; ComfyUI-Qwen est arrêté (plantage VRAM).
- Services : `.\services.ps1 restart -Only serveur|analyse|compression|generation` ; toujours relancer après un arrêt.
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`.

## Dernière session (2026-10-06)
# Session du 2026-10-06

## Décisions prises
- Clic ▶ et « Lire » : mise en tête de file sans couper le morceau en cours (confirmé par l'utilisateur).
- Nom de la radio : « CréaZik IA WebRadio » dans toutes les UI et dans les jingles vocaux.
- Pochettes : texte (titre, playlist, date) généré dans l'image ; une charte graphique par playlist.
- Aperçu auditeur et mot « Playlist » retirés des affichages auditeur.

## Livrables produits ou modifiés
- webradio/listen.js, listen.css, listen.html, radio.html, ui.html, server.py : correctifs et renommage.
- webradio/radio_engine.py, tests : action playlist_front, 19 tests passent.
- webradio/playlists/ (11 « Esprit » et blues), playlists.json, scenes_spec.json, series.txt : playlists créées.
- webradio/voice_jingles.json : 20 jingles régénérés ; run.py, covers_charte.json, tools/cover_gen.py, make_charte.py : créés.

## Hypothèses validées / invalidées
- VALIDE : style de pochette avec texte généré par le modèle (lisible, orthographe correcte).
- INVALIDE : `services.ps1 stop -Only generation` arrête la génération -> run_rotation.py reste actif.
- EN ATTENTE : rendu des 3 exemples de charte, jingles réécoutés, iPhone.

## Prochaine étape exacte
Arrêter réellement la génération, relancer ComfyUI-Qwen, générer les 3 exemples de pochette, puis relancer la génération.

## Question bloquante pour la session suivante
Aucune
