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
86 playlists musicales (921 morceaux) et 20 jingles vocaux. Interfaces auditeur/admin séparées (5000/5001) ; l'admin programme, trie, renomme et supprime morceaux et playlists, et dispose d'une section Statistiques (base `radio.db`, exports JSON/CSV). Les morceaux à score négatif ne sont plus diffusés.
L'UI auditeur propose pouces, « sans avis », dynamique Slow/Medium/High, un carré de publicité cliquable avec une mascotte à 20 styles, et le morceau démarre en fondu sous le jingle. 25 tests du moteur passent.
Le lot de pochettes tourne (699 à générer au dernier statut, 26 exclues pour score négatif) ; `/generate_covers` le reprend. `python run.py` relance les services. Contrôles iPhone en attente ; noms d'artistes et bouton Suivant public à retirer avant le déploiement.
