# Plan d'exécution WebRadio

Suivi de toutes les demandes de la conversation. Statuts : FAIT (livré et contrôlé par test, requête ou navigateur), FAIT non vérifié (livré, jamais vu ou écouté), EN COURS, A FAIRE, EN ATTENTE (dépend d'une information de l'utilisateur).

## 1. Radio en direct et lecteur
| # | Demande | Statut |
|---|---|---|
| 1.1 | Play = écouter ce qui tourne actuellement (radio en direct commune) | FAIT : moteur serveur (11 tests), lecteur contrôlé dans un navigateur : lecture calée sur le direct |
| 1.2 | Bug : en passant en mode admin, la radio ne s'entend plus | FAIT (corrigé par 1.1 ; à confirmer sur iPhone) |
| 1.3 | Bug : play en admin oblige à attendre la fin du morceau | FAIT (corrigé par 1.1 ; à confirmer sur iPhone) |
| 1.4 | Fondus de transition à déboguer, transitions très douces | FAIT non écouté : courbes à puissance constante, préchargement, MP3 allégés ; sur iPhone, fondus via Web Audio à vérifier |
| 1.5 | Mode auditeur : pas de changement de morceau | FAIT (bouton masqué ; blocage réel : le direct est commun) |
| 1.6 | Bascule auditeur/admin par icône en haut à droite | FAIT |
| 1.7 | Jingle tous les N morceaux, réglable | FAIT (moteur testé) |
| 1.8 | Programmation admin : passés, à venir, clic pour lire ensuite (morceau, jingle, playlist) | FAIT : actions contrôlées dans un navigateur (lire maintenant, remonter, retirer) |
| 1.9 | Pouces haut et bas, valeurs enregistrées, clics illimités qui pèsent sur le poids (100 clics = le morceau ne passe presque plus) | FAIT (serveur, moteur testé, lecteur) ; non vu sur iPhone |
| 1.10 | Favoris | FAIT non vérifié |
| 1.11 | Commentaires, un commentaire au hasard toutes les 5 s | FAIT non vérifié |

## 2. Visuels et motion design
| # | Demande | Statut |
|---|---|---|
| 2.1 | Supprimer le choix du visuel | FAIT (boutons retirés par l'agent design) |
| 2.2 | Un visuel différent par playlist, affiché selon la playlist du morceau | FAIT non vu : 12 motifs, une fiche de style par playlist |
| 2.3 | Un nouveau visuel à chaque nouvelle playlist (règle) | FAIT : fiche de style ajoutée à chaque playlist créée, et visuel inédit généré automatiquement en repli |
| 2.4 | Script de transitions visuelles très douces | FAIT non vu : 5 types de transitions |
| 2.5 | Motion design pendant les jingles : nom de la radio et message IA locale | FAIT non vu : 3 variantes, textes éditables dans la gestion |
| 2.6 | Motion design régulier (tous les 5 morceaux) pour serenia-tech.fr, 10 designs | FAIT non vu : 10 designs, textes tirés du contenu du site |
| 2.7 | Texte défilant, contact, animation liée à la musique | FAIT |
| 2.8 | L'agent design doit proposer un design plus moderne et plus stylisé | A FAIRE : refonte visuelle des pages (écoute, gestion, explorateur) après vérification des visuels |

## 3. Voix et jingles
| # | Demande | Statut |
|---|---|---|
| 3.1 | Recherche de la meilleure voix open source adaptée au PC | FAIT (Kokoro et Chatterbox, installés sur D:) |
| 3.2 | Jingles parlés pour valoriser l'IA locale | FAIT : 10 jingles parlés générés (Kokoro), textes sobres et vérifiables, à valider par l'utilisateur |
| 3.3 | Mesure d'énergie pour appuyer le discours | A FAIRE |

## 4. Génération et playlists
| # | Demande | Statut |
|---|---|---|
| 4.1 | Génération en tournante (un morceau par playlist à tour de rôle) | FAIT (en cours d'exécution) |
| 4.2 | Durée des morceaux 1 min 30 plus ou moins 45 s | FAIT (paroles adaptées à la durée) |
| 4.3 | Morceaux « pas terminés à 1 min 30 » à déboguer | EN COURS : fins de fichiers mesurées (pas de coupure sèche, 2 à 5 s de silence final), transcription des paroles à relancer |
| 4.4 | Relance systématique après arrêt, relance automatique des plantages | FAIT (services.ps1, superviseur) |
| 4.5 | Playlists demandées : Perso et ses 6 versions, instrumental, disco EN, groove EN, electro atmosphérique, electro-pop FR, années 50, futuriste, poésie FR et EN, percussions Amérique du Sud et Afrique, rap FR mélodique, tribal, a cappella hommes et femmes, guitare, harpe, piano seuls, chant mongol, didgeridoo, electro spatiale, synthés épiques, rock progressif instrumental, funk saxophone, tech, hard tech, jeux vidéo, hard rock | FAIT : 40 playlists configurées, en génération |
| 4.6 | Disco en espagnol, portugais, italien, allemand (accord donné) | A FAIRE |
| 4.7 | Couvertures de morceaux avec une IA locale (nom de l'IA à fournir) | EN ATTENTE du nom ; à lancer quand la file est vide |
| 4.8 | Compléter la radio : playlists éclectiques, tous les styles du monde | EN COURS : à poursuivre en continu |

## 5. Pondération
| # | Demande | Statut |
|---|---|---|
| 5.1 | Analyse du système de pondération | FAIT (rapport remis) |
| 5.2 | Gains rapides : file revalidée (fait dans le moteur), délai entre versions d'une même chanson, pourcentages réels affichés | EN COURS : file revalidée faite ; reste le délai par chanson et l'affichage des pourcentages |

## 6. Sécurité, administration, accès
| # | Demande | Statut |
|---|---|---|
| 6.1 | Sécuriser le tunnel, propositions | FAIT |
| 6.2 | Gestion WebRadio réservée à l'admin (admin / admin pour l'instant) | FAIT |
| 6.3 | Sections admin pliables | FAIT |
| 6.4 | Agent de design dédié à l'UI | FAIT |
| 6.5 | Vocabulaire : benchmarks remplacés par playlists dans tout le code | FAIT |
| 6.6 | Commit | FAIT à la fin de ce plan (voir historique git) |

## 7. Qualité
| # | Demande | Statut |
|---|---|---|
| 7.1 | Tests automatiques du moteur | FAIT (11 tests) |
| 7.2 | Vérification dans un vrai navigateur (Playwright) | EN COURS : lecteur et admin vérifiés ; visuels, transitions, motion design à vérifier |
| 7.3 | Documentation à jour, anciens fichiers obsolètes archivés | A FAIRE |
| 7.4 | Tests manuels à faire par l'utilisateur listés | FAIT (tests_manuels.md) |

## Ordre d'exécution restant
1. Vérifier dans le navigateur les visuels, transitions et motion design (2.2 à 2.6, 7.2).
2. Refonte visuelle plus moderne et plus stylisée par l'agent design (2.8).
3. Mesure d'énergie (3.3) et validation des textes de jingles.
4. Débogage des fins de morceaux (4.3).
5. Pondération : délai par chanson et pourcentages (5.2).
6. Disco en 4 langues (4.6), puis nouvelles playlists éclectiques (4.8).
7. Documentation et nettoyage (7.3).
