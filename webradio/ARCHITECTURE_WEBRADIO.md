# Architecture WebRadio IA locale

Statut : proposition. Seuls la sécurité du serveur, les commentaires, la page admin et les jingles sont implémentés (section 7). Le reste est à valider avant développement.

## 1. Objectifs
- Radio 24/7 alimentée uniquement par des morceaux générés en local par plusieurs IA, sur la machine (RTX 4060 8 Go).
- Programmation intuitive : catégories, sous-catégories, playlists pondérées, jingles.
- Ajout facile de morceaux, avec choix de l'IA qui génère.
- Sobriété énergétique mesurée et assumée à l'antenne.
- Hébergement via un tunnel, avec un accès admin protégé.

## 2. Limite actuelle importante
Le "mix" actuel tourne dans le navigateur de chaque auditeur : chacun tire ses propres morceaux, ce n'est pas un flux unique. Pour une vraie radio (tous les auditeurs entendent la même chose au même moment), il faut un lecteur côté serveur qui produit un seul flux audio (voir 5.3). C'est la décision d'architecture la plus structurante.

## 3. Modèle de données (fichiers JSON, pas de base de données au départ)

### 3.1 Catalogue : `radio/catalog.json`
Un enregistrement par morceau, indexé par une clé stable `playlist:id` (déjà utilisée par les favoris et les exclusions).

| Champ | Rôle |
|---|---|
| `id` | clé stable |
| `title`, `file`, `duration` | affichage et lecture |
| `category`, `subcategory` | classement (3.2) |
| `tags` | étiquettes libres (ambiance, tempo, langue) |
| `vocal` | `instrumental` ou `vocal`, `language` |
| `provider`, `model`, `generated_at` | IA et date (déjà enregistrés pour les nouveaux morceaux) |
| `prompt`, `lyrics_file` | reproductibilité |
| `energy_wh`, `elapsed_s` | coût de génération (6) |
| `status` | `generated`, `failed`, `retired` |

### 3.2 Taxonomie : `radio/taxonomy.json`
Catégories et sous-catégories éditables depuis l'admin. Proposition de départ, à valider :
- Chanson française : jazz manouche, cabaret, folk, variété, chanson maritime, chanson narrative.
- Pop et rock : synthpop, pop-rock, rock, blues-rock, humoristique.
- Électronique : electro 80, electro 90, trance Goa, ambient, lo-fi, synthwave.
- Classique et sacré : piano solo, orchestral, chant grégorien, chorale.
- Monde et acoustique : musique du monde, percussions, celtique, flamenco, bossa nova.
- Cinéma et ambiance : musique de film, romantique, épique.

Un morceau a une catégorie et une sous-catégorie principales, plus des tags. Classement initial automatique à partir des prompts et noms de playlist, puis corrigeable à la main.

### 3.3 Playlists : `radio/playlists.json`
Deux types :
- **Intelligente** : une règle (catégorie, sous-catégories, tags, vocal ou instrumental, favoris, playlist générée). Elle se remplit toute seule quand de nouveaux morceaux arrivent.
- **Manuelle** : liste explicite de morceaux.

Chaque playlist a un `weight` (0 à 10), un statut actif, et un mode de lecture (aléatoire, ordre, anti-répétition propre).

### 3.4 Programmation : `radio/schedule.json`
Tranches horaires (par exemple matin, journée, soirée, nuit), chacune avec ses poids de playlists et sa fréquence de jingles. Une tranche "par défaut" couvre le reste.

### 3.5 Règle de tirage (hiérarchie des poids)
1. Tranche horaire active, puis playlist tirée selon son poids.
2. Morceau tiré dans la playlist (exclusions et anti-répétition appliquées).
3. Le poids actuel par playlist (ensemble de morceaux générés ensemble) devient un cas particulier de playlist intelligente, ce qui permet une migration sans perte.
4. Jingle inséré tous les N morceaux (déjà en place).

## 4. Composants

```
Navigateur auditeur (ui.html)        Navigateur admin (radio.html)
          |                                   |
          +----------- serveur web -----------+   auth, commentaires, API JSON
                            |
        +-------------------+----------------------+
        |                   |                      |
   Catalogue / playlists   File de jobs         Lecteur radio (playout)
   (fichiers JSON)         de génération        -> flux Icecast (5.3)
                                |
                    Fournisseurs d'IA locaux (4.1)
```

### 4.1 Fournisseurs d'IA (plugins)
Interface unique : `generate(demande) -> fichier audio + métadonnées + coût énergétique`. Un fichier par fournisseur dans `providers/`.
- Déjà fonctionnel : ACE-Step 1.5 (`ace_worker.py`).
- Candidats à tester avec la même playlist de test (à vérifier avant de promettre quoi que ce soit : compatibilité 8 Go de VRAM, licence, qualité) : MusicGen, Stable Audio Open, et des modèles de chant récents.
- Chaque fournisseur déclare : VRAM nécessaire, durée max, support des paroles, licence. Le planificateur refuse ce qui ne tient pas dans la carte.

### 4.2 File de jobs
- Un fichier de file : demande (fournisseur, prompt, paroles, durée, playlist cible, catégorie).
- Un seul job GPU à la fois, un processus par job (acquis des premières générations : évite les blocages de VRAM), temps limite et relance automatique (déjà dans `run_queue.py`).
- Fenêtres de génération configurables (par exemple la nuit ou quand la machine est libre).

### 4.3 Ajout de morceaux depuis l'admin
Un formulaire : choisir playlist ou catégorie, fournisseur, style, paroles (ou "inventer"), durée, nombre de variantes. Les morceaux générés arrivent en "à valider" : l'admin écoute, garde ou rejette. Seuls les morceaux validés entrent dans les playlists.

## 5. Radio

### 5.1 Écoute (client)
Lecteur actuel dans `ui.html` : suffisant pour un usage personnel.

### 5.2 Programmation (admin)
Page `radio.html` à faire évoluer : arbre catégories, playlists avec curseurs de poids, planning horaire, file de génération, validation des nouveaux morceaux.

### 5.3 Flux unique (proposition)
Un lecteur serveur (Liquidsoap, qui se pilote par script) lit playlists et jingles et pousse un flux vers Icecast ; les auditeurs ouvrent une seule URL de flux. Avantages : même contenu pour tous, reprise après coupure, métadonnées "en cours de lecture", compatible lecteurs et applis radio. Inconvénient : deux composants à installer et à sécuriser. À valider.

### 5.4 Dynamique de la journée
Le moteur (`radio_engine.py`) pondère le tirage de chaque morceau par un facteur de dynamique :
- Énergie visée selon l'heure de Paris : sinusoïde `dyn_base + dyn_amp * cos(2π (h - pic) / 24)`, pic à 17 h 30 (décalé d'une heure le week-end), creux la nuit. Réglable dans la page de gestion (section « Dynamique de la journée », avec courbe et énergie visée à l'instant).
- Énergie de chaque morceau : rang en percentile du catalogue sur rythme (onsets), brillance (centroïde), niveau (RMS) et tempo, mesurés par `analyze_viz.py` (`.feat.json`).
- Enchaînement des tempos : écart au morceau précédent, octaves tolérées (x2, /2).
- Chaque créneau de la file utilise l'heure à laquelle il sera joué.
Repères : Médiamétrie (écoute radio en France dominée par 6 h-9 h, second palier en fin d'après-midi) et études d'écoute en streaming (énergie en journée, calme tard le soir). Ces études montrent des écarts modestes : la courbe est une approximation réglable, pas une mesure.
Limites : le tempo estimé par autocorrélation est correct à 5 % pour 30 morceaux sur 45 (33 à l'octave près) ; ACE-Step ne suit pas toujours le tempo demandé.

## 6. Sobriété énergétique
- **Estimer** : le GPU de la machine n'expose pas sa puissance (`nvidia-smi` renvoie « N/A »). L'énergie par morceau est donc estimée d'après le taux d'utilisation et la puissance maximale de 115 W (champ `energy_wh_est`, `GET /api/energy`). Une vraie mesure demanderait une prise connectée. Aucun chiffre n'est annoncé tant qu'il n'est pas validé.
- **Réduire** : réutiliser le catalogue plutôt que générer en continu, utiliser les modèles et réglages légers (ACE-Step turbo, 8 pas), limiter la file, générer en heures creuses ou à la demande.
- **Afficher** : tableau de bord admin (Wh total, Wh par morceau, nombre d'écoutes par morceau, coût par écoute).

## 7. Jingles pédagogiques
Interprétation retenue : les jingles servent à expliquer à l'antenne comment la radio est faite (IA locale, sobriété). Deux niveaux :
1. **Jingles musicaux** de 5 secondes : 8 générés avec ACE-Step (fait).
2. **Jingles parlés** : un court texte lu par une voix de synthèse locale (par exemple Piper, à évaluer : voix française, légèreté, licence), avec des chiffres réels issus de la mesure (6) : par exemple nombre de morceaux, énergie totale, GPU utilisée. Les textes sont rédigés dans l'admin, jamais de chiffre inventé.

## 8. Sécurité et tunnel

### 8.1 Déjà appliqué dans `server.py`
- Écoute locale uniquement (127.0.0.1) : seul le tunnel, installé sur la même machine, peut atteindre le serveur.
- Liste blanche de fichiers servis : les configs, journaux, paroles, identifiants, scripts ne sont plus accessibles (testé : 404).
- Rôles : l'écoute, les commentaires et les favoris personnels sont publics ; la page Gestion WebRadio, les réglages et la modération sont réservés à l'admin.
- Mot de passe admin stocké haché (PBKDF2), cookie de session HttpOnly, SameSite=Strict, Secure derrière HTTPS, limite de 5 échecs par minute, vérification de l'origine sur les écritures, taille des requêtes limitée.
- Commentaires : texte nettoyé et échappé à l'affichage, 500 caractères maximum, 3 par minute et par adresse, suppression par l'admin.
- En-têtes : CSP stricte, nosniff, anti-framing, pas de referrer.

### 8.2 Risque connu à traiter
Le mot de passe admin est `admin` tant qu'il n'est pas changé (demande actuelle). Derrière un tunnel public, c'est devinable par n'importe qui avec le lien : la limite de tentatives ralentit mais n'empêche pas. À changer avant de partager le lien (champ dans la page admin).

### 8.3 Propositions pour le tunnel (à choisir selon l'usage)
| Option | Convient pour | Remarque |
|---|---|---|
| Tailscale (réseau privé, Funnel si besoin d'ouvrir) | usage perso, iPhone | aucun port public, accès limité à tes appareils |
| Cloudflare Tunnel + Cloudflare Access | radio publique avec admin protégé en plus | double authentification sur `/radio.html` et `/api/*` sans toucher au code |
| ngrok | tests rapides | URL changeante en offre gratuite, authentification à configurer |

Recommandation : Cloudflare Tunnel avec Access sur les chemins admin, ou Tailscale tant que la radio reste personnelle. Je n'ai pas vérifié les offres et limites actuelles de ces services : à confirmer avant de choisir.

### 8.3 bis Solution retenue pour une mise en ligne permanente (à réaliser plus tard)
Le serveur n'utilise que la bibliothèque standard Python et sert des fichiers déjà générés (874 mp3, 2,2 Go au 2026-10-08) : la génération (ACE, ComfyUI) n'est pas nécessaire pour l'écoute. Un VPS sans GPU suffit ; le PC ne sert qu'à générer.
1. VPS Linux d'entrée de gamme (1 Go de RAM, 20 à 40 Go de disque, Ubuntu), serveur Python lancé comme service `systemd`.
2. HTTPS via Caddy ou Cloudflare gratuit, sous-domaine `radio.serenia-tech.fr` (DNS chez OVH). Le site (Vercel + Render) ajoute un lien ou une page « Radio » ; un iframe exigerait de modifier la CSP `frame-src` et `X-Frame-Options` du site.
3. Synchronisation PC vers VPS des seuls nouveaux mp3 et pochettes (`rsync`/`scp`) ; les données vivantes (votes, `radio.db`, files) restent sur le serveur et ne sont pas écrasées.
4. Avant ouverture : retirer `DEV_UNIFIED`, le cadre admin, le bouton Test et la redirection `radio.html` ; changer le mot de passe admin ; revoir le mode Découverte et les pubs ; régler les droits de diffusion.
Coût estimé : VPS environ 3 à 6 € par mois (ordre de grandeur non vérifié, à confirmer chez Hetzner, OVH ou Scaleway) ; DNS/HTTPS gratuits. Écartés : Vercel et Render gratuits (pas de disque persistant), tunnel depuis le PC (radio coupée quand le PC s'arrête). Netlify (comme Vercel) écarté : fonctions serverless sans disque durable ni processus permanent, alors que la radio a besoin d'un état serveur partagé (rotation, `radio.db`, votes, commentaires, session admin) ; héberger les mp3 en statique imposerait de réécrire le moteur côté navigateur et de renoncer à l'état commun (limites de l'offre gratuite non vérifiées). Non testé : fonctionnement du serveur sous Linux.

### 8.4 Reste à faire
- Mot de passe admin fort ou clé d'accès ; second facteur via Cloudflare Access.
- Séparer le flux public (Icecast) du serveur d'administration, qui ne doit jamais exposer la génération IA.
- Sauvegarde des JSON (catalogue, playlists, commentaires).
- Journal d'audit des actions admin.
- Droits : aucun morceau n'est issu d'une œuvre protégée (paroles inventées). À conserver pour une diffusion publique.

## 9. Décisions à prendre
1. Flux unique serveur (5.3) ou lecteur navigateur ?
2. Taxonomie de départ (3.2) : la valider ou la corriger.
3. Choix du tunnel (8.3) et date de mise en ligne.
4. Autres IA à tester en premier (4.1).
5. Voix de synthèse pour les jingles parlés (7).
