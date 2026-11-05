# CreaZik_V3

WebRadio IA locale : musique générée en local avec ACE-Step 1.5, diffusée en direct à tous les auditeurs (client web pensé pour iPhone, tunnel Cloudflare).

## Stack
- Génération : ACE-Step 1.5 (RTX 4060 8 Go), voix des jingles Chatterbox multilingue, pochettes ComfyUI-Qwen.
- Radio : serveur Python (port 5000, UI unique auditeur et admin), moteur `webradio/radio_engine.py`, audio MP3 uniquement.

## Structure
- `webradio/` : application (serveur, moteur, client, génération, playlists) ; `webradio/user.html` : interface auditeur (page d'accueil du port 5000).
- `revue_ui_user/` : artefact de revue de l'interface auditeur.
- `PLAN_WEBRADIO.md`, `roadmap_webradio.md` : suivi d'exécution et phases.
- `webradio/REGLES_GENERATION_DEV.md` : règles de génération et de développement.
- `tests_manuels.md` : contrôles manuels en attente.
- `TEXTES/` : paroles classées par artiste et textes destinés à la génération musicale.

## État actuel
UI unique sur le port 5000 (`webradio/user.html`) : profils d'UI et comptes, plugins auditeur (styles, création d'image, création de morceau) et admin (programmation, outils, jingle texte, suivi du travail) ; la page `/` sert l'auditeur, l'admin s'y connecte par identifiant. Jingles urgents, lecture personnelle, délégation à Codex et OpenCode (`_codex/`).
Les files d'images et de morceaux d'auditeurs sont en pause (`webradio/gpu_pause.flag`) pendant un entraînement GPU externe. Section « Tests » pour écouter les créations avant toute diffusion de contenu généré par l'administrateur.
Réorientation vers l'écriture humaine (`OUTILS/`, 19 versions Funky Yogi à écouter) ; exploration stop motion (robot batteur retenu). Écoutes, contrôles iPhone, validation des préférences et déploiement VPS en attente.
