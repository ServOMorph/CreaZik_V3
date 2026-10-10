# CreaZik_V3

WebRadio IA locale : musique générée en local avec ACE-Step 1.5, diffusée en direct à tous les auditeurs (client web pensé pour iPhone, tunnel Cloudflare).

## Stack
- Génération : ACE-Step 1.5 (RTX 4060 8 Go), voix des jingles Chatterbox multilingue, pochettes ComfyUI-Qwen.
- Radio : serveur Python (port 5000 pour les auditeurs, port local 5001 pour l'administration), moteur `webradio/radio_engine.py`, audio MP3 uniquement.

## Structure
- `webradio/` : application (serveur, moteur, client, génération, playlists).
- `PLAN_WEBRADIO.md`, `roadmap_webradio.md` : suivi d'exécution et phases.
- `webradio/REGLES_GENERATION_DEV.md` : règles de génération et de développement.
- `tests_manuels.md` : contrôles manuels en attente.
- `TEXTES/` : paroles classées par artiste et textes destinés à la génération musicale.

## État actuel
Interfaces auditeur/admin séparées (5000/5001) et section « Tests » pour écouter les créations avant toute diffusion. Chaque ajout à la WebRadio nécessite une demande explicite de l'utilisateur.
Campagne comparative écoutée : 40 votes dans les Tests ; ACE-Step 1.5 obtient 10 avis positifs sur 10, MusicGen Small, HeartMuLa OSS 3B et Stable Audio 3 Small-Music en obtiennent chacun 2 sur 10. Les métadonnées restent dans `MODELES_LLM/sorties/campagne_2026-10-09/`.
Les essais temporaires « Soul du matin » et « Funky Yogi » ont été supprimés ; l'original « Soul du matin » reste dans la WebRadio. Les paroles Funky Yogi et Marie sont classées dans `TEXTES/artistes/`, avec les droits déclarés par l'utilisateur.
La validation préalable reste à appliquer techniquement au pipeline automatique. Les contrôles iPhone et la grille de voix féminine restent en attente ; déploiement VPS non réalisé.
