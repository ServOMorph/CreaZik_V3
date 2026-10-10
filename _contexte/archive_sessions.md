# Session du 2026-10-06 (précédente, première moitié)

## Décisions prises
- Garder les noms d'artistes pendant le développement ; les remplacer par des genres descriptifs avant le déploiement.
- Retirer « Playlist » des titres affichés et remplacer les libellés « Perso » par des intitulés descriptifs.
- À la demande de l'utilisateur, arrêter tous les services et processus WebRadio et ComfyUI ; laisser le tunnel Cloudflare et les applications d'autres projets intacts.

## Livrables produits ou modifiés
- `webradio/tools/cover_gen.py` : prompt de pochette en trois lignes + négatifs renforcés (commité à la clôture).
- `webradio/radio.html` : programmation admin restaurée avec ajout de morceaux/playlists et recherche.
- `webradio/playlists.json` : 88 libellés harmonisés, sans préfixe « Playlist » ni « Perso ».
- `webradio/REGLES_GENERATION_DEV.md`, `AMELIORATIONS.md` : précaution juridique et remplacement des noms d'artistes prévu avant déploiement.
- Génération des pochettes interrompue proprement dans son état de reprise : 107 images créées, 804 manquantes au dernier statut.
- `.claude/commands/replace_downvoted_tracks.md` créé puis supprimé à la demande de l'utilisateur.

## Hypothèses validées / invalidées
- VALIDE : prompt de pochette en trois lignes explicites (titre, playlist, date) : texte correct sur 2 essais (flamenco, médiéval).
- VALIDE : services WebRadio à l'arrêt, port ComfyUI 8189 fermé, 1714 MiB de VRAM utilisés (applications Windows).
- EN ATTENTE : reprise des pochettes ; contrôles manuels iPhone et jingles ; renommage des titres d'artistes avant le déploiement.

## Prochaine étape exacte
Relancer `/generate_covers` pour reprendre les pochettes manquantes.

---

# Session du 2026-10-07

## Décisions prises
- Jingles : voix féminine Chatterbox (timbre synthétique), 1 s de silence en tête, rangés dans `webradio/jingles/` par catégorie (WebRadio, Traveling Sound, SérénIA Tech), mélangés, un tous les 5 morceaux.
- UI auditeur : cadre visuel unique centré, cycle de phases de 5 s (pochette, animations, pub 9 s, animations, pochette) avec transitions animées ; mascotte masquée ; pubs SérénIA Tech et Traveling Sound cliquables, charte Traveling Sound.
- Dynamique : boutons Slow/Medium/High réservés à l'admin ; le choix du développeur remplace l'énergie mesurée (poids 1).
- Nom affiché « CréaZik IA WebRadio » partout ; la voix dit « IA » (test sur 5 jingles).

## Livrables produits ou modifiés
- `webradio/jingles/`, `playlists.json`, `radio_engine.py`, `server.py` : jingles hors playlists, catégories, route statique `/jingles/`, dynamique admin.
- `webradio/radio.html` : jingles par catégories repliables, lecture et texte des jingles, libellé du poids de dynamique.
- `webradio/listen.html`, `listen.css`, `listen.js`, `motion.js`, `radio_content.json` : cycle visuel, transitions, pubs et charte.
- `TEXTES/`, `.claude/memory.md` : dossier de textes de test ; mémoire « mode dev ».

## Hypothèses validées / invalidées
- VALIDE : 25 tests du moteur passent ; serveur redémarré, mp3 des 3 catégories servis (HTTP 200) ; catalogue de 29 jingles chargé ; rendu des pubs Traveling Sound validé par l'utilisateur.
- INVALIDE : la transcription Whisper n'a pas pu confirmer « IA » (elle écrit « il y a ») : à trancher à l'écoute.
- EN ATTENTE : écoute des jingles 1 à 5 « IA » et des jingles SérénIA Tech ; contrôles iPhone ; affichage réel des catégories repliables dans l'admin.

## Prochaine étape exacte
Écouter les jingles 1 à 5 dans l'admin, trancher la prononciation de « IA », puis régénérer les 14 autres si elle convient.

## Question bloquante pour la session suivante
La prononciation « I A » des jingles WebRadio convient-elle ?

---

# Session du 2026-10-08 (légende animée, cadrage des paroles)

## Décisions prises
- Légende du visuel (titre / description) : défilement vertical alterné toutes les 3,5 s, validé sur iPhone par l'utilisateur.
- Travail en parallèle réparti en deux agents de zone : `textes` (paroles françaises, commande `/generate_lyrics` à créer) et `modeles_llm` (autres modèles musicaux).
- Paroles : le nom d'artiste ne sert que de consigne de style interne, jamais dans un titre, un caption ou une attribution publics.

## Livrables produits ou modifiés
- `webradio/listen.js`, `webradio/listen.css` : légende animée (`setCaption`, `startCaptionTyping`) ; première version en frappe remplacée par le défilement.
- `webradio/REGLES_GENERATION_DEV.md` : règle de légende et cadrage des paroles.

## Hypothèses validées / invalidées
- VALIDE : défilement de la légende correct sur iPhone (contrôle utilisateur).
- EN ATTENTE : qualité réelle des paroles produites par la future commande, à juger à l'écoute.

## Prochaine étape exacte
Lancer `/start textes` dans une session dédiée et créer `/generate_lyrics` ; écouter v7 à v9 des tests ACE si ce n'est pas fait.

## Question bloquante pour la session suivante
Aucune
---

# Session du 2026-10-09 (section Tests, démo T01, graine ACE, titrage)

## Décisions prises
- Section « Tests » dans l'UI admin (liste récente d'abord, pouces, suppression, position, repère « Jamais écouté », numéro unique par test) ; police Sora embarquée ; titre et date sur la pochette.
- Démo T01 : version 18 retenue (voix d'homme, `[Silence]`, texte adapté « posté », « zoublie ») ; voix de femme non retenue, instable.
- Graine ACE corrigée (`use_random_seed=False`) ; paroles contrôlées par `check_lyrics.py` avant lancement.

## Livrables produits ou modifiés
- `webradio/server.py`, `listen.js`, `listen.css`, `listen.html`, `motion.js`, `radio_engine.py`, `radio.html`, `ace_worker.py`, `fonts/` : voir `CHANGELOG.md` v1.7 ; correctifs de revue de code appliqués.
- `TEXTES/tools/check_lyrics.py`, `.claude/commands/generate_lyrics.md`, `.claude/skills/generation-morceaux/SKILL.md`, `webradio/REGLES_GENERATION_DEV.md`, `tests_manuels.md`, `AMELIORATIONS.md` : mis à jour.
- Pochettes : lot terminé (175 créées, 256 exclues pour score négatif).

## Hypothèses validées / invalidées
- VALIDE : la graine n'était pas appliquée ; volume des jingles réglable fonctionnel sur iPhone ; version 18 de la démo jugée bonne par l'utilisateur.
- INVALIDE : essais « seed » antérieurs du test Marie et de la démo ; duo homme/femme par balises de section.
- EN ATTENTE : voix de femme stable ; titrage sur iPhone ; relecture de la revue de code.

## Prochaine étape exacte
Écouter la grille voix de femme et valider le titrage sur iPhone ; relancer analyse et compression avant la prochaine génération musicale.

## Question bloquante pour la session suivante
Une voix de femme stable est-elle obtenue sur l'une des versions de la grille ?

---

# Session du 2026-10-10

## Décisions prises
- Comparer ACE-Step 1.5, MusicGen Small et HeartMuLa OSS 3B sur dix briefs communs, en séparant les seuils techniques de l'écoute humaine.
- Garder les sorties techniquement invalides de HeartMuLa dans l'UI pour rendre leurs défauts observables.

## Livrables produits ou modifiés
- `MODELES_LLM/sorties/campagne_2026-10-09/` : 30 sorties comparatives, sidecars, manifest et journaux de tentatives.
- `webradio/playlists/tests-modeles/outputs/playlist_results.json` : 30 entrées de cette campagne exposées dans trois dossiers de modèles, en plus des dix pistes Stable Audio antérieures.
- `MODELES_LLM/registre_campagne.py` et `DOCUMENTATION/` : suivi reproductible et documentation des modèles et critères.

## Hypothèses validées / invalidées
- VALIDE : ACE-Step et MusicGen Small passent les contrôles techniques sur les dix briefs chacun ; écoute humaine en attente.
- VALIDE : HeartMuLa passe techniquement sur cinq briefs sur dix ; cinq sorties restent consultables comme invalides.
- INVALIDE : toutes les sorties HeartMuLa seraient techniquement recevables -> écrêtage probable sur cinq pistes, durée insuffisante sur l'une d'elles.
- EN ATTENTE : jugement artistique à l'écoute des 30 pistes dans l'UI.

## Prochaine étape exacte
Écouter les 30 pistes comparatives dans la section Tests et renseigner le résultat humain dans l'UI.

## Question bloquante pour la session suivante
Aucune

---

# Session du 2026-10-10

## Décisions prises
- Soumettre tout nouveau contenu destiné à la WebRadio à l'interface de Tests ; aucune diffusion sans demande explicite, même après validation.
- Classer les paroles par artiste : Funky Yogi et Marie ; l'utilisateur déclare disposer des droits sur ces textes.

## Livrables produits ou modifiés
- `AGENTS.md`, `.claude/memory.md`, `webradio/REGLES_GENERATION_DEV.md`, `AMELIORATIONS.md` : règle de validation préalable et action d'application technique.
- `TEXTES/artistes/funky-yogi/`, `TEXTES/artistes/Marie/`, `TEXTES/INDEX.md` : paroles et attribution rangées ; références des tests Marie mises à jour.
- Essais ACE temporaires générés, écoutés puis supprimés à la demande de l'utilisateur ; référence radio conservée.

## Hypothèses validées / invalidées
- INVALIDE sur « Soul du matin » : `shift=3` n'a pas apporté le groove et la précision souhaités par rapport à la référence.
- Selon l'écoute de l'utilisateur, les essais « Funky Yogi » avec moins de styles mêlés sont meilleurs ; cela ne démontre pas une règle générale pour le modèle.

## Prochaine étape exacte
Poursuivre les contrôles manuels restants ; si une nouvelle génération est demandée, la placer dans les Tests avant toute diffusion.

## Question bloquante pour la session suivante
Aucune
