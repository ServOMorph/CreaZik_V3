# Contexte — textes   (immuable sauf décision explicite)

## Objectif (immuable sauf décision explicite)
Écrire les textes de chansons et améliorer le processus d'écriture pour la génération musicale.

## Stack / contraintes techniques (stable, rarement modifié)
- Textes destinés à ACE-Step 1.5 (génération locale, RTX 4060 8 Go) ; format de paroles à documenter par l'agent.
- Textes existants : `TEXTES/artistes/Marie/Marie-1.md`, `TEXTES/artistes/Marie/Marie-1_ace.md` ; paroles du catalogue dans `webradio/playlists/perso/lyrics*` (lecture seule).
- Écriture limitée à `TEXTES/` ; récupération par l'orchestrateur.

## État actuel (réécrit intégralement à chaque /close)
Agent initialisé. Aucun livrable produit par l'agent.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-08 : Création de l'agent ; écriture restreinte à TEXTES/.
