# Règles de génération et de développement - WebRadio CreaZik

Document établi à partir des décisions prises au fil des conversations. Chaque règle vient d'une demande de l'utilisateur ou d'une décision actée ; les points non tranchés sont listés à la fin.

## 1. Principes généraux

- Le projet est une WebRadio IA locale : tout est généré et servi depuis le PC de l'utilisateur (ACE-Step 1.5, RTX 4060 8 Go), exposé par un tunnel Cloudflare. Le client principal est l'iPhone (Safari).
- Vocabulaire : on parle de « playlists », jamais de « benchmarks ». Le dossier applicatif est `webradio/`.
- Les affirmations publiques (éthique, écologie, IA locale) doivent rester vérifiables.
- Paroles françaises : un nom d'artiste cité pour imiter un style ne sert que de consigne d'écriture interne ; ne jamais recopier ou paraphraser de près des paroles existantes, ne pas attribuer le texte à l'artiste, ne pas le faire figurer dans un titre, un caption ou un affichage public.
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
- Pochette : une image différente par morceau, sans aucun texte (ni titre, ni playlist, ni date), générée par `tools/cover_gen.py` à partir du titre et du prompt musical du morceau avec une graine propre au morceau. Plus de charte graphique par playlist.
- Les playlists dont l'identifiant commence par `esprit-` ou dont le libellé commence par « Esprit » sont exclues de la génération des pochettes jusqu'au remplacement de ces références par des styles descriptifs.
- La génération en lot se lance avec `/generate_covers`, attend que la génération musicale soit inactive et reprend en ignorant les pochettes PNG déjà créées. `/stop_covers` arrête uniquement ce lot et ComfyUI-Qwen ; sans pochette disponible, l'interface conserve l'animation visuelle.
- Priorité des pochettes : relire les votes avant chaque image, générer d'abord les morceaux au solde positif, puis ceux sans vote, puis les soldes équilibrés ; exclure les soldes négatifs. Si le solde devient négatif pendant la génération, ne pas conserver l'image.

### 2.6 Tests de génération (versions d'essai)
- Tout nouveau fichier de test ou contenu généré destiné à la WebRadio passe d'abord par l'interface de Tests et la validation de l'utilisateur. Inclure le fichier de référence si la génération part d'un contenu existant. Pour un format non pris en charge par cette interface, établir un moyen de validation avant publication. Aucun ajout aux playlists diffusées ni à la rotation sans demande explicite de l'utilisateur, même après validation. Cette règle prime les consignes de génération automatique pour les nouvelles créations.
- Les tests vivent dans `webradio/tests_ace/<sujet>/` (hors playlists, rotation et radio), une version par worker (`generate.py --only <id>`), une seule variable modifiée à la fois, avec contrôle des paroles par `TEXTES/tools/check_lyrics.py` avant le lancement. Les résultats à écouter sont copiés dans `playlists/tests-ace/outputs/` (section Tests de l'UI) ; seuls les MP3 sont gardés (le WAV du dossier de test et sa source dans `ACE-Step-1.5\output\creazik\` sont supprimés).
- La graine du cas de test est appliquée depuis le 2026-10-09 (`use_random_seed=False` dans `ace_worker.py`) : avant, `use_random_seed` valait vrai par défaut et toutes les graines des tests (« seed 42 », etc.) étaient ignorées, donc les comparaisons « à graine fixe » plus anciennes ne sont pas fiables. Une même graine redonne un audio presque identique (corrélation 0,99997, pas bit à bit). Aucune configuration de playlist ne définit de graine : la rotation reste aléatoire.
- Surveiller dans le journal la ligne `auto-enabling CPU VAE decode` : si la VRAM libre avant le décodage tombe à environ 0 Go (navigateurs, bureau), le décodage passe sur processeur et peut durer des heures. Fermer ou arrêter les consommateurs de VRAM avant de lancer.
- Graine toujours explicite (>= 0) pour un test : avec `-1`, ACE tire une graine non relevée et le morceau n'est pas reproductible. Chaque génération de `ace_worker.py` écrit un sidecar `.metadata.json` (prompt, paroles, paramètres, versions, `sha256`, durée) et un `generation_manifest.json` dans le dossier de sortie ; le nom du WAV porte l'horodatage et la graine. Pour un cas instrumental, un champ `lyrics` (balises de section) est transmis à ACE.
- Instrus de Marie (rap mélodique minimal, piano, violon) : 5 graines sans autre changement, tri à l'écoute dans les Tests, les retenus vont dans `TEXTES/artistes/Marie/tops_instrus/` ; l'entrée du beat n'est pas pilotable (14 à 30 s mesurées selon graine et tempo). Détail dans le skill `generation-morceaux`.
- Texte protégé (`TEXTES/usage_prive/`, ex. T01 « Arroser Les Roses ») : démo privée seulement, dossier de test non versionné, jamais en playlist ni en rotation ; un test d'écoute ne vaut pas accord de l'auteur : le statut `VALIDE` reste interdit tant que l'accord écrit n'existe pas. Toute adaptation du texte (ex. « posté », « zoublie ») est à signaler à l'auteur.

## 3. Règles de la radio (moteur)

### 3.1 Direct
- La radio est un direct partagé : cliquer sur play rejoint le morceau en cours, sans nouveau départ.
- Le moteur reprend le morceau en cours après un redémarrage du serveur.
- Aucun test de type « suivant » ou « lire maintenant » sur la radio en production.

### 3.2 Enchaînements
- Jingle vers morceau : le morceau démarre en même temps que le jingle, en fondu à volume bas (12 %, `DUCK_LEVEL`) pendant la voix, puis le volume monte jusqu'au maximum sur 3 s après la fin du jingle (`DUCK_RISE_S`). Le volume des jingles est réglable dans l'admin (`jingle_volume`, 0,8 par défaut) et appliqué aussi à la prévisualisation. Sur iPhone, Safari ignore `el.volume` : le client force le circuit Web Audio (GainNode) sur iOS pour que le volume des jingles et la baisse du morceau soient appliqués.
- Seuls les jingles vocaux sont conservés ; ils sont rangés hors des playlists, dans `webradio/jingles/<catégorie>/` (`webradio` : CréaZik IA WebRadio, `traveling-sound`, `serenia-tech`), déclarés dans `playlists.json` avec `role: jingle` et `category`. Toutes les catégories sont mélangées dans la même rotation ; l'admin les trie par catégorie (blocs repliables).
- Chaque jingle commence par 1 s de silence (le début était coupé) et reçoit le même traitement de volume (compression, loudnorm -11 LUFS).
- Transitions réglables par préréglages en mode admin : fondu enchaîné, fondu, silence ; les fondus sont très doux.
- Jingle tous les N morceaux (valeur modifiable dans l'interface ; réglée à 5).
- Jamais deux fois le même morceau d'affilée ; un délai de 15 morceaux avant de rejouer une même chanson (`no_repeat_songs`).
- Une playlist dont le seul morceau jouable vient de passer n'est pas choisie.
- Publicité du site tous les 5 morceaux (motion design de 9 s).

### 3.3 Pondération et votes
- Chaque playlist a un poids : un poids 10 passe plus souvent qu'un poids 1.
- Les pouces haut et bas peuvent être cliqués autant de fois que souhaité ; chaque clic modifie le poids ; un morceau dont le score (haut moins bas) est négatif n'est plus diffusé automatiquement (il reste programmable à la main par l'admin).
- Commentaires associés au morceau en cours ; un commentaire au hasard est mis en avant toutes les 5 s.
- Un bouton de réinitialisation, entre les pouces, remet à zéro les pouces du morceau en cours uniquement (`/api/vote/reset`, désactivé sans pouce). Il n'y a plus de bouton « sans avis ».
- Favoris disponibles ; la réinitialisation globale des votes est dans la page de gestion.

### 3.4 Dynamique de la journée
- Énergie visée selon l'heure de Paris : sinusoïde, doux le matin, plus rythmé vers 17 h 30, décalage d'une heure le week-end, très calme la nuit.
- Énergie de chaque morceau mesurée sur l'audio (rythme, brillance, niveau, tempo) et classée par rapport au catalogue.
- Enchaînements harmonisés par tempo (octaves tolérées).
- En mode développement (un seul utilisateur : le développeur), seul l'admin voit et peut envoyer les boutons Slow / Medium / High (le serveur refuse les autres avec 403) ; son choix remplace entièrement l'énergie mesurée du morceau (`dyn_user_weight` = 1 par défaut, sans dilution selon le nombre d'avis).
- C'est une approximation réglable (Médiamétrie et études d'écoute en streaming) ; les limites sont documentées.

### 3.5 Modes
- Mode auditeur : aucun changement de morceau possible ; bandeau Traveling Sound visible.
- Mode admin : programmation (lire à suivre, jouer maintenant, jingles, playlists) ; bascule par une icône en haut à droite, sans boutons dédiés ; passer en admin lance l'écoute de la radio.
- La page de gestion (`/radio.html`) et l'explorateur (`/ui.html`) sont réservés à l'admin ; les sections sont repliables.

### 3.6 Base de données, avis et suppression
- `radio.db` (SQLite, non versionnée) enregistre chaque diffusion de morceau (horodatage, durée écoutée, passage forcé), les marqueurs « écouté, sans avis » (conservés en base, plus de bouton dans l'UI), les avis de dynamique Slow / Medium / High et l'historique des votes.
- L'UI du port 5000 est l'UI dev : Suivant et Slow/Medium/High y sont ouverts (le bouton « Test » public est supprimé) à tous ; `/api/dynamics` n'exige plus l'admin. Une UI auditeur sera créée plus tard et devra refermer ces accès.
- Les avis Slow/Medium/High (0,15 / 0,5 / 0,85) sont fusionnés avec l'énergie mesurée dans la dynamique de la journée ; poids réglable (`dyn_user_weight`), croissant avec le nombre d'avis.
- La section admin « Statistiques » expose les indicateurs, constats automatiques, tableaux triables et exports JSON (avec dictionnaire des champs) et CSV pour analyse humaine et IA.
- Suppression d'un morceau ou d'une playlist : le MP3, la pochette et les fichiers dérivés sont effacés, l'entrée est masquée via `catalog_overrides.json` (le statut « generated » est conservé pour que la rotation ne le régénère pas) et les données de création (prompt, paroles, modèle, caractéristiques, votes, motif) sont ajoutées à `learning/morceaux_rejetes.jsonl`, corpus de ce qu'il ne faut pas reproduire. Refusé si le morceau est en cours de diffusion. Le renommage passe aussi par `catalog_overrides.json`.
- Phase de test : le bouton « Suivant » est public (`PUBLIC_SKIP`) ; à retirer avant le déploiement (voir `AMELIORATIONS.md`).

### 3.7 Section Tests de l'UI (admin)
- Les sections « Gestion WebRadio » et « Tests » de la page d'écoute sont repliables et visibles dès que l'admin est connecté (même en « voir comme auditeur »). « Tests » liste les versions de `webradio/playlists/tests-ace/outputs/playlist_results.json` (hors catalogue, jamais diffusées), du plus récent au plus ancien : lecture, pouces haut/bas, suppression avec confirmation, barre de position.
- Routes réservées à l'admin : `GET /api/tests`, `POST /api/tests/vote`, `/api/tests/played`, `/api/tests/delete`. L'état (pouces, « écouté », fichiers à supprimer plus tard si Windows les verrouille) est dans `webradio/tests_state.json`, non versionné. Une version jamais lancée porte le badge « Jamais écouté » ; il disparaît au premier clic sur lecture.
- La section affiche d'abord des dossiers (nom lisible, nombre de versions, badge « N jamais écoutés », dossiers à écouter en tête), puis les versions du dossier ouvert. Le dossier vient du serveur (`tests_folder` dans `server.py`) : clé `folder` de l'entrée de `playlist_results.json` si elle existe, sinon un dossier par modèle pour `tests-modeles`, sinon des règles sur le nom pour `tests-ace` (Marie, Lagniel, Grille 135 s, Grille 60 s, sinon « ACE · Divers »). Chaque item expose `folder` et `folder_label`.
- Commentaire par version : `POST /api/tests/comment` (admin, 2000 caractères), stocké sous `comments` dans `webradio/tests_state.json` et renvoyé dans le champ `comment` de `/api/tests` ; conservé après suppression de la version, pour l'analyse des résultats.
- Chaque test a un numéro unique en tête du nom (`NN · description`), jamais réutilisé ; le suivant est le plus grand numéro existant plus un (45 au 2026-10-09). Seul le nom affiché change : les fichiers gardent leur nom.
- Les MP3 de cette section sont servis par les motifs statiques publics de `playlists/*/outputs/` : lisibles sans connexion pour qui connaît l'URL (voir points non tranchés).

## 4. Règles visuelles et sonores

- Un décor par playlist (plus de choix de style) ; transitions visuelles très douces entre playlists.
- Les visuels évoluent sur la durée du morceau (arc narratif : intensité en 5 temps, dérive de teinte, second motif, ondes ponctuelles), avec de l'aléatoire stable par morceau.
- Le cadre visuel est unique et centré ; il enchaîne des phases de 5 s : pochette (si disponible), animations visuelles, publicité (9 s), animations visuelles, pochette, avec huit transitions animées (`PHASE_FX` dans `listen.js`). La mascotte (`mascot.js`) est conservée mais masquée. La légende du visuel (titre, description) défile verticalement en alternance toutes les 3,5 s.
- Titrage sur la pochette : le titre du morceau est centré en haut de l'image et la date de génération en petit en bas à droite, sans modifier le fichier de la pochette. La zone est calculée sur l'image réellement affichée (carrée, centrée) et non sur le cadre ; le titre reste sur une ligne en réduisant la police (jusqu'à 9 px), sinon coupé au « - », sinon sur plusieurs lignes entre les mots (`fitCoverTitle` dans `listen.js`). Les titres dessinés sur canvas (pubs, jingles) passent par `fit` de `motion.js`, qui réduit la taille puis coupe avec « … » plutôt que de déborder.
- Police des titres : Sora (SIL OFL, fichier embarqué `webradio/fonts/Sora-latin.woff2`, aucune requête externe), pour tous les titrages de l'UI et des pubs SérénIA Tech et CréaZik. Les pubs Traveling Sound gardent la machine à écrire de leur charte.
- Publicités (`radio_content.json`) : SérénIA Tech (clic vers serenia-tech.fr), Traveling Sound (5 pubs tirées des textes des jingles, charte du site : fond sombre, vert jungle et orange, crème, police machine à écrire, clic vers son site), messages CréaZik IA WebRadio (sans clic) ; rotation par groupes.
- Jingles parlés : voix féminine suave et lente générée par Chatterbox multilingue (CPU) avec un timbre de référence synthétique (Kokoro `ff_siwis`), `exaggeration` 0,4 et `cfg_weight` 0,1 ; le nom s'affiche « CréaZik IA WebRadio » et se prononce avec « IA » (« Créa Zique, I A, Ouèbe Radio ») ; « Traveling Sound Ouèbe Radio » et « Sérénia Tèk » pour les pubs ; contrôle d'intelligibilité par transcription (Whisper-small).
- Design moderne et stylisé, lisible à 375 px, conçu pour le téléphone.

## 5. Règles de développement

### 5.1 Communication et conduite
- Réponses en français, ton professionnel, synthétique ; exécuter uniquement ce qui est demandé ; pas de commentaires inutiles dans le code ; pas d'emojis dans le code.
- Ne jamais affirmer qu'une chose fonctionne sans l'avoir vérifiée.
- Écrire les scripts à plusieurs lignes avec l'outil d'écriture de fichiers plutôt qu'avec des heredocs (problèmes de guillemets et d'antislash).

### 5.2 Services
- Après avoir arrêté un service radio (serveur, analyse ou compression), le relancer si nécessaire (`.\services.ps1 restart -Only serveur|analyse|compression`). Un arrêt volontaire de la génération musicale peut rester en place jusqu'à la prochaine session ; `/start_generation` la reprend.
- `services.ps1 stop -Only generation` arrête aussi `run_rotation.py` et ses workers sans supprimer les pistes déjà marquées `generated`. Ne pas faire tourner la génération musicale en même temps que ComfyUI pour les pochettes : ils se disputent le GPU.
- Ne pas redémarrer le serveur inutilement : cela coupe le morceau en cours des auditeurs. Une modification de code Python (serveur, moteur, base) n'est prise en compte qu'après `.\services.ps1 restart -Only serveur` : sans cela, les nouvelles routes répondent 404 et l'UI annule l'action.

### 5.3 Tests et livraison
- Chaque phase de développement inclut la création et l'exécution des tests pertinents avant d'être marquée faite.
- Les tests automatiques sont dans `tests/test_radio_engine.py` (27 tests au dernier passage, début de session du 2026-10-08) ; ils portent sur la continuité, les fondus (dont le fondu sous jingle), les poids, les votes et le score négatif, les répétitions, la dynamique (dont les avis Slow/Medium/High), les statistiques et la base `radio.db`, le catalogue éditable, la reprise et le catalogue MP3.
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

- Validation à l'écoute de la prononciation de « IA » dans les jingles 1 à 5 de la catégorie WebRadio (Whisper entend « il y a ») ; si validée, régénérer les 14 autres ; textes des jingles SérénIA Tech non validés.
- Changement du mot de passe admin par défaut.
- Rythme de génération du lot de pochettes ; fiabilité du texte des pochettes (prompt en trois lignes, titre et style plus grands, non testé sur un lot).
- Comportements iPhone non vérifiés : fondus audio dont le fondu sous jingle, lecture automatique après connexion, écran verrouillé, cycle visuel, transitions et clics sur les pubs.
- Bouton « Suivant » public et exposition des boutons Renommer/Supprimer : à retirer ou verrouiller avant le déploiement.
- Réorganisation de l'UI admin : propositions de l'agent design (barre d'accès rapide, onglets) en attente de choix ; sort de `ui.html`.
- Les suppressions de playlists ne retirent pas leurs identifiants de `series.txt` : la rotation peut les régénérer.
- Génération ACE : le timbre de voix n'est pas constant sur un morceau (même sur 40 s). Voix de femme sur la démo T01 : instable sur les tests 11, 13 (duo homme/femme inopérant), 14, 15 et 19 (la 15, tirage aléatoire, était la meilleure selon l'écoute). Les tests « seed » du test Marie (v7 à v9) ne concluent rien : les graines n'étaient pas appliquées. Grille avec graines appliquées à écouter : tests 26 à 31 (135 s) et 39 à 44 (60 s, texte corrigé). Une cause de blocage du décodage est la VRAM libre insuffisante, pas la durée seule.
- Voix de femme, pistes de recherche non testées : durée courte, « female vocal » en fin de caption, modèles Base ou XL Turbo (non installés ; Turbo seul).
- Démo T01 (Arroser Les Roses, Jean-Marc Lagniel) : version 18 retenue par l'utilisateur (voix d'homme, silences `[Silence]` avant chaque « Arroser les roses », texte adapté « posté » et « zoublie ») ; accord de l'auteur non demandé.
- Avant le déploiement : `DEV_UNIFIED = True` est écrit en dur dans `server.py` (pages admin et connexion atteignables, CSP assoupli) ; les MP3 et résultats de `playlists/tests-ace/` sont lisibles sans connexion par les motifs statiques publics ; la section Tests et ses routes sont à retirer ou verrouiller.
- À confirmer : seuil `total <= h * 0.688` dans `jlayout` de `motion.js` (introduit hors de cette session, probable faute de frappe) ; suppression du formulaire de commentaires et masquage du bloc « musique humaine » et du contact dans `listen.html` (présente dans le répertoire de travail, non faite pendant cette session).
- Mise en ligne permanente : VPS Linux retenu mais non réalisé ; fonctionnement du serveur sous Linux non testé (voir `ARCHITECTURE_WEBRADIO.md` 8.3 bis).
- Agents de zone `textes` (paroles françaises, commande `/generate_lyrics` créée, avec contrôle `TEXTES/tools/check_lyrics.py` ; grille rimes, répétitions, clichés à compléter) et `modeles_llm` en parallèle : tests GPU à faire à tour de rôle sur la RTX 4060 8 Go.
- Les services `analyse` et `compression` sont arrêtés (comme `generation`) à la fin de la session du 2026-10-09 : les relancer avant la prochaine génération de morceaux.
- Pochettes sans texte (prompt par morceau, graine propre) et traçabilité d'`ace_worker.py` : modifiées, non testées en conditions réelles (pochette sur une playlist, reprise d'une piste déjà générée avec le nom horodaté, compatibilité avec `compress_audio.py` et la suppression).
- Protocole d'apprentissage non câblé : `learning/morceaux_rejetes.jsonl` n'est lu par aucune génération.
- Graine effective non relevée quand `seed` vaut `-1` (rotation).
