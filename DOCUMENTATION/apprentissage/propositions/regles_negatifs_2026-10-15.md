# Règles proposées à partir des morceaux à score négatif (2026-10-15)

Statut : propositions, non appliquées. Ni `regles_modeles.json`, ni le skill `generation-morceaux`, ni `preferences.json` ne sont modifiés ; application sur accord de l'utilisateur.

## Base d'analyse
- 857 morceaux votés avec un score non nul : 473 négatifs, 384 positifs (taux global de négatifs : 55 %). Sources : `webradio/votes.json`, catalogue encore présent (603 morceaux hors jingles) et `webradio/learning/morceaux_rejetes.jsonl` (254 morceaux déjà supprimés). Liste figée des 296 négatifs encore au catalogue : `negatifs_2026-10-15.json`.
- Un seul votant (le développeur). Un vote par morceau en général, signal binaire. Les graines des morceaux antérieurs au 2026-10-11 ne sont pas connues : l'analyse ne porte ni sur la graine ni sur les paramètres de diffusion ACE (non enregistrés pour ces morceaux), seulement sur le caption, le type, la langue, la durée, le tempo mesuré et la playlist.
- Les effets ci-dessous sont corrélés entre eux (une playlist impose son style, sa langue et son caption) : aucune ne prouve une cause. Seules les différences à effectif d'au moins 12 morceaux par groupe sont retenues comme règles ; le reste est hypothèse.

## Règles proposées (preuves mesurées)
1. Voix en anglais : 9 négatifs sur 101 (9 %), contre 149 sur 239 (62 %) en français. Priorité à l'anglais pour les morceaux vocaux. Les langues italienne, espagnole, portugaise et allemande n'ont que 10 morceaux chacune (0 à 20 % de négatifs) : tendance, pas règle.
2. Chansons françaises : 62 % de négatifs, dont les reprises « francais_tests-* » (rock 20/21, classique 18/20, chorale 17/20, folk 17/21, grégorien 14/19). Ne pas relancer de lot de chansons françaises en ACE ; limiter à des essais unitaires dans les Tests.
3. Instrumental : 311 négatifs sur 477 (65 %), contre 162 sur 380 (43 %) pour les vocaux. Un morceau instrumental sans identité forte (instrument solo, ambiance) est rejeté plus souvent qu'un morceau chanté. À préférer : instrumental avec section rythmique marquée (voir règle 6), sinon vocal anglais.
4. Captions à éviter (effectif >= 12, taux de négatifs >= 85 %) : « energetic french vocal » (21/22), « powerful drums » (20/21), « distorted electric guitars » (20/21), « rock » (20/21), « tuba » (12/13), « tambourine » (12/13), « classical music » (22/24), « art song » (18/20), « lyrical operatic vocal » (18/20), « church acoustics » (17/20), « mixed choir four-part harmony satb » (17/20), « lively » (12/12).
5. Captions associés à peu de rejets (effectif >= 12, taux de négatifs <= 30 %) : « female vocal » (1/18), « english lyrics » (2/30), « disco » (1/15), « four-on-the-floor kick » (1/15), « duet vocal » (1/13), « brass section » (2/17), « slap bass » (3/19), « saxophone » (3/14), « 124 bpm » (2/13), « 118 bpm » (3/12), « 120 bpm » (6/20), « male vocal » (6/21), « slow » (5/17). Ils décrivent surtout les playlists disco/groove/funk (voir règle 6).
6. Styles : les playlists à 0-10 % de négatifs sont disco (en, de, es, it, pt), groove-en, house-trance, hard-rock, rap-fr-melodique, annees-50, poesie-fr/en, acappella-femmes, esprit-jackson/dylan/madness (effectif 10 chacune). Les playlists à 90-100 % de négatifs (effectif 6 à 10) sont harpe-seule, klezmer, polynesie, caraibes, gospel, percussion-afrique, soul-motown. Favoriser les styles danse/groove avec section rythmique (funk, disco, house) ; éviter instrument solo, percussions seules et musiques traditionnelles en ACE.
7. Tempo dans le caption : les morceaux dont le caption contient un tempo en bpm sont négatifs à 30 % (67/221 ; 27 à 40 % selon la tranche), contre 64 % (405/632) sans tempo. L'effet est confondu avec la date de génération (captions récents plus précis) ; garder tout de même un tempo explicite par précaution.
8. Durée : peu d'effet (négatifs : 55 % sous 60 s, 59 % de 60 à 90 s, 55 % de 90 à 120 s, 48 % de 120 à 150 s). Pas de règle ; 120 à 150 s est le groupe le moins rejeté.
9. Tempo mesuré (`feat.bpm`) : taux entre 50 % et 61 % sans gradient net. Pas de règle.

## Ce que cette analyse ne permet pas
- Séparer l'effet du caption de celui du style de la playlist.
- Dire si un rejet vient de la voix, du mixage, de la mélodie ou de la structure : aucun commentaire textuel exploitable n'a été enregistré avec les votes.
- Évaluer graine et paramètres ACE pour les morceaux d'avant le 2026-10-11.
