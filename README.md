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
L'UI auditeur affiche un cadre visuel unique en cycle de 5 s (pochette, animations, pub cliquable, animations, pochette) ; les boutons Slow/Medium/High sont à nouveau ouverts à tous (l'UI sur le port 5000 est l'UI dev, une UI auditeur viendra plus tard) et leur choix remplace l'énergie mesurée. Mode développement, un seul utilisateur. 27 tests du moteur au dernier passage (2026-10-08).
Lot de pochettes terminé (`cover_batch.py`, 175 créées, 256 morceaux exclus pour pouces négatifs) ; `python run.py` relance les services. Mise en ligne permanente prévue sur un VPS Linux (voir `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis), non réalisée. Contrôles iPhone en attente ; noms d'artistes, boutons Suivant et Test, section Tests et `DEV_UNIFIED` à traiter avant le déploiement.
Section « Tests » de l'UI admin : versions de test numérotées (hors catalogue et rotation), lecture, pouces, suppression, barre de position, repère « Jamais écouté ». Titre et date sur les pochettes, police Sora embarquée pour tous les titrages. Graine ACE-Step désormais appliquée ; skill `generation-morceaux` et contrôle des paroles `TEXTES/tools/check_lyrics.py` pour préparer les générations.
Démo privée « Arroser Les Roses » (texte protégé, accord de l'auteur non demandé) : version 18 retenue ; voix de femme encore instable (grille à écouter). Deux agents de zone en parallèle : `textes` (paroles françaises, commande `/generate_lyrics`) et `modeles_llm` (autres modèles musicaux).
