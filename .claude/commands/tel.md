---
description: Mode téléphone — réponses d'une ou deux phrases, questions à choix multiples
---

# /tel — Mode téléphone

L'utilisateur lit depuis son téléphone. À partir de maintenant et jusqu'à la commande `/pc` :

1. **Chaque réponse finale tient en une ou deux phrases de résumé**, sans liste, sans tableau, sans bloc de code, sans titre. Uniquement le résultat et, si besoin, la prochaine étape.
2. **Aucun détail technique** (fichiers, commandes, journaux) sauf si l'utilisateur le demande explicitement.
3. **Pour obtenir son avis : toujours l'outil de questions à choix multiples** (AskUserQuestion), jamais une question ouverte dans le texte.
   - Une seule question par appel, posées les unes après les autres.
   - La proposition recommandée est **toujours la première option**, avec « (Recommandé) » à la fin du libellé.
   - Libellés courts (5 mots maximum), description d'une ligne.
4. Continuer à décider et à agir sans demander l'avis quand la décision ne revient pas vraiment à l'utilisateur.
5. L'honnêteté reste prioritaire : si quelque chose a échoué ou n'est pas vérifié, le dire dans ces deux phrases.

Confirmer l'activation en une phrase.
