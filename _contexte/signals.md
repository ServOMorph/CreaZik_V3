# Signals — CreaZik_V3   (MAJ 2026-10-06)

## Actions ouvertes
- [P1|ouvert] Contrôles manuels iPhone des nouveautés (UI auditeur, jingle vers morceau, mascotte, admin) et réécoute des 20 jingles vocaux
  - fait quand: les sections correspondantes de `tests_manuels.md` sont vidées par contrôles réels (fondu sous jingle, mascotte, carré de pub cliquable, boutons sans avis / Slow-Medium-High, Suivant, section Statistiques, catalogue admin)
  - réf: `tests_manuels.md`, `webradio/listen.js`, `webradio/mascot.js`, `webradio/radio.html`, `webradio/voice_jingles.json`
- [P1|ouvert] Terminer la génération des pochettes éligibles (batch en cours, nouveau prompt : titre très grand sans numéro, playlist en grand, date très petite)
  - fait quand: toutes les pochettes éligibles sont générées ou les échecs restants sont listés, scores négatifs exclus
  - réf: `python webradio/tools/cover_batch.py --status` (au dernier statut : 746 tâches, 699 à générer, 26 exclues pour score négatif), `webradio/logs/cover_generation_state.json`, `.claude/commands/generate_covers.md`
- [P2|ouvert] Changer le mot de passe admin par défaut
  - fait quand: mot de passe admin changé et accès confirmé
  - réf: `webradio/REGLES_GENERATION_DEV.md` section 6, `tests_manuels.md`
- [P2|ouvert] Avant le déploiement : retirer le bouton « Suivant » public (`PUBLIC_SKIP` dans `server.py`, `applyMode` dans `listen.js`), remplacer les noms d'artistes des titres de playlists par des genres, et trancher l'exposition des boutons Renommer/Supprimer
  - fait quand: aucun saut public possible, aucun nom d'artiste dans les titres publics
  - réf: `AMELIORATIONS.md`, `webradio/REGLES_GENERATION_DEV.md` sections 3.6 et 5.5, `webradio/playlists.json`
- [P2|ouvert] Choisir parmi les propositions de réaménagement de l'UI admin (barre d'accès rapide, onglets Direct/Réglages/Catalogue/Analyse, tableau de bord Direct, réglages simples/avancés) et décider du sort de `ui.html` (explorateur devenu redondant)
  - fait quand: l'utilisateur a tranché et les choix retenus sont appliqués
  - réf: `webradio/radio.html`, `webradio/ui.html`
- [P3|ouvert] Poursuivre la génération musicale en rotation (86 playlists musicales, 921 morceaux, 85 identifiants dans `series.txt`) et retirer de « idée de playlist.md » chaque entrée une fois sa playlist complète
  - fait quand: toutes les pistes prévues sont générées et les entrées terminées sont retirées de la liste d'idées
  - réf: `webradio/run_rotation.py`, `webradio/series.txt`, `idée de playlist.md` (restent : Rap Français autotuné, Hight Light Tribe, non traités)
- [P3|ouvert] Confirmer l'interprétation « Mike Fields = Mike Oldfield »
  - fait quand: l'utilisateur confirme ou corrige
  - réf: `PLAN_WEBRADIO.md` section 4.5

## Contexte chaud
- Le serveur radio (5000/5001), l'analyse, la compression, le batch de pochettes et ComfyUI-Qwen tournaient en fin de session ; la génération musicale n'a pas été relancée (voir `/start_generation`). Le serveur a été redémarré plusieurs fois pour prendre en compte les nouvelles routes ; en cas de nouvelle modification Python, il faut le redémarrer (`services.ps1 restart -Only serveur`).
- `radio.db` (SQLite, non versionnée) enregistre diffusions, « sans avis » et avis de dynamique depuis le 2026-10-06 ; `catalog_overrides.json` porte renommages et suppressions ; `webradio/learning/morceaux_rejetes.jsonl` (versionné) contient une première suppression réelle faite par l'utilisateur.
- Les 8 jingles instrumentaux ont été supprimés ; il reste 20 jingles vocaux. Les agents design ont appliqué la nouvelle organisation de `radio.html` et le layout de `listen.html` sans test sur iPhone.
- Fichiers non suivis laissés à part : `liste_musiques_queue.md`, `_archive_docs/`, `webradio/silence.wav.viz.json`.

## Dernière session (2026-10-06)
# Session du 2026-10-06

## Décisions prises
- Base SQLite `radio.db` (diffusions, « sans avis », avis Slow/Medium/High à un ou deux boutons) ; section Statistiques admin avec exports JSON (dictionnaire de champs) et CSV.
- Suppression d'un morceau ou d'une playlist : MP3 et pochette effacés, données de création archivées dans `learning/morceaux_rejetes.jsonl` ; renommage via `catalog_overrides.json` ; score négatif = plus diffusé.
- UI auditeur : visuel réduit à gauche, carré de pub cliquable à droite (pubs du site + messages de la radio, mascotte de 5 s avec 20 chorégraphies selon le style) ; légende titre/style sur les visuels sans pochette ; bouton Suivant public pendant les tests.
- Jingles : instrumentaux supprimés ; le morceau démarre en fondu sous le jingle puis monte au maximum.

## Livrables produits ou modifiés
- `webradio/stats_db.py`, `radio_engine.py`, `server.py` : base, analytics, catalogue éditable, fondu sous jingle, route de saut, validation de dynamique.
- `webradio/radio.html` : catalogue fusionné avec l'explorateur, tri par score/nom/poids, statistiques, sections fermées par défaut, réorganisation par l'agent design ; bouton Explorateur supprimé.
- `webradio/listen.html`, `listen.css`, `listen.js`, `mascot.js`, `motion.js` : UI auditeur, panneau de pub, mascotte, bouton de texte des pubs ajusté.
- `webradio/tools/cover_gen.py` : titre et style plus grands, sans numéro ; `tests/test_radio_engine.py` : 25 tests, tous passent.
- `REGLES_GENERATION_DEV.md`, `AMELIORATIONS.md`, `tests_manuels.md` : mis à jour.

## Hypothèses validées / invalidées
- VALIDE : 25 tests passent ; rendu navigateur (serveur statique) du catalogue admin, de la planche des 20 mascottes et des transitions de pubs ; endpoints dynamique (un ou deux niveaux) répondent sur le serveur redémarré.
- INVALIDE : le bouton de dynamique « ne reste pas allumé » venait d'un serveur non redémarré, pas du code client.
- EN ATTENTE : tous les contrôles iPhone ; interprétation des messages dictés (deux boutons = niveaux intermédiaires ; « numéro devant » = titre sans numéro) non confirmée ; fondu sous jingle à écouter.

## Prochaine étape exacte
Faire les contrôles manuels listés dans `tests_manuels.md` (iPhone), puis choisir les propositions de réaménagement admin et le sort de `ui.html`.

## Question bloquante pour la session suivante
Aucune
