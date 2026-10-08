# Contexte — modeles_llm   (immuable sauf décision explicite)

## Objectif (immuable sauf décision explicite)
Rechercher, installer et tester les modèles de génération musicale pertinents pour le projet.

## Stack / contraintes techniques (stable, rarement modifié)
- Modèle actuel : ACE-Step 1.5 en local ; pipeline `webradio/ace_worker.py`, `webradio/generate.py`.
- Matériel : RTX 4060 8 Go, 48 Go de RAM, Ryzen 7 5700X.
- Modèles installés sur D:\AI\Musique\ (hors Git) pour partage avec d'autres projets ; documentation et comptes rendus dans `MODELES_LLM/`.
- Sorties de test dans `MODELES_LLM/` ; `webradio/tests_ace/` est réservé aux tests du modèle ACE (interdit à cet agent). Règles : `webradio/REGLES_GENERATION_DEV.md`.

## État actuel (réécrit intégralement à chaque /close)
Agent initialisé. Aucun modèle évalué.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-10-08 : Création de l'agent ; modèles installés sur D:\AI\Musique\ (après analyse de D:, convention D:/AI/ ; poids Hugging Face dans D:/HuggingFaceCache).
