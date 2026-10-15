# Changelog

## v1.13 — 2026-10-15

### Ajouté
- Section « Pochettes » (admin) avec boutons Valider / À refaire, `webradio/covers_review.py`, routes `/api/covers/review` et `/api/covers/verdict`, script `webradio/tools/cover_review_watch.py` (plafond de 3 régénérations) et 8 tests.
- Bouton « Test » : boucle de la playlist `blues-rock-guitare` (`test_loop` du moteur, 2 tests) ; boutons « Tout plier / Tout déplier » (panneau Programmation et sections de `radio.html`).
- Playlist « Blues-rock guitare claire » (10 morceaux générés, 6 gardés après écoute) ; `roadmap_nuit_autonome.md`.
- Archive de votes `DOCUMENTATION/apprentissage/votes_archive/` sommée par `calculer_preferences.py` (`--sans-archive`, 3 tests) ; analyse des morceaux négatifs et règles proposées.

### Modifié
- 300 morceaux à score négatif supprimés, 5 playlists vides supprimées, `series.txt` nettoyé, scores remis à zéro ; la playlist blues-rock passe de poids 0 à la rotation normale.

## v1.12 — 2026-10-12

### Ajouté
- Écriture humaine : `OUTILS/extraction_paroles/` (extraction locale des textes photographiés), `OUTILS/apprentissage/` (préférences issues des votes, diff avant application), `OUTILS/run_textes/` (run automatique par texte, graine de reprise) et `DOCUMENTATION/apprentissage/` ; 10 textes Funky Yogi relus et 19 versions générées dans les Tests ; `roadmap_ecriture_humaine.md`.
- Section Tests : entrées `planned` sans MP3, texte sur plusieurs lignes, boutons sous le texte, plier/déplier.
- `ace_worker.py` : graine effective enregistrée, `reference_audio`, `src_audio` et mode cover (`task_type`, extraits `audio_start_s`/`audio_duration_s`).
- Playlist `creation-francaise` ; morceau 22 dans `instrumental` avec ses JSON ; clip L'Invariable : cas 7 à 22 dans `webradio/tests_ace/clip_atelier_invariable/`.

### Corrigé
- Serveur relancé après arrêt prolongé : le rattrapage du moteur empêchait la lecture sur téléphone ; serveur Eleventy parasite du port 5000 arrêté.

### Modifié
- Chansons françaises retirées de la diffusion (14 versions gardées), boucle de lecture désactivée ; `/close` calcule et présente le diff des préférences.

## v1.11 — 2026-10-10

### Ajouté
- Traçabilité de chaque génération (`ace_worker.py` : sidecar `.metadata.json`, manifeste, nom de fichier avec horodatage et graine) ; `lyrics` pris en compte pour les instrumentaux.
- Instrus rap mélodique de Marie conservés dans `TEXTES/artistes/Marie/` (`tops_instrus/` : graines 2026 et 31415) ; règle de génération des instrus de Marie et mesures d'intro dans le skill `generation-morceaux`.

### Modifié
- Pochettes sans texte : prompt par morceau (`cover_gen.py`, `cover_batch.py`), charte graphique supprimée.
- Skill de génération : passage obligatoire par les Tests, graine imposée ; mémoire projet : sens de « garde ».

## v1.10 — 2026-10-10

### Modifié
- Validation dans l'interface de Tests exigée pour les nouveaux contenus destinés à la WebRadio ; diffusion uniquement sur demande explicite.
- Paroles Funky Yogi et Marie classées sous `TEXTES/artistes/`, avec attribution et droits déclarés par l'utilisateur ; chemins des tests Marie mis à jour.
- Campagne comparative renseignée par les votes d'écoute ; essais temporaires « Soul du matin » et « Funky Yogi » retirés, original radio conservé.

## v1.9 — 2026-10-10

### Ajouté
- Section « Tests » en dossiers (nom lisible, nombre de versions, badge « jamais écoutés », dossiers à écouter en tête) ; clé `folder` optionnelle dans `playlist_results.json` (`tests_folder` dans `server.py`).
- Commentaire par version de test (`/api/tests/comment`, stocké dans `tests_state.json`, champ `comment` de `/api/tests`).

### Supprimé
- Bouton « Test » de l'UI d'écoute (HTML, CSS, JS).

## v1.8 — 2026-10-10

### Ajouté
- Campagne comparative de 30 générations musicales (ACE-Step 1.5, MusicGen Small, HeartMuLa OSS 3B), avec documentation, prompts, configurations, sidecars et résultats techniques accessibles dans l'UI de tests.

## v1.7 — 2026-10-09

### Ajouté
- UI : bouton de réinitialisation des pouces du morceau en cours (`/api/vote/reset`), volume des jingles réglable dans l'admin (`jingle_volume`), section « Tests » repliable (liste du plus récent au plus ancien, numéros uniques, pouces, suppression, barre de position, badge « Jamais écouté », routes `/api/tests*`), titre et date sur les pochettes, police Sora embarquée (`webradio/fonts/`).
- `TEXTES/tools/check_lyrics.py` : contrôle des paroles avant génération (balises, sections vides, syllabes, durée, cohérence avec le caption) ; section « Caption ACE » dans `/generate_lyrics` ; suivi des textes dans le skill `generation-morceaux`.
- Démo privée T01 « Arroser Les Roses » : versions numérotées de 1 à 44 dans la section Tests, version 18 retenue.

### Modifié
- `ace_worker.py` : graine appliquée (`use_random_seed=False`), les graines précédentes étaient ignorées.
- iOS : circuit Web Audio forcé pour que le volume des jingles et la baisse du morceau (12 %) s'appliquent ; `fit` de `motion.js` ne laisse plus un titre sortir du cadre ; `.gitignore` : démos privées et `tests_state.json`.

### Corrigé
- Suppression d'un test sous Windows quand le fichier est verrouillé ; contrôleur de paroles (BOM, syllabes en « -ent », « non instrumental »).

## v1.6 — 2026-10-08

### Ajouté
- Légende animée du visuel d'écoute : titre et description défilent en alternance (`listen.js`, `listen.css`), validée sur iPhone.
- Agents de zone `textes` et `modeles_llm` ; commande `/generate_lyrics` planifiée (paroles françaises, style en consigne interne).

## v1.5 — 2026-10-08

### Ajouté
- `webradio/ARCHITECTURE_WEBRADIO.md` section 8.3 bis : solution retenue pour une mise en ligne permanente (VPS Linux, systemd, HTTPS, sous-domaine du site, synchronisation des mp3), Vercel, Render gratuit et Netlify écartés.

### Modifié
- Batch de pochettes relancé dans un terminal cmd indépendant de VS Code (reprise des pochettes restantes).

## v1.4 — 2026-10-07

### Ajouté
- Série de tests de voix ACE-Step sur `TEXTES/Marie-1_ace.md` (`webradio/tests_ace/marie/`, v1 à v9) ; skill `generation-morceaux` ; bouton « Test » dans l'UI auditeur (playlist `tests-ace` hors catalogue) ; boutons « Mettre en file » dans le catalogue admin.

### Modifié
- UI du port 5000 devenue UI dev : boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin).
- `ace_worker.py` : `bpm`, `keyscale` et `timesignature` pris en paramètres de génération.

## v1.3 — 2026-10-07

### Ajouté
- Jingles rangés dans `webradio/jingles/<catégorie>/` (WebRadio, Traveling Sound, SérénIA Tech) : 5 jingles Traveling Sound et 5 jingles SérénIA Tech, mélangés aux jingles CréaZik ; admin avec catégories repliables, bouton de lecture et texte de chaque jingle.
- UI auditeur : cadre visuel unique centré, cycle de phases de 5 s (pochette, animations, pub de 9 s, animations, pochette) avec huit transitions animées ; pubs SérénIA Tech et Traveling Sound cliquables, pubs Traveling Sound à la charte du site.
- Dossier `TEXTES/` pour les textes de test de génération musicale.

### Modifié
- Voix des jingles : voix féminine Chatterbox (timbre de référence synthétique), plus lente, avec 1 s de silence en tête ; un jingle tous les 5 morceaux ; nom « CréaZik IA WebRadio » affiché partout, prononcé avec « IA » sur 5 jingles (à valider).
- Dynamique : boutons Slow/Medium/High réservés à l'admin (403 sinon), choix pris en compte à 100 % (poids 1) dans l'énergie du morceau.
- Mascotte masquée (fonction conservée), description sous Lecture/Suivant supprimée.

## v1.2 — 2026-10-06

### Ajouté
- Base SQLite `radio.db` (diffusions, « sans avis », avis Slow/Medium/High à un ou deux niveaux) et section Statistiques admin avec exports JSON et CSV.
- Catalogue admin fusionné avec l'explorateur : recherche, filtres, fiches, favoris, lecture, renommage, suppression avec archive d'apprentissage (`learning/morceaux_rejetes.jsonl`), commentaires ; tri des playlists par score, nom ou pondération ; score cumulé.
- UI auditeur : bouton « sans avis », dynamique Slow/Medium/High, carré de publicité cliquable avec mascotte à 20 styles, légende titre/style sans pochette, bouton Suivant public (phase de test).
- Fondu du morceau sous le jingle puis montée au maximum.

### Modifié
- Les morceaux à score négatif ne sont plus diffusés automatiquement.
- Jingles instrumentaux supprimés (20 jingles vocaux conservés) ; pochettes : titre et style plus grands, sans numéro.
- UI admin réorganisée (agent design), sections fermées par défaut avec état mémorisé ; bouton Explorateur retiré.

### Corrigé
- Bouton de dynamique qui ne restait pas allumé (serveur non redémarré) ; texte des boutons de pub qui dépassait.

## v1.1 — 2026-10-06

### Corrigé
- Pochettes : prompt en trois lignes explicites (titre, playlist, date) pour éviter le texte mélangé ou coupé.

## v1.0 — 2026-10-06

### Ajouté / modifié
- Interfaces auditeur et administration séparées ; programmation admin restaurée avec recherche par morceau et playlist.
- Libellés visibles harmonisés : préfixe « Playlist » retiré et anciennes playlists « Perso » renommées de façon descriptive.
- Processus de génération des pochettes reprenable ; état mis à jour après son interruption à la demande de l'utilisateur.
- Noms d'artistes conservés pendant le développement et à remplacer par des descriptions de genres avant déploiement.

### Décision
- La commande `/replace_downvoted_tracks` créée pendant la session a été supprimée à la demande de l'utilisateur ; elle ne fait pas partie des commandes du projet.

## v0.3 — 2026-10-06

### Ajouté
- `run.py` (lance serveur, analyse, compression, génération et ouvre l'UI) et commande `/stop` (arrêt de tout, VRAM libérée).

### Corrigé
- `services.ps1 stop` arrête aussi `run_rotation.py`.

## v0.2 — 2026-10-06

### Ajouté
- 11 playlists « Esprit » et blues (génération en rotation), `run.py` à la racine.
- Charte graphique par playlist (`webradio/covers_charte.json`, `tools/cover_gen.py`).

### Modifié
- Nom de la radio « CréaZik IA WebRadio » (UI et jingles vocaux, régénérés).
- Mise en queue sans couper (▶, « Lire »), Programmation lisible, noms de playlists sans « Playlist », bandeau « Aperçu auditeur » retiré.

## v0.1 — 2026-10-06

### Ajouté
- Dynamique de la journée (réglages, courbe, tests) et arc visuel narratif par morceau.
- Mode auditeur : texte et bandeau vers Traveling Sound Web Radio.
- Règles de génération et de développement (`webradio/REGLES_GENERATION_DEV.md`), branchées sur `/start` et `/close`.
- Test de pochette avec ComfyUI-Qwen (`webradio/tools/cover_test.py`).

### Modifié
- Audio : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
