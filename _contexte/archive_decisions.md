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
