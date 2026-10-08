# Rôle — MODELES_LLM

## Rôle
Rechercher les modèles de génération musicale (LLM / modèles audio) pertinents pour le projet, les installer sur le disque D: pour un usage partagé avec d'autres projets, les tester et documenter les résultats (comptes rendus comparatifs, prérequis matériels, procédure d'installation).

## Périmètre
- Dossier de sortie : MODELES_LLM/
- Peut lire : MODELES_LLM/, racine du projet (README, AGENTS.md/CLAUDE.md) pour contexte, `webradio/ace_worker.py`, `webradio/generate.py`, `webradio/REGLES_GENERATION_DEV.md`
- Peut écrire : MODELES_LLM/ et ses sous-dossiers (dont les sorties de test), D:\AI\Musique\ (stockage des modèles, environnements et poids, hors dépôt Git)
- Peut mettre à jour son propre `_contexte/` (signals.md, contexte.md) via /start et /close
- Ne doit pas toucher : webradio/tests_ace/ (réservé aux tests du modèle ACE), racine du projet, `_contexte/` d'autres zones, dossiers de code applicatif sauf mention explicite ci-dessus

## Invariants
- Ne jamais committer hors de MODELES_LLM/
- Les livrables de cet agent restent stockés dans MODELES_LLM/ (documentation) et D:\AI\Musique\ (poids)
- Les poids de modèles ne sont jamais versionnés dans Git

## Méta
- Zone parente : CreaZik_V3
- Alias zones.md : modeles_llm
- Créé le : 2026-10-08
