# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Chatterbox multilingue (CPU, timbre de référence Kokoro) ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
Réorientation vers l'écriture humaine : outils d'extraction, d'apprentissage et de run en place ; 19 versions Funky Yogi dans les Tests, à écouter ; préférences (867 votes archivés) et règles tirées des négatifs en attente d'accord.
Radio nettoyée le 2026-10-15 : 300 morceaux négatifs et 5 playlists vides supprimés, scores remis à zéro (archive sommée par le calcul) ; playlist « Blues-rock guitare claire » (6 morceaux) en rotation, bouton Test (boucle) et section « Pochettes » (revue + script de régénération) ajoutés.
Restent : mode Test à arrêter, jugement des pochettes, écoutes, clip L'Invariable (droits du cover), contrôles iPhone et navigateur en vraie session admin, application technique de la validation préalable.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-09 : Démo privée T01 (Arroser Les Roses) : version 18 retenue, texte adapté (« posté », « zoublie »), voix de femme non retenue (instable), statut `VALIDE` interdit sans accord écrit de l'auteur ; lot de pochettes terminé, scores négatifs exclus.
- 2026-10-10 : campagne comparative de 30 extraits (10 ACE-Step 1.5, 10 MusicGen Small, 10 HeartMuLa OSS 3B) ; statuts techniques conservés séparément de l'écoute humaine, avec pistes invalides HeartMuLa laissées visibles pour examen.
- 2026-10-10 : Tout nouveau contenu destiné à la WebRadio est soumis dans les Tests avec sa référence éventuelle ; aucune diffusion sans demande explicite de l'utilisateur, même après validation.
- 2026-10-10 : Paroles classées par artiste dans `TEXTES/artistes/` ; l'utilisateur déclare être Funky Yogi et détenir les droits sur ce texte, et déclare disposer des droits sur les textes Marie.
- 2026-10-10 : section Tests rangée en dossiers (clé `folder` ou règles du serveur) avec commentaire par version dans `tests_state.json` ; bouton « Test » supprimé.
- 2026-10-10 : Graine toujours imposée pour les tests ; sidecar et manifeste par génération ; « garde » = ranger le MP3 chez l'artiste ; instrus de Marie générés par 5 graines puis triés à l'écoute (intro non pilotable).
- 2026-10-12 : Écriture humaine : Funky Yogi mis en musique (electro/funk/disco/soul, ~120 BPM), préférences issues des seuls votes radio avec accord avant mise à jour ; chansons françaises retirées de la radio sauf 14 versions.
- 2026-10-12 : À chaque ajout de morceau à la WebRadio, prendre les JSON (sidecar, audiomap) avec ; playlist `creation-francaise` créée pour les créations originales.
- 2026-10-15 : Morceaux à score négatif du catalogue diffusé supprimés (suppression par `RadioEngine.edit_catalog` hors serveur), scores remis à zéro ; archive `DOCUMENTATION/apprentissage/votes_archive/` sommée par `calculer_preferences.py` ; règles tirées des négatifs proposées, non appliquées.
- 2026-10-15 : Playlist « Blues-rock guitare claire » (anglais, nom d'artiste jamais public) validée après test : 6 morceaux positifs en rotation, 4 négatifs supprimés ; bouton Test (`test_loop`) ; revue des pochettes par page locale, plafond de 3 refus ; pas de push pendant l'exécution autonome.
