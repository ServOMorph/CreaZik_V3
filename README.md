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
- `TEXTES/` : textes de test pour la génération musicale.

## État actuel
86 playlists musicales et 29 jingles actifs ; interfaces auditeur/admin séparées (5000/5001). Section « Tests » admin avec dossiers de modèles et commandes d'écoute.
Campagne comparative disponible : 10 pistes ACE-Step 1.5 et 10 MusicGen Small techniquement passées ; 5 pistes HeartMuLa OSS 3B passées, 5 invalides pour défauts techniques. Ces 30 nouvelles pistes restent en attente d'écoute humaine ; 10 pistes Stable Audio d'une campagne antérieure figurent aussi dans l'UI.
Prompts, paramètres, tentatives et métadonnées de la campagne sont consignés dans `MODELES_LLM/sorties/campagne_2026-10-09/`; les fichiers MP3 sont servis dans les dossiers de tests correspondants.
Lot de pochettes terminé ; prochaine étape : écouter les 30 pistes et continuer les contrôles iPhone en attente. Déploiement VPS non réalisé.
Démo privée « Arroser Les Roses » : version 18 retenue ; voix de femme encore à évaluer. Avant déploiement, les points recensés dans `AMELIORATIONS.md` restent à traiter.
