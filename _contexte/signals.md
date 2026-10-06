# Signals — CreaZik_V3   (MAJ 2026-10-06)

## Actions ouvertes
- [P1|ouvert] Reprendre et terminer la génération des pochettes éligibles
  - fait quand: toutes les pochettes éligibles sont générées ou les échecs restants sont listés, les scores négatifs restant exclus
  - réf: `webradio/logs/cover_generation_state.json`, `python webradio/tools/cover_batch.py --status`, `.claude/commands/generate_covers.md` ; état à la clôture : interrompu, 107 créées sur 950 tâches initiales, 804 encore manquantes au dernier contrôle, 26 exclues pour score négatif
- [P2|ouvert] Réécouter les 20 jingles « Créa Zik IA WebRadio » et effectuer les contrôles iPhone, y compris la recherche dans la programmation admin
  - fait quand: jingles validés et section correspondante de `tests_manuels.md` vidée par contrôles réels
  - réf: `webradio/voice_jingles.json`, `tests_manuels.md`, `webradio/radio.html`
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement, remplacer les noms d'artistes des titres de playlists par des descriptions de genres
  - fait quand: aucun nom d'artiste ne figure dans les titres publics avant mise en production
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` section 5.5, `webradio/playlists.json`
- [P3|ouvert] Poursuivre la génération musicale en rotation (88 entrées au catalogue, 86 identifiants dans `series.txt`, dont 11 playlists « Esprit ») et retirer de « idée de playlist.md » chaque entrée une fois sa playlist complète
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md` (restent : Rap Français autotuné, Hight Light Tribe, non traités)
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- À la demande de l'utilisateur, tous les services WebRadio sont arrêtés. État final contrôlé : serveur, analyse, compression et génération à l'arrêt ; ComfyUI n'écoute plus sur 8189 ; GPU à 1714 MiB utilisés sur 8188 MiB. `ollama ps` ne liste aucun modèle chargé ; l'application Ollama n'a pas été arrêtée. Le tunnel Cloudflare manuel n'a pas été touché.
- Reprise radio : `python run.py`. Reprise pochettes : `/generate_covers` ; le batch avait 107 images terminées, 804 manquantes au dernier statut, 26 pistes exclues pour score négatif. L'image temporaire en cours sera ignorée/nettoyée par le batch à la reprise.
- Les interfaces user/admin sont séparées (ports 5000/5001). L'admin permet de programmer morceaux et playlists et de rechercher par titre de morceau ou nom de playlist.
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`, `06-10-2026`, `matin` ; ne pas intégrer sans vérification.

## Dernière session (2026-10-06)
# Session du 2026-10-06

## Décisions prises
- Garder les noms d'artistes pendant le développement ; les remplacer par des genres descriptifs avant le déploiement.
- Retirer « Playlist » des titres affichés et remplacer les libellés « Perso » par des intitulés descriptifs.
- À la demande de l'utilisateur, arrêter tous les services et processus WebRadio et ComfyUI ; laisser le tunnel Cloudflare et les applications d'autres projets intacts.

## Livrables produits ou modifiés
- `webradio/radio.html` : programmation admin restaurée avec ajout de morceaux/playlists et recherche.
- `webradio/playlists.json` : 88 libellés harmonisés, sans préfixe « Playlist » ni « Perso ».
- `webradio/REGLES_GENERATION_DEV.md`, `AMELIORATIONS.md` : précaution juridique et remplacement des noms d'artistes prévu avant déploiement.
- Génération des pochettes interrompue proprement dans son état de reprise : 107 images créées, 804 manquantes au dernier statut ; `cover_generation_state.json` marqué `interrupted`.
- `.claude/commands/replace_downvoted_tracks.md` créé puis supprimé à la demande de l'utilisateur ; il ne reste pas dans le dépôt.

## Hypothèses validées / invalidées
- VALIDE : services WebRadio à l'arrêt, port ComfyUI 8189 fermé, 1714 MiB de VRAM utilisés (applications Windows).
- EN ATTENTE : reprise des pochettes ; contrôles manuels iPhone et jingles ; renommage des titres d'artistes avant le déploiement.

## Prochaine étape exacte
Relancer `/generate_covers` pour reprendre les pochettes manquantes. Les services radio restent arrêtés jusqu'à une demande de redémarrage.

## Question bloquante pour la session suivante
Aucune
