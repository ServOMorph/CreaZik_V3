# Roadmap WebRadio IA locale

Référence : `webradio/ARCHITECTURE_WEBRADIO.md`. Statuts mis à jour par `/close` uniquement.

## Phase 1 - Base playlists et serveur sécurisé [EN COURS]
- Génération en rotation de toutes les playlists (78 configurées) + jingles, relance automatique.
- Serveur sécurisé, rôles admin / auditeurs, commentaires.
- Validation de l'écoute sur iPhone (tests manuels).

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 2 - Catalogue et taxonomie [TODO]
- `catalog.json`, `taxonomy.json`, script de construction à partir des playlists générées.
- Classement initial et correction manuelle dans l'admin.
- Tests : intégrité du catalogue sur les 178 morceaux.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 3 - Playlists et programmation [TODO]
- Playlists intelligentes et manuelles, poids par playlist, tranches horaires.
- Migration des poids actuels (par playlist générée) vers des playlists intelligentes.
- Tests : distribution du tirage sur un grand nombre de tirages.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 4 - Ajout de morceaux et multi-IA [TODO]
- Interface fournisseurs, file de jobs, formulaire d'ajout, validation des nouveaux morceaux.
- Deuxième fournisseur d'IA évalué avec la même playlist de test.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 5 - Sobriété énergétique et jingles parlés [TODO]
- Mesure des Wh par morceau, tableau de bord.
- Jingles parlés avec voix locale et chiffres mesurés.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 6 - Flux unique et mise en ligne [TODO]
- Lecteur serveur et flux unique, choix du tunnel, durcissement final.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 7 - Couvertures des morceaux [TODO]
- Générer une couverture par morceau avec ComfyUI-Qwen (Qwen-Image 2.1, `D:\ServOMorph\ComfyUI-Qwen`, port 8189), à lancer quand la file de génération musicale est vide. Test réalisé, style à valider avant le lot.
- Afficher la couverture sur la page d'écoute et dans l'explorateur ; champ `cover` dans le catalogue.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.
