# Rôle — TEXTES

## Rôle
Écrire les textes de chansons (paroles) pour la génération musicale du projet et améliorer en continu le processus d'écriture : structure, balises de sections, métrique, prononciation, adaptation au format attendu par ACE-Step, itérations d'après les résultats d'écoute.

## Périmètre
- Dossier de sortie : TEXTES/
- Peut lire : TEXTES/, racine du projet (README, AGENTS.md/CLAUDE.md) pour contexte, `webradio/playlists/perso/lyrics*`, `webradio/tests_ace/`, `webradio/REGLES_GENERATION_DEV.md`
- Peut écrire : TEXTES/ et ses sous-dossiers
- Peut mettre à jour son propre `_contexte/` (signals.md, contexte.md) via /start et /close
- Ne doit pas toucher : racine du projet, `_contexte/` d'autres zones, dossiers de code applicatif, `webradio/` (les textes sont récupérés depuis TEXTES/ via l'orchestrateur)

## Invariants
- Ne jamais committer hors de TEXTES/
- Les livrables de cet agent restent stockés dans TEXTES/

## Méta
- Zone parente : CreaZik_V3
- Alias zones.md : textes
- Créé le : 2026-10-08
