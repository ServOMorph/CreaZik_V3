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
86 playlists musicales (921 morceaux) et 29 jingles vocaux (WebRadio, Traveling Sound, SérénIA Tech, dans `webradio/jingles/`, voix féminine Chatterbox). Interfaces auditeur/admin séparées (5000/5001) ; l'admin programme, trie, renomme et supprime morceaux et playlists, trie les jingles par catégories et dispose d'une section Statistiques (base `radio.db`, exports JSON/CSV).
L'UI auditeur affiche un cadre visuel unique en cycle de 5 s (pochette, animations, pub cliquable, animations, pochette) ; les boutons Slow/Medium/High sont à nouveau ouverts à tous (l'UI sur le port 5000 est l'UI dev, une UI auditeur viendra plus tard) et leur choix remplace l'énergie mesurée. Mode développement, un seul utilisateur. 25 tests du moteur passent.
Le lot de pochettes se poursuit avec `cover_batch.py` (reprise automatique) ; `python run.py` relance les services. Mise en ligne permanente prévue sur un VPS Linux (voir `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis), non réalisée. Contrôles iPhone en attente ; noms d'artistes et bouton Suivant public à retirer avant le déploiement.
Série de tests de voix ACE-Step « Marie » (`webradio/tests_ace/marie/`, v1 à v9 générées, v7 à v9 à écouter), écoutable via le bouton « Test » de l'UI auditeur ; skill `generation-morceaux` pour préparer les générations.
Légende du visuel animée (titre et description en défilement alterné, validée sur iPhone). Deux agents de zone en parallèle : `textes` (paroles françaises, commande `/generate_lyrics` à créer) et `modeles_llm` (autres modèles musicaux).
