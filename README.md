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
Réorientation vers l'écriture humaine : outils d'extraction de textes, d'apprentissage et de run (`OUTILS/`), 10 textes Funky Yogi relus et 19 versions générées à écouter ; chansons françaises retirées de la radio (14 gardées).
Les générations de test écrivent un `.metadata.json` et un manifeste ; la graine est toujours imposée ; `ace_worker.py` accepte une référence audio et le mode cover. Contrôles iPhone, écoutes, validation des préférences et déploiement VPS en attente.
