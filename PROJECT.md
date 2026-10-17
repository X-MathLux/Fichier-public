# Projet

Ce fichier est la fiche du projet actif. Le kickoff la remplit avec le besoin réel.

| Sujet | État initial |
| --- | --- |
| Objectif | Construire un socle personnel de projets pilotés avec Codex |
| Utilisateur | Propriétaire du dépôt et agents de développement mandatés |
| Résultat observable | Créer, répartir, vérifier et reprendre un projet avec des preuves conservées |
| Périmètre du socle | Instructions, rôles, skills, tableau de tâches, isolation Git, CI du socle |
| Stack de l'application | À choisir selon le besoin du futur projet |
| Déploiement | Local par défaut ; fournisseur à choisir si nécessaire |

## Au lancement d'un futur projet

Écrire le problème concret, les utilisateurs, les parcours essentiels, les critères de réussite et ce qui est hors périmètre.
Choisir ensuite la stack, les dépendances, les commandes de développement et les tests de l'application.
Ajouter les commandes sous `checks.application` dans `project.json` et expliquer comment les reproduire.

## Décisions

Les décisions qui changent l'architecture vont dans [docs/decisions/](docs/decisions/README.md).
Les recherches sourcées vont dans [docs/research/](docs/research/README.md).
Les questions métier non résolues restent explicites ; elles ne sont pas transformées en hypothèses silencieuses.
