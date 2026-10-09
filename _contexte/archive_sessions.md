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
