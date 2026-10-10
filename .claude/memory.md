# Mémoire projet
<!-- Fichier géré via /create_memory. Ne pas modifier manuellement sauf pour supprimer des entrées. -->

## 2026-10-07 — Mode dev, un seul utilisateur
Le projet est en mode dev : aucun autre utilisateur que le développeur pour l'instant. Les votes, avis et dynamiques enregistrés sont les siens et sont à conserver (ne pas les effacer).

## 2026-10-09 — Traçabilité des morceaux
À chaque génération musicale, conserver avec le morceau la date et le fuseau, le modèle et sa version/révision, le prompt exact, les paroles/tags ou entrées audio, tous les paramètres effectifs, les versions logicielles et l’appareil utilisé, les caractéristiques du fichier, les contrôles et le statut d’écoute. Maintenir un sidecar JSON par morceau et un manifeste reprenable; ne jamais confondre validation technique et validation artistique par écoute.

## 2026-10-10 — Validation avant diffusion WebRadio
Tout nouveau fichier de test ou contenu généré destiné à la WebRadio doit être soumis à l'utilisateur dans l'interface de Tests avant diffusion, avec sa référence si une comparaison part d'un contenu existant. Si le format n'y est pas pris en charge, établir un moyen de validation adapté. Ne rien ajouter aux playlists diffusées ni mettre en rotation sans demande explicite de l'utilisateur, même après validation.

## 2026-10-10 — Sens de « garde » pour un morceau
Quand l'utilisateur dit « garde » à propos d'un morceau généré (test), déplacer le MP3 et son sidecar `.metadata.json` dans le dossier de l'artiste du texte (par exemple `TEXTES/artistes/Marie/`), le retirer de la section Tests et mettre à jour l'`INDEX.md` du dossier. Ne pas le laisser dans les Tests.
