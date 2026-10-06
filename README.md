# CreaZik_V3

WebRadio IA locale : musique générée en local avec ACE-Step 1.5, diffusée en direct à tous les auditeurs (client web pensé pour iPhone, tunnel Cloudflare).

## Stack
- Génération : ACE-Step 1.5 (RTX 4060 8 Go), voix des jingles Kokoro-82M, pochettes ComfyUI-Qwen.
- Radio : serveur Python (port 5000), moteur `webradio/radio_engine.py`, audio MP3 uniquement.

## Structure
- `webradio/` : application (serveur, moteur, client, génération, playlists).
- `PLAN_WEBRADIO.md`, `roadmap_webradio.md` : suivi d'exécution et phases.
- `webradio/REGLES_GENERATION_DEV.md` : règles de génération et de développement.
- `tests_manuels.md` : contrôles manuels en attente.

## État actuel
89 playlists configurées, génération en rotation. Dynamique horaire, arc visuel par morceau et mode auditeur (bandeau Traveling Sound) livrés ; 19 tests automatiques passent. Bug du clic admin corrigé. Pochettes : style avec texte validé, charte par playlist écrite, 3 exemples à générer ; contrôles iPhone en attente.
