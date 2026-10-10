---
description: Génère ou reprend les pochettes des morceaux avec l'IA locale
---

# /generate_covers

Génère les couvertures des morceaux disponibles (une image différente par morceau, sans texte) à partir du titre et du style musical du morceau. La commande peut être relancée depuis une autre conversation : les fichiers image existants sont la source de vérité, et l'état détaillé est conservé dans `webradio/logs/cover_generation_state.json`.

## Procédure

1. Lire `webradio/REGLES_GENERATION_DEV.md` et vérifier `python webradio/tools/cover_batch.py --status`.
2. Exclure les playlists dont l'identifiant commence par `esprit-` ou dont le libellé commence par « Esprit ».
3. Lancer `python webradio/tools/cover_batch.py`. Ne pas lancer en parallèle une seconde génération. Le script attend automatiquement la fin des processus de génération musicale, démarre ComfyUI-Qwen si nécessaire, puis génère les pochettes une par une.
4. Avant chaque génération, le script relit `webradio/votes.json` : il traite d'abord les morceaux au solde de pouces positif, puis ceux sans aucun vote, puis les soldes équilibrés. Les soldes négatifs sont exclus. La priorité est recalculée avant chaque morceau afin de prendre en compte les votes qui évoluent. Si un morceau devient négatif pendant la génération, son image temporaire n'est pas conservée.
5. Chaque couverture est enregistrée dans le dossier `outputs` sous le nom du morceau avec le suffixe `.cover.png`. Les fichiers déjà valides sont ignorés ; après interruption ou changement de conversation, relancer cette commande pour reprendre.
6. En cas de demande d'arrêt, exécuter `/stop_covers`. Ne pas appeler `/stop`, qui arrête aussi les services radio.
7. Si une couverture manque ou échoue, ne pas bloquer la radio : l'interface auditeur affiche l'animation visuelle existante à la place.
8. À la fin, afficher le nombre de pochettes créées, celles exclues pour solde négatif, celles en échec, et le chemin du fichier d'état. `completed_with_skips` signifie que les seuls éléments restants ont un solde négatif ; la commande pourra les réévaluer lors d'un prochain lancement.

Pour limiter le travail à une playlist : `python webradio/tools/cover_batch.py --playlist <identifiant>`.
