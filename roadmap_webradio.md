# Roadmap WebRadio IA locale

Référence : `webradio/ARCHITECTURE_WEBRADIO.md`. Statuts mis à jour par `/close` uniquement.

## Phase 1 - Base playlists et serveur sécurisé [EN COURS]
- Génération en rotation du catalogue actuel (86 playlists musicales, 921 morceaux, 85 identifiants dans `series.txt`) + 20 jingles vocaux ; reprise via `/start_generation`.
- Serveur sécurisé, rôles admin / auditeurs, commentaires ; base `radio.db`, avis « sans avis » et dynamique, statistiques admin, catalogue éditable (faits, contrôles iPhone en attente).
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
- Générer les couvertures éligibles avec ComfyUI-Qwen (Qwen-Image 2.1, `D:\ServOMorph\ComfyUI-Qwen`, port 8189), après la file musicale et selon les votes. Lot en cours : 699 couvertures à générer au dernier statut (746 tâches, 26 exclues pour score négatif) ; reprise via `/generate_covers`, les votes sont relus avant chaque image.
- Affichage intégré à la page d'écoute : pochette ou, sans pochette, titre et style sur le visuel ; validation visuelle sur iPhone et champ `cover` dans le catalogue restent à finaliser.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.
