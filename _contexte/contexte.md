# Contexte — CreaZik_V3

## Objectif (immuable sauf décision explicite)
expérimentation de création de musique avec IA instrumental et vocal, avec modification possible complète des créations

## Stack / contraintes techniques (stable, rarement modifié)
- Génération musicale : ACE-Step 1.5 en local (RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X), pipeline dans `webradio/`.
- Radio : serveur Python (port 5000) + moteur `radio_engine.py`, client web (iPhone Safari), tunnel Cloudflare.
- Voix des jingles : Chatterbox multilingue (CPU, timbre de référence Kokoro) ; pochettes : ComfyUI-Qwen (Qwen-Image 2.1 GGUF, port 8189).
- Audio diffusé : MP3 192 kbit/s uniquement. Règles détaillées : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
WebRadio locale avec interface de Tests ; tout nouveau contenu destiné à la diffusion passe d'abord par l'écoute et nécessite ensuite une demande explicite de l'utilisateur.
Campagne comparative écoutée : 40 votes dans les Tests ; ACE-Step 10 positifs sur 10, MusicGen, HeartMuLa et Stable Audio 2 positifs sur 10 chacun. Les contrôles techniques restent distincts des votes artistiques.
Essais temporaires « Soul du matin » et « Funky Yogi » supprimés ; seul l'original « Soul du matin » reste dans la WebRadio. Les paroles Funky Yogi et Marie sont classées sous `TEXTES/artistes/` avec les droits déclarés par l'utilisateur.
Démo T01 version 18 retenue ; grille de voix féminine et contrôles iPhone encore à effectuer (`tests_manuels.md`).
La validation préalable est consignée mais son application technique à la génération automatique reste ouverte (`AMELIORATIONS.md`).

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-07 : L'UI du port 5000 devient l'UI dev ; boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin), à refermer avec l'UI auditeur future.
- 2026-10-08 : Mise en ligne prévue sur VPS Linux bon marché (systemd, HTTPS, sous-domaine du site) ; Vercel, Render gratuit et Netlify écartés ; pas encore réalisée.
- 2026-10-08 : Deux agents de zone (`textes`, `modeles_llm`) pour travailler en parallèle ; nom d'artiste en consigne de style interne seulement, jamais public.
- 2026-10-09 : Section « Tests » dans l'UI admin (du plus récent au plus ancien, pouces, suppression, barre de position, repère « Jamais écouté », numéro unique par test) ; police Sora embarquée pour tous les titrages, pubs Traveling Sound en machine à écrire ; titre et date sur la pochette sans toucher l'image.
- 2026-10-09 : La graine ACE n'était pas appliquée (`use_random_seed` vrai par défaut) : corrigé dans `ace_worker.py` ; les essais « à graine fixe » antérieurs ne sont pas fiables ; paroles contrôlées par `check_lyrics.py` avant chaque lancement.
- 2026-10-09 : Démo privée T01 (Arroser Les Roses) : version 18 retenue, texte adapté (« posté », « zoublie »), voix de femme non retenue (instable), statut `VALIDE` interdit sans accord écrit de l'auteur ; lot de pochettes terminé, scores négatifs exclus.
- 2026-10-10 : campagne comparative de 30 extraits (10 ACE-Step 1.5, 10 MusicGen Small, 10 HeartMuLa OSS 3B) ; statuts techniques conservés séparément de l'écoute humaine, avec pistes invalides HeartMuLa laissées visibles pour examen.
- 2026-10-10 : Tout nouveau contenu destiné à la WebRadio est soumis dans les Tests avec sa référence éventuelle ; aucune diffusion sans demande explicite de l'utilisateur, même après validation.
- 2026-10-10 : Paroles classées par artiste dans `TEXTES/artistes/` ; l'utilisateur déclare être Funky Yogi et détenir les droits sur ce texte, et déclare disposer des droits sur les textes Marie.
- 2026-10-10 : section Tests rangée en dossiers (clé `folder` ou règles du serveur) avec commentaire par version dans `tests_state.json` ; bouton « Test » supprimé.
