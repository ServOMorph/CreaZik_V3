# Améliorations à faire

Cette liste centrale recense les améliorations encore ouvertes. Garder chaque entrée concrète, éviter les doublons et retirer une entrée uniquement lorsqu'elle est terminée ; les contrôles manuels non validés restent dans `tests_manuels.md`.

## À faire

- [ ] Appliquer techniquement la validation préalable des nouveaux contenus : diriger les générations vers l'interface de Tests (ou y ajouter le support des formats nécessaires), puis empêcher leur ajout aux playlists diffusées et à la rotation sans demande explicite de l'utilisateur. La génération et la rotation actuelles écrivent encore directement dans les sorties des playlists.
- [ ] Avant le déploiement de l'application, remplacer les noms d'artistes dans les titres des playlists inspirées par des formulations descriptives des genres musicaux. Les noms sont conservés pendant le développement ; voir les précautions dans `webradio/REGLES_GENERATION_DEV.md`.
- [ ] Avant le déploiement : retirer le bouton « Suivant » public de l'UI auditeur (listen.js, fonction applyMode, et `PUBLIC_SKIP` dans server.py), ainsi que les boutons Renommer/Supprimer si exposés. Le saut change le morceau pour tous les auditeurs ; il n'est public que pendant la phase de test.
- [ ] Choisir parmi les propositions de réaménagement de l'UI admin (barre d'accès rapide, onglets Direct/Réglages/Catalogue/Analyse, tableau de bord Direct, réglages simples/avancés) et les appliquer.
- [ ] Décider du sort de `webradio/ui.html` (explorateur) maintenant que ses fonctions sont dans le catalogue admin ; le supprimer ou le garder.
- [ ] Retirer de `series.txt` les playlists supprimées via l'admin, sinon la rotation les régénère ; ajouter un contrôle automatique à la suppression d'une playlist.
- [ ] Faire utiliser les noms modifiés dans `catalog_overrides.json` par `cover_gen.py` / `cover_batch.py` (ils lisent encore `playlists.json`).
- [ ] Régénérer les 14 jingles WebRadio restants avec « IA » prononcé, une fois la prononciation validée à l'écoute (scripts dans `D:\ServOMorph\TTS_Local\`).
- [ ] Décider avant le déploiement si les boutons Slow/Medium/High restent réservés au développeur (actuellement ouverts à tous dans l'UI dev, `/api/dynamics` sans contrôle admin, poids 1 dans la dynamique). Créer une UI auditeur séparée de l'UI dev.
- [ ] Avant le déploiement : retirer la section « Tests » (le bouton « Test » public est déjà supprimé) (routes `/api/tests*` de `server.py`, `tests_state.json`) et le dossier `webradio/playlists/tests-ace/`, ou les verrouiller derrière l'admin ; exclure `tests-ace` des motifs statiques publics.
- [ ] Avant le déploiement : remplacer `DEV_UNIFIED = True` (en dur dans `server.py`) par un réglage explicite (argument ou variable d'environnement, faux par défaut), car il rend atteignables les pages admin et la connexion et assouplit le CSP.
- [ ] Mettre la radio en ligne en permanence sur un VPS Linux (systemd, HTTPS, sous-domaine du site, synchronisation des mp3 et pochettes sans écraser `radio.db`), puis ajouter un lien « Radio » sur le site ; tester d'abord le serveur sous Linux. Détail : `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis.
- [ ] Compléter le contrôle des paroles `TEXTES/tools/check_lyrics.py` (balises, syllabes et durée existent) avec rimes pauvres, répétitions et clichés, et valider la qualité réelle d'un lot de paroles produit par `/generate_lyrics` (commande créée).
- [ ] Voix de femme stable avec ACE-Step : écouter la grille (tests 26 à 31 et 39 à 44), puis essayer les pistes restantes (durée courte, « female vocal » en fin de caption, modèle Base ou XL Turbo à installer) et consigner le résultat dans le skill `generation-morceaux`.
- [ ] Confirmer le seuil `0.688` de `jlayout` dans `webradio/motion.js` et la suppression du formulaire de commentaires / du bloc « musique humaine » dans `webradio/listen.html` (changements hors de cette session) : corriger ou assumer.
- [ ] Concurrence entre `ace_worker.py` (réécrit `playlist_results.json` sans verrou) et la suppression d'un test du dossier `tests-ace` par le serveur : masquer par un état séparé ou partager un verrou si des tests y sont régénérés pendant une suppression.
