# Signals — CreaZik_V3   (MAJ 2026-10-06)

## Actions ouvertes
- [P1|ouvert] Générer 3 images d'exemple de pochettes avec charte graphique par playlist, les faire valider, puis lancer le lot quand la file de génération musicale est vide
  - fait quand: l'utilisateur valide les 3 exemples (flamenco "Rumba du matin", hard-tech "Rave souterraine", medieval-renaissance "Danse médiévale") et le lot est lancé ou planifié
  - réf: webradio/covers_charte.json (87 playlists), webradio/tools/cover_gen.py, tools/make_charte.py ; avant : /stop, lancer ComfyUI-Qwen (lancer.bat, port 8189) ; après : python run.py pour tout relancer (le tunnel Cloudflare reste manuel)
- [P2|ouvert] Réécouter les 20 jingles « Créa Zik IA WebRadio » (voix, prononciation « Ouèbe Radio ») et tester run.py (lance les 4 services puis ouvre ui.html ; lancer depuis un état arrêté, sinon doublon de rotation)
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
- Tout est arrêté (commande /stop testée) ; relancer par `python run.py`. Ollama tourne sans modèle chargé. Des run.py d'autres projets (SerenIATech, TableauDeBord, Orga) tournent : ne pas les arrêter.
- Services : `.\services.ps1 restart -Only serveur|analyse|compression|generation` ; toujours relancer après un arrêt.
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`.

## Dernière session (2026-10-06)
# Session du 2026-10-06

## Décisions prises
- run.py à la racine lance les 4 services puis ouvre l'UI ; commande /stop arrête tout et libère la VRAM.
- Nom de la radio « CréaZik IA WebRadio » (UI et jingles) ; pochettes avec texte généré par le modèle, charte par playlist.

## Livrables produits ou modifiés
- run.py, .claude/commands/stop.md : créés, /stop testée.
- webradio/services.ps1 : stop arrête aussi run_rotation.py.
- webradio/covers_charte.json, tools/cover_gen.py : créés (3 exemples non générés).

## Hypothèses validées / invalidées
- VALIDE : /stop arrête les 4 services ; VRAM à 1,5 Go (applications Windows).
- EN ATTENTE : run.py non testé (risque de doublon si une rotation tourne), 3 exemples de pochette, jingles à réécouter.

## Prochaine étape exacte
Lancer python run.py, puis arrêter la génération (/stop), lancer ComfyUI-Qwen et générer les 3 exemples de pochette.

## Question bloquante pour la session suivante
Aucune
