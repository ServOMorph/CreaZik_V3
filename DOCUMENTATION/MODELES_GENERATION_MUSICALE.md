# Panorama des modèles de génération musicale

Mise à jour : 9 octobre 2026. Les caractéristiques ci-dessous viennent des dépôts officiels indiqués dans les guides de chaque modèle. Les mesures de vitesse et de qualité n’ont pas encore été réalisées de façon comparable sur cette machine.

## PC de référence

Le contexte de la zone `MODELES_LLM` indique Windows, une RTX 4060 de 8 Go, 48 Go de RAM et un Ryzen 7 5700X. La mémoire GPU disponible varie avec les autres applications : la contrôler avant tout essai et exécuter un seul modèle GPU à la fois. Les guides de la zone et le travail de recherche antérieur sont dans [MODELES_LLM/recherche_modeles_generation_musicale.md](../MODELES_LLM/recherche_modeles_generation_musicale.md).

## Comparaison

| Modèle | Entrée principale | Sortie attendue | Matériel / durée documentés | Usage dans la comparaison |
|---|---|---|---|---|
| ACE-Step 1.5 | Caption, paroles structurées, métadonnées facultatives | Chanson complète, voix ou instrumental, édition audio | Le README actuel recommande le DiT 2B Turbo pour 6–8 Go et indique les modes d’offload/quantification pour les petites cartes; durée annoncée jusqu’à 600 s | Modèle de référence déjà utilisé dans le projet; la campagne comprend maintenant dix sorties ACE. |
| HeartMuLa OSS 3B | Fichier paroles + tags musicaux | Chanson conditionnée par paroles et style; le dépôt indique un support multilingue | 3B + codec; le dépôt recommande `--lazy_load true` sur GPU unique, sans publier de mesure pour une RTX 4060 8 Go | Évaluer l’interprétation de paroles françaises, du genre, de l’énergie et des instruments. |
| MusicGen Small | Description textuelle | Clip text-to-music, modèle 300M | Meta indique qu’un GPU est requis pour AudioCraft, recommande 16 Go, et précise que des cartes plus petites peuvent produire des séquences courtes avec Small. Le modèle Small est limité à 30 s dans l’implémentation AudioCraft | Référence instrumentale text-to-music; ne pas lui attribuer une génération de paroles contrôlée. |
| Stable Audio 3 Small-Music | Description textuelle | Musique instrumentale | 433M, CPU, jusqu’à 120 s; runtime officiel TFLite/XNNPACK compatible Windows | Évaluer l’adhérence au style, aux instruments, au tempo et à l’évolution sur 30 s. Ne pas attendre des paroles intelligibles. |

## Principes d’essai

- Utiliser dix briefs identiques sur les quatre modèles, adaptés au format d’entrée prévu par leur documentation.
- Fixer une durée de 30 s pour les extraits comparatifs : c’est le plafond de MusicGen Small. Les résultats ne représentent donc pas une chanson complète.
- Garder la seed fixe quand l’interface l’expose; consigner l’absence de seed si l’API utilisée ne l’expose pas.
- Coter séparément l’adhérence au brief, la cohérence musicale, la qualité audio, les artefacts, et la gestion des voix. Pour les modèles instrumentaux, l’axe voix est « non applicable ».
- Valider techniquement un fichier seulement s’il se décode, dure environ 30 s, n’est pas silencieux/corrompu et correspond globalement au brief. La validation de goût reste à faire à l’écoute dans l’UI.
- Convertir les WAV de génération en MP3 192 kbit/s pour l’UI, puis retirer les WAV de test selon la règle de la webradio.

## Limites à garder en tête

- Les générations ne sont pas des A/B parfaitement équivalents : HeartMuLa produit une chanson guidée par paroles, alors que MusicGen Small et Stable Audio 3 Small-Music sont principalement utilisés ici comme générateurs instrumentaux. Les briefs vocaux sont adaptés à ces deux derniers en arrangements instrumentaux.
- La recommandation Meta de 16 Go est une recommandation générale; elle ne démontre pas que MusicGen Small échoue sur une RTX 4060 8 Go. La mesure doit être observée sur la machine.
- HeartMuLa ne publie pas de besoin mémoire RTX 4060 dans son guide de déploiement. Le chargement paresseux économise la mémoire, mais ne garantit pas que 3B tourne dans la VRAM libre au moment d’un essai.
- La licence des poids MusicGen AudioCraft est CC-BY-NC 4.0, distincte de la licence MIT du code. Tenir compte de cette restriction avant tout usage commercial.

## Sources principales

- [ACE-Step 1.5 — dépôt officiel](https://github.com/ace-step/ACE-Step-1.5)
- [HeartMuLa — dépôt officiel et déploiement local](https://github.com/HeartMuLa/heartlib)
- [MusicGen — documentation officielle AudioCraft](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)
- [Stable Audio 3 — dépôt officiel](https://github.com/Stability-AI/stable-audio-3)
