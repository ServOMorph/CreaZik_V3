# Liste d'attente — textes à transformer en chanson

Fichier mis à jour par l'agent TEXTES (ajout de textes) et par l'orchestrateur (avancement des générations) via `python TEXTES/tools/liste_attente.py`. Ne pas éditer les lignes du tableau à la main.

Statuts : `A_PREPARER` (texte brut à baliser) · `PRET` (paroles ACE prêtes) · `EN_GENERATION` · `GENERE` (mp3 produit, à écouter) · `VALIDE` (validé à l'écoute) · `REJETE` · `BLOQUE_DROITS` (autorisation requise avant tout usage public).

| ID | Texte | Auteur | Fichier de paroles | Droits | Statut | MAJ | Résultat / note |
|----|-------|--------|--------------------|--------|--------|-----|-----------------|
| T01 | Arroser Les Roses | Jean-Marc Lagniel | TEXTES/usage_prive/arroser-les-roses_ace.md | Protégé : démo privée seulement, autorisation de l'auteur non demandée | GENERE | 2026-10-08 | v18 retenue (homme, [Silence]) ; grille voix femme : 6 versions de 60 s regenerees avec le texte corrige (numeros 39 a 44, remplacent 20 a 25) et 6 versions de 135 s (26 a 31) dans la section Tests, a ecouter ; non valide, accord auteur absent |
| T02 | (sans titre) « Il était une fois, une grand-mère qui mourut. » | Capitaine Red Barbosa | TEXTES/domaine_public/capitaine-red-barbosa_01.md | « Libre de droit » déclaré par l'utilisateur, non vérifié | A_PREPARER | 2026-10-08 | Titre, style, structure (refrain) et balisage ACE à définir |

## Journal

- 2026-10-08 : création de la liste (T01, T02).
- 2026-10-08 : T01 -> EN_GENERATION (5 versions courtes (45 s, couplet 1 + refrain) en cours dans webradio/tests_ace/demo_lagniel/, une variable par version (bpm, graine, voix, rythme))
- 2026-10-08 : T01 : lancement de 5 generations courtes de test (demo_lagniel), un worker par version
- 2026-10-08 : T01 -> GENERE (5 MP3 de test (45 s) dans webradio/tests_ace/demo_lagniel/outputs/ (v1 base, v2 bpm100, v3 graine 7, v4 baryton, v5 folk) ; v1 aussi sur le bouton Test (webradio/playlists/tests-ace/outputs/07_demo_arroser_v1.mp3), a retirer apres ecoute ; a ecouter, non valide)
- 2026-10-08 : T01 -> GENERE (Version v1 gardee (45 s, couplet 1 + refrain) : webradio/tests_ace/demo_lagniel/outputs/01_v1_base_seed42.mp3 et section Tests de l'UI ; v2 a v5 supprimees de l'UI (originaux dans demo_lagniel/outputs) ; a ecouter, non valide)
- 2026-10-08 : T01 -> EN_GENERATION (Generation complete (135 s, 39 lignes, graine 42, caption de v1) en cours : webradio/tests_ace/demo_lagniel/ id 6 ; v1 courte gardee)
- 2026-10-08 : T01 -> GENERE (Version complete 135 s (39 lignes, graine 42, caption de v1) : webradio/tests_ace/demo_lagniel/outputs/06_v6_complet_135s_seed42.mp3 et section Tests de l'UI ; v1 courte gardee ; a ecouter, non valide)
- 2026-10-08 : T01 -> GENERE (v6 complete 135 s + v7 (balise [Silence]) et v8 (balise [Instrumental]) : extraits 60 s, dans la section Tests de l'UI et dans webradio/tests_ace/demo_lagniel/outputs/ ; v1 courte gardee ; a ecouter, non valide)
- 2026-10-08 : T01 -> GENERE (Versions completes 135 s avec saxophone lead et silences : v9 ([Silence]), v10 ([Instrumental]), v11 (voix femme, [Instrumental]) dans la section Tests de l'UI et webradio/tests_ace/demo_lagniel/outputs/ ; v6 sans silence, v7 et v8 extraits ; a ecouter, non valide)
- 2026-10-08 : T01 -> GENERE (v12 (v10 + poste/zoublie) et v13 (duo : couplets alternes homme/femme, refrains ensemble, outro homme puis femme) 135 s dans la section Tests de l'UI et webradio/tests_ace/demo_lagniel/outputs/ ; texte adapte (poste, zoublie) a signaler a l'auteur ; v10 validee a l'ecoute pour l'instrumental ; non valide)
- 2026-10-08 : T01 -> GENERE (v12 retenue par l'utilisateur apres ecoute (2026-10-08) : webradio/tests_ace/demo_lagniel/outputs/12_v12_sax_poste_zoublie.mp3 (135 s, homme, saxophone lead, silences [Instrumental], texte adapte : poste, zoublie). Statut VALIDE non applicable tant que l'accord ecrit de l'auteur n'existe pas ; demo privee, jamais en playlist ni radio)
- 2026-10-08 : T01 -> GENERE (v12 retenue (homme) apres ecoute ; v14 = v12 avec voix feminine ([* - female vocal], caption playful female vocal) dans la section Tests de l'UI et webradio/tests_ace/demo_lagniel/outputs/14_v14_femme_sax.mp3 ; v13 (duo) ne fonctionne pas ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v12 retenue (homme) ; voix femme : v14 (graine 42) instable, v15 a v17 = memes reglages avec graines 7, 123, 2024 dans la section Tests de l'UI et webradio/tests_ace/demo_lagniel/outputs/ ; a ecouter ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v12 retenue (homme, [Instrumental]) ; v18 = v12 avec [Silence] a la place de [Instrumental] (webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3 et section Tests) ; voix femme instable (v14 a v17) ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v12 retenue (homme) ; voix femme : v15 (graine 7) jugee la meilleure a l'ecoute (webradio/tests_ace/demo_lagniel/outputs/15_v15_femme_sax_seed7.mp3), v14, v16, v17 non retenues ; v18 = v12 avec [Silence] ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v12 retenue (homme) ; voix femme : v15 retenue a l'ecoute (webradio/tests_ace/demo_lagniel/outputs/15_v15_femme_sax_seed7.mp3, non reproductible car la graine du worker n'est pas appliquee : use_random_seed actif) ; v19 = meme reglage, autre tirage ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v18 retenue par l'utilisateur apres ecoute (2026-10-08) : webradio/tests_ace/demo_lagniel/outputs/18_v18_sax_silence_poste.mp3 (135 s, voix d'homme, saxophone lead, silences [Silence], texte adapte : poste, zoublie). Voix de femme non retenue : instable (v11, v14, v15, v19), duo v13 inoperant. Statut VALIDE non applicable tant que l'accord ecrit de l'auteur n'existe pas ; demo privee, jamais en playlist ni radio)
- 2026-10-08 : T01 -> GENERE (v18 retenue (homme, [Silence]) ; recherche voix femme : worker corrige (graine appliquee, verifie par doublon), grille de 12 versions (60 s et 135 s, 2 captions, graines 7/123/2024) dans la section Tests de l'UI, a ecouter ; non valide, accord auteur absent)
- 2026-10-08 : T01 -> GENERE (v18 retenue (homme, [Silence]) ; grille voix femme : 6 versions de 60 s regenerees avec le texte corrige (numeros 39 a 44, remplacent 20 a 25) et 6 versions de 135 s (26 a 31) dans la section Tests, a ecouter ; non valide, accord auteur absent)
