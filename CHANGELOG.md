# Changelog

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
