# Améliorations à faire

Cette liste centrale recense les améliorations encore ouvertes. Garder chaque entrée concrète, éviter les doublons et retirer une entrée uniquement lorsqu'elle est terminée ; les contrôles manuels non validés restent dans `tests_manuels.md`.

## À faire

- [ ] Générer les pochettes manquantes éligibles avec `/generate_covers`, selon la priorité et les exclusions définies par les votes.
- [ ] Avant le déploiement de l'application, remplacer les noms d'artistes dans les titres des playlists inspirées par des formulations descriptives des genres musicaux. Les noms sont conservés pendant le développement ; voir les précautions dans `webradio/REGLES_GENERATION_DEV.md`.
- [ ] Avant le déploiement : retirer le bouton « Suivant » public de l'UI auditeur (listen.js, fonction applyMode, et `PUBLIC_SKIP` dans server.py), ainsi que les boutons Renommer/Supprimer si exposés. Le saut change le morceau pour tous les auditeurs ; il n'est public que pendant la phase de test.
- [ ] Choisir parmi les propositions de réaménagement de l'UI admin (barre d'accès rapide, onglets Direct/Réglages/Catalogue/Analyse, tableau de bord Direct, réglages simples/avancés) et les appliquer.
- [ ] Décider du sort de `webradio/ui.html` (explorateur) maintenant que ses fonctions sont dans le catalogue admin ; le supprimer ou le garder.
- [ ] Retirer de `series.txt` les playlists supprimées via l'admin, sinon la rotation les régénère ; ajouter un contrôle automatique à la suppression d'une playlist.
- [ ] Faire utiliser les noms modifiés dans `catalog_overrides.json` par `cover_gen.py` / `cover_batch.py` (ils lisent encore `playlists.json`).
