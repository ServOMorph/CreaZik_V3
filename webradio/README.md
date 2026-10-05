# CreaZik WebRadio

Radio en direct dont tous les morceaux sont générés en local par IA (ACE-Step 1.5 sur le GPU de la machine). Le serveur Python programme la radio, les navigateurs jouent le direct.

## Démarrage

```powershell
.\services.ps1 status            # état des 4 services
.\services.ps1 start             # démarre ceux qui sont arrêtés
.\services.ps1 restart -Only serveur
.\services.ps1 stop              # pensez à relancer ensuite avec start
```

Services : `serveur` (page et moteur de radio, port 5000, écoute locale), `generation` (rotation ACE-Step), `analyse` (profils sonores pour l'animation), `compression` (MP3 pour le web). Le moteur reprend le morceau en cours après un redémarrage du serveur.

Pages : `/` écoute (auditeurs et admin), `/radio.html` gestion (admin, connexion sur `/login`), `/ui.html` explorateur de playlists.

## Organisation

| Élément | Rôle |
|---|---|
| `playlists/<id>/config.json` | morceaux à générer (prompt, type, durée, paroles) |
| `playlists/<id>/lyrics/` | paroles (inventées) |
| `playlists/<id>/outputs/` | WAV, MP3, profils sonores, `playlist_results.json` (non versionnés) |
| `playlists.json` | registre des playlists (libellé, description, rôle jingle) |
| `scenes_spec.json` | fiche de style visuelle de chaque playlist |
| `radio_content.json` | textes des jingles et des publicités |
| `radio_settings.json` | réglages de la radio (poids, jingles, transitions, publicités) |
| `radio_engine.py` | moteur de radio en direct (tirage, jingles, transitions, publicités) |
| `server.py` | serveur web, rôles, API |
| `run_rotation.py`, `run_queue.py`, `generate.py`, `ace_worker.py` | génération supervisée |
| `listen.html/css/js`, `scenes.js`, `transitions.js`, `motion.js` | page d'écoute et visuels |

## Ajouter une playlist (procédure)

1. Créer `playlists/<id>/config.json` (modèle : une playlist existante). Durée tirée autour de 90 s plus ou moins 45 s : lancer `python set_durations.py`.
2. Si vocale : écrire des paroles inventées dans `lyrics/` (jamais de paroles protégées).
3. Déclarer la playlist dans `playlists.json` (libellé et description sans nom d'artiste).
4. Ajouter son identifiant dans `series.txt` (la rotation le relit à chaque tour).
5. Ajouter sa fiche de style dans `scenes_spec.json` : motif, deux teintes, vitesse, densité (un visuel inédit est généré automatiquement si la fiche manque, mais il faut en créer une soigneusement).
6. Si la playlist regroupe des versions des mêmes chansons, ajouter `"song_group"` dans sa configuration (délai entre versions d'une même chanson).

## Données de la radio

- Direct : `GET /api/radio/state` (public), actions admin `POST /api/radio/action`.
- Réglages : `POST /api/radio` (admin). Statistiques de passage : `GET /api/radio/stats` (admin). Énergie de génération mesurée : `GET /api/energy`.
- Pouces : `POST /api/vote` (chaque clic compte). Commentaires : `GET/POST /api/comments` (filtre `?key=` par morceau).

## Tests

```powershell
python tests/test_radio_engine.py     # moteur de radio (14 tests)
```

## Sécurité

Écoute sur `127.0.0.1` uniquement (tunnel installé sur la machine). Seuls l'interface, les résultats et les fichiers audio sont servis. Mot de passe admin à changer dans la page de gestion (défaut `admin`). Détails et pistes dans `ARCHITECTURE_WEBRADIO.md`.
