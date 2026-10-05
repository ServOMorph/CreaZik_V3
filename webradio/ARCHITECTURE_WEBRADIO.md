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

## 6. Sobriété énergétique
- **Mesurer** : échantillonner la puissance du GPU pendant chaque génération (`nvidia-smi`) et enregistrer l'énergie (Wh) par morceau. Aucun chiffre n'est annoncé sans cette mesure.
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
