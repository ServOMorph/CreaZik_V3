# Contexte — textes   (immuable sauf décision explicite)

## Objectif (immuable sauf décision explicite)
Écrire les textes de chansons et améliorer le processus d'écriture pour la génération musicale.

## Stack / contraintes techniques (stable, rarement modifié)
- Textes destinés à ACE-Step 1.5 (génération locale, RTX 4060 8 Go) ; format de paroles à documenter par l'agent.
- Textes existants : `TEXTES/artistes/Marie/Marie-1.md`, `TEXTES/artistes/Marie/Marie-1_ace.md` ; paroles du catalogue dans `webradio/playlists/perso/lyrics*` (lecture seule).
- Écriture limitée à `TEXTES/` ; récupération par l'orchestrateur.

## État actuel (réécrit intégralement à chaque /close)
Génération de paroles par LLM abandonnée. Deux textes suivis dans `TEXTES/liste_attente.md` : T01 (Lagniel, démo v18 générée, accord de l'auteur absent) et T02 (Capitaine Red Barbosa, à préparer). Textes protégés dans `usage_prive/`, textes déclarés libres dans `domaine_public/`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-08 : Création de l'agent ; écriture restreinte à TEXTES/.
- 2026-10-13 : Textes protégés uniquement dans `usage_prive/`, jamais en playlist/radio sans accord écrit de l'auteur ; suivi des textes par `liste_attente.py`.
