# Règles de génération et de développement - WebRadio CreaZik

Document établi à partir des décisions prises au fil des conversations. Chaque règle vient d'une demande de l'utilisateur ou d'une décision actée ; les points non tranchés sont listés à la fin.

## 1. Principes généraux

- Le projet est une WebRadio IA locale : tout est généré et servi depuis le PC de l'utilisateur (ACE-Step 1.5, RTX 4060 8 Go), exposé par un tunnel Cloudflare. Le client principal est l'iPhone (Safari).
- Vocabulaire : on parle de « playlists », jamais de « benchmarks ». Le dossier applicatif est `webradio/`.
- Les affirmations publiques (éthique, écologie, IA locale) doivent rester vérifiables.
- Les textes ou poèmes utilisés doivent être de vrais textes du domaine public ; ne jamais en inventer en les attribuant à un auteur.
- Le plan d'exécution est `PLAN_WEBRADIO.md`. La mise à jour des statuts de roadmap est faite par `/close`, pas en cours de session.
- Tout ce qui reste à contrôler à la main va dans `tests_manuels.md` ; la section est supprimée une fois le test validé.

## 2. Règles de génération musicale

### 2.1 Durée
- Durée cible d'un morceau : 90 s plus ou moins 45 s (`set_durations.py`, valeur déterministe par playlist et par morceau, jamais de ré-attribution sur un morceau déjà généré).
- Les paroles sont ajustées à la durée (`fit_lyrics` retire des sections) pour que le morceau se termine sans coupure sèche.

### 2.2 Paroles
- Morceaux vocaux : paroles en français, inventées si nécessaire. Exceptions : playlists dans une autre langue (disco anglais, groove anglais, poésie anglaise, disco en espagnol, portugais, italien, allemand).
- Lorsqu'une playlist est demandée en s'inspirant d'un chanteur, utiliser sa langue d'origine pour les paroles chantées (par exemple : anglais pour Michael Jackson).
- Les paroles importées par l'utilisateur (PDF « Paroles Meuniers Éveillés ») sont rangées dans les playlists « perso » ; les PDF source ne sont pas versionnés.
- Les playlists « perso » déclinent les mêmes morceaux en plusieurs styles (electro, folk, rock, classique, grégorien, chorale) et partagent un `song_group` pour ne pas se suivre de près.

### 2.3 Ordre et supervision de la génération
- Génération en rotation : un morceau par playlist, à tour de rôle (`run_rotation.py`), et non playlist par playlist.
- `series.txt` est relu à chaque tour, avec fins de ligne LF uniquement.
- Chaque piste est tentée 3 fois ; un délai maximal de `max(90 s, 3 x durée)` ; après 3 échecs, la piste est abandonnée et signalée dans les logs.
- Les statuts par piste dans `playlist_results.json` font foi : au redémarrage, les pistes déjà générées sont ignorées. La rotation n'est pas relancée par un superviseur permanent ; utiliser `/start_generation` et `/stop_generation` pour la gérer indépendamment des interfaces.
- Toute playlist doit être tentée dans toutes les catégories prévues ; l'objectif est que tout soit généré et accessible sur le téléphone.
- Chaque nouvelle playlist reçoit une configuration (`config.json`, paroles) et une entrée dans `scenes_spec.json` (motif visuel, teintes, vitesse, densité).
- Les playlists sont éclectiques et couvrent les styles musicaux du monde.

### 2.4 Format audio
- Seuls les MP3 (192 kbit/s) sont conservés et diffusés. Le moteur et l'explorateur lisent le MP3.
- À chaque génération, le WAV produit par le worker est converti, analysé (profil visuel et caractéristiques), contrôlé (durée du MP3 cohérente avec le WAV) puis supprimé (`compress_audio.py`).
- Seul `silence.wav` est conservé (déverrouillage audio sur iOS).
- Les fichiers de sortie ne sont jamais versionnés dans git.

### 2.5 Mesures et énergie
- La consommation de la carte est une estimation (`energy_wh_est`), car `nvidia-smi` ne donne pas la puissance ; elle est présentée comme telle.
- Les pochettes sont générées avec une IA locale (ComfyUI-Qwen, Qwen-Image 2.1) et uniquement lorsque la file de génération musicale est vide.
- Pochette : le texte (titre du morceau, nom de la playlist, date de création en plus petit) est généré dans l'image par le modèle, jamais incrusté après coup ; le prompt impose trois lignes explicites (titre, playlist, date), car une phrase unique fait mélanger les lignes au modèle. Une charte graphique par playlist est dans `webradio/covers_charte.json` (`tools/make_charte.py`), appliquée par `tools/cover_gen.py`.
- La génération en lot se lance avec `/generate_covers`, attend que la génération musicale soit inactive et reprend en ignorant les pochettes PNG déjà créées. `/stop_covers` arrête uniquement ce lot et ComfyUI-Qwen ; sans pochette disponible, l'interface conserve l'animation visuelle.
- Priorité des pochettes : relire les votes avant chaque image, générer d'abord les morceaux au solde positif, puis ceux sans vote, puis les soldes équilibrés ; exclure les soldes négatifs. Si le solde devient négatif pendant la génération, ne pas conserver l'image.

## 3. Règles de la radio (moteur)

### 3.1 Direct
- La radio est un direct partagé : cliquer sur play rejoint le morceau en cours, sans nouveau départ.
- Le moteur reprend le morceau en cours après un redémarrage du serveur.
- Aucun test de type « suivant » ou « lire maintenant » sur la radio en production.

### 3.2 Enchaînements
- Transitions réglables par préréglages en mode admin : fondu enchaîné, fondu, silence ; les fondus sont très doux.
- Jingle tous les N morceaux (valeur modifiable dans l'interface).
- Jamais deux fois le même morceau d'affilée ; un délai de 15 morceaux avant de rejouer une même chanson (`no_repeat_songs`).
- Une playlist dont le seul morceau jouable vient de passer n'est pas choisie.
- Publicité du site tous les 5 morceaux (motion design de 9 s).

### 3.3 Pondération et votes
- Chaque playlist a un poids : un poids 10 passe plus souvent qu'un poids 1.
- Les pouces haut et bas peuvent être cliqués autant de fois que souhaité ; chaque clic modifie le poids (environ 100 pouces bas pour qu'un morceau disparaisse).
- Commentaires associés au morceau en cours ; un commentaire au hasard est mis en avant toutes les 5 s.
- Favoris disponibles ; la réinitialisation des votes est dans la page de gestion.

### 3.4 Dynamique de la journée
- Énergie visée selon l'heure de Paris : sinusoïde, doux le matin, plus rythmé vers 17 h 30, décalage d'une heure le week-end, très calme la nuit.
- Énergie de chaque morceau mesurée sur l'audio (rythme, brillance, niveau, tempo) et classée par rapport au catalogue.
- Enchaînements harmonisés par tempo (octaves tolérées).
- C'est une approximation réglable (Médiamétrie et études d'écoute en streaming) ; les limites sont documentées.

### 3.5 Modes
- Mode auditeur : aucun changement de morceau possible ; bandeau Traveling Sound visible.
- Mode admin : programmation (lire à suivre, jouer maintenant, jingles, playlists) ; bascule par une icône en haut à droite, sans boutons dédiés ; passer en admin lance l'écoute de la radio.
- La page de gestion (`/radio.html`) et l'explorateur (`/ui.html`) sont réservés à l'admin ; les sections sont repliables.

## 4. Règles visuelles et sonores

- Un décor par playlist (plus de choix de style) ; transitions visuelles très douces entre playlists.
- Les visuels évoluent sur la durée du morceau (arc narratif : intensité en 5 temps, dérive de teinte, second motif, ondes ponctuelles), avec de l'aléatoire stable par morceau.
- Motion design pendant les jingles (nom de la radio et message sur l'IA locale) ; 10 designs de promotion du site, tirés du contenu de serenia-tech.fr.
- Jingles parlés sur l'IA locale comme alternative éthique et écoresponsable : voix Kokoro-82M (français), table de prononciation ; chaque jingle prononce le nom « Créa Zik IA WebRadio », contrôle d'intelligibilité par transcription.
- Design moderne et stylisé, lisible à 375 px, conçu pour le téléphone.

## 5. Règles de développement

### 5.1 Communication et conduite
- Réponses en français, ton professionnel, synthétique ; exécuter uniquement ce qui est demandé ; pas de commentaires inutiles dans le code ; pas d'emojis dans le code.
- Ne jamais affirmer qu'une chose fonctionne sans l'avoir vérifiée.
- Écrire les scripts à plusieurs lignes avec l'outil d'écriture de fichiers plutôt qu'avec des heredocs (problèmes de guillemets et d'antislash).

### 5.2 Services
- Après avoir arrêté un service radio (serveur, analyse ou compression), le relancer si nécessaire (`.\services.ps1 restart -Only serveur|analyse|compression`). Un arrêt volontaire de la génération musicale peut rester en place jusqu'à la prochaine session ; `/start_generation` la reprend.
- `services.ps1 stop -Only generation` arrête aussi `run_rotation.py` et ses workers sans supprimer les pistes déjà marquées `generated`. Ne pas faire tourner la génération musicale en même temps que ComfyUI pour les pochettes : ils se disputent le GPU.
- Ne pas redémarrer le serveur inutilement : cela coupe le morceau en cours des auditeurs.

### 5.3 Tests et livraison
- Chaque phase de développement inclut la création et l'exécution des tests pertinents avant d'être marquée faite.
- Les tests automatiques sont dans `tests/test_radio_engine.py` (18 tests) ; ils portent sur la continuité, les fondus, les poids, les votes, les répétitions, la dynamique, les statistiques, la reprise et le catalogue MP3.
- Un commit et un push après chaque phase de codage, message en français ; fichiers sensibles ou volumineux exclus.
- Les contrôles visuels se font dans le navigateur de test, puis sont à confirmer sur iPhone.

### 5.4 Sécurité
- Aucun secret en dur ; identifiants admin hachés (PBKDF2) hors git, mot de passe par défaut à changer.
- Liste blanche de fichiers statiques ; en-têtes de sécurité stricts (CSP) ; limitation de débit (connexion, commentaires, votes).
- Écritures admin : type JSON obligatoire et cookie SameSite=Strict.
- Les commentaires, votes, favoris, états et réglages utilisateur ne sont pas versionnés.

### 5.5 Noms d'artistes dans les titres publics
- Ne pas présenter l'usage d'un nom ou pseudonyme célèbre dans un titre de playlist comme garanti sans risque. Le contexte peut créer une impression d'affiliation ou d'association ; des droits de la personnalité et des droits de marque peuvent entrer en jeu.
- Pour les titres publics, préférer une formulation descriptive des genres, instruments ou périodes musicales, sans nom, photographie ni logo d'artiste. Si un nom d'artiste doit être conservé pour un usage public ou commercial, faire vérifier le cas précis par un conseil en propriété intellectuelle ; la mention « esprit de » ou « inspiré par » ne constitue pas à elle seule une garantie juridique.

## 6. Points non tranchés ou à valider

- Validation par l'utilisateur des textes des jingles parlés.
- Changement du mot de passe admin par défaut.
- Rythme de génération du lot de pochettes ; fiabilité du texte des pochettes (prompt en trois lignes testé sur 2 essais seulement).
- Comportements iPhone non vérifiés : fondus audio, lecture automatique après connexion, écran verrouillé.
