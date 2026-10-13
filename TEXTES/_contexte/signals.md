# Signals — textes   (MAJ 2026-10-13)

## Actions ouvertes
- [P1|ouvert] Obtenir l'accord écrit de Jean-Marc Lagniel pour T01 « Arroser Les Roses » (envoi du mail avec la démo v18 à contact@parolessansmusique.fr). Brouillon du mail non rédigé, proposé et non demandé.
  fait quand: réponse écrite de l'auteur reçue et consignée dans `TEXTES/usage_prive/INDEX.md` (ou refus consigné)
  réf: `TEXTES/usage_prive/INDEX.md`, `TEXTES/liste_attente.md` (T01), `webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3`
- [P2|ouvert] Préparer T02 (Capitaine Red Barbosa) : titre, style, structure (refrain à créer ou non), balisage ACE ; confirmer le statut « libre de droit » (déclaré, non vérifié, auteur possiblement pseudonyme).
  fait quand: fichier `_ace.md` créé et T02 passé à `PRET` via `liste_attente.py`
  réf: `TEXTES/domaine_public/capitaine-red-barbosa_01.md`, `TEXTES/liste_attente.md`
- [P3|ouvert] Décider du sort de `generate_lyrics.py` et de `/generate_lyrics` (piste LLM gemma4:12b abandonnée par l'utilisateur ; non supprimés).
  fait quand: fichiers supprimés ou conservés par décision explicite
  réf: `TEXTES/tools/generate_lyrics.py`, `.claude/commands/generate_lyrics.md`

## Dernière session (2026-10-13)
# Session du 2026-10-13

## Décisions prises
- Piste « génération des paroles par LLM (gemma4:12b) » mise de côté ; script et commande conservés.
- Textes du site parolessansmusique.fr : protégés (© Jean-Marc Lagniel, usage privé libre, usage professionnel sur accord), donc non récupérés en masse ; demande d'accord par mail, précédée d'une démo.
- T01 « Arroser Les Roses » choisi pour la démo (stockage privé, jamais en playlist ni radio).
- Suivi des textes via `liste_attente.md` + `liste_attente.py`, mis à jour par l'orchestrateur.

## Livrables produits ou modifiés
- `TEXTES/domaine_public/` (texte Capitaine Red Barbosa + INDEX) : commité.
- `TEXTES/usage_prive/` (T01 original, version ACE, INDEX) : commité.
- `TEXTES/liste_attente.md`, `TEXTES/tools/liste_attente.py` : commités ; T01 mis à jour par l'orchestrateur jusqu'à `GENERE`.
- `TEXTES/tools/generate_lyrics.py`, `.claude/commands/generate_lyrics.md` : commités, piste abandonnée.

## Hypothèses validées / invalidées
- VALIDE : démo T01 v18 (voix d'homme, saxophone, [Silence]) retenue à l'écoute par l'utilisateur.
- INVALIDE : voix de femme sur T01, instable (v11, v14 à v19) ; duo v13 inopérant.
- EN ATTENTE : accord écrit de l'auteur ; statut libre de droit de T02 non vérifié.

## Prochaine étape exacte
Envoyer la demande d'accord à l'auteur (avec la v18), puis préparer T02.

## Question bloquante pour la session suivante
Aucune
