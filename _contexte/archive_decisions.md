# Archive des décisions

- 2026-10-05 : Initialisation du protocole vibecoding.
- 2026-10-06 : Le projet devient une WebRadio IA locale ; règles consignées dans webradio/REGLES_GENERATION_DEV.md (chargé par /start, mis à jour par /close).
- 2026-10-06 : MP3 seul, WAV supprimé après conversion, analyse et contrôle de durée.
- 2026-10-06 : Pochettes via ComfyUI-Qwen, lancées quand la file de génération musicale est vide.
- 2026-10-06 : Pochettes avec texte généré par le modèle ; charte par playlist dans webradio/covers_charte.json.
- 2026-10-06 : Interfaces auditeur/admin séparées (ports 5000/5001) ; programmation admin avec recherche par morceau ou playlist.
- 2026-10-06 : Libellés publics sans préfixe « Playlist » ; libellés « Perso » remplacés par des noms descriptifs. Noms d'artistes conservés en développement et à remplacer avant déploiement.
- 2026-10-06 : Base SQLite `radio.db` pour diffusions, « sans avis » et dynamique perçue (fusionnée à l'énergie mesurée) ; statistiques admin avec exports JSON/CSV.
- 2026-10-06 : Suppression = fichiers effacés + archive dans `learning/morceaux_rejetes.jsonl` ; renommage via `catalog_overrides.json` ; score négatif = non diffusé automatiquement.

- 2026-10-06 : Panneau de pub carré cliquable avec mascotte (20 styles) ; jingles instrumentaux supprimés ; morceau en fondu sous le jingle.
- 2026-10-07 : Jingles rangés dans `webradio/jingles/<catégorie>/`, mélangés, 1 s de silence en tête, voix féminine Chatterbox.
- 2026-10-07 : Dynamique : seul l'admin saisit Slow/Medium/High et son choix remplace l'énergie mesurée ; mode dev à un seul utilisateur.
- 2026-10-07 : Tests de voix ACE hors catalogue (`playlists/tests-ace/`, bouton Test) ; BPM/tonalité en paramètres du worker ; un seul changement par version de test.
- 2026-10-07 : L'UI du port 5000 devient l'UI dev ; boutons Slow/Medium/High rouverts à tous (`/api/dynamics` sans contrôle admin), à refermer avec l'UI auditeur future.
- 2026-10-08 : Mise en ligne prévue sur VPS Linux bon marché (systemd, HTTPS, sous-domaine du site) ; Vercel, Render gratuit et Netlify écartés ; pas encore réalisée.
- 2026-10-08 : Deux agents de zone (`textes`, `modeles_llm`) pour travailler en parallèle ; nom d'artiste en consigne de style interne seulement, jamais public.
- 2026-10-09 : Section « Tests » dans l'UI admin (du plus récent au plus ancien, pouces, suppression, barre de position, repère « Jamais écouté », numéro unique par test) ; police Sora embarquée pour tous les titrages, pubs Traveling Sound en machine à écrire ; titre et date sur la pochette sans toucher l'image.
- 2026-10-09 : La graine ACE n'était pas appliquée (`use_random_seed` vrai par défaut) : corrigé dans `ace_worker.py` ; les essais « à graine fixe » antérieurs ne sont pas fiables ; paroles contrôlées par `check_lyrics.py` avant chaque lancement.
- 2026-10-09 : Démo privée T01 (Arroser Les Roses) : version 18 retenue, texte adapté (« posté », « zoublie »), voix de femme non retenue (instable), statut `VALIDE` interdit sans accord écrit de l'auteur ; lot de pochettes terminé, scores négatifs exclus.
- 2026-10-10 : campagne comparative de 30 extraits (10 ACE-Step 1.5, 10 MusicGen Small, 10 HeartMuLa OSS 3B) ; statuts techniques conservés séparément de l'écoute humaine, avec pistes invalides HeartMuLa laissées visibles pour examen.
