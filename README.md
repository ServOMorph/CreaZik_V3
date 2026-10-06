# CreaZik_V3

WebRadio IA locale : musique générée en local avec ACE-Step 1.5, diffusée en direct à tous les auditeurs (client web pensé pour iPhone, tunnel Cloudflare).

## Stack
- Génération : ACE-Step 1.5 (RTX 4060 8 Go), voix des jingles Kokoro-82M, pochettes ComfyUI-Qwen.
- Radio : serveur Python (port 5000 pour les auditeurs, port local 5001 pour l'administration), moteur `webradio/radio_engine.py`, audio MP3 uniquement.

## Structure
- `webradio/` : application (serveur, moteur, client, génération, playlists).
- `PLAN_WEBRADIO.md`, `roadmap_webradio.md` : suivi d'exécution et phases.
- `webradio/REGLES_GENERATION_DEV.md` : règles de génération et de développement.
- `tests_manuels.md` : contrôles manuels en attente.

## État actuel
88 entrées au catalogue, dont 86 identifiants en rotation. Les interfaces auditeur/admin sont séparées (5000/5001) ; l'admin permet de programmer une piste ou une playlist et de les rechercher. Les titres affichés ne comportent plus « Playlist » ni « Perso » ; les noms d'artistes seront remplacés avant le déploiement.
19 tests du moteur passent. Le lot de pochettes est interrompu et reprenable : 107 créées sur 950 tâches initiales, 804 encore manquantes et 26 exclues pour score négatif au dernier statut. Relancer avec `/generate_covers`. Les services sont actuellement arrêtés à la demande de l'utilisateur ; `python run.py` les relance. Contrôles iPhone et écoute des jingles en attente.
