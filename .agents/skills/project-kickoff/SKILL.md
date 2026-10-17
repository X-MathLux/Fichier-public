---
name: project-kickoff
description: Initialiser un nouveau projet issu de ce template, préciser son besoin et installer les vérifications de sa stack.
---

Lire `PROJECT.md`, `project.json` et les préférences `.local/PERSONAL.md` si présentes.
Clarifier uniquement les informations qui déterminent le résultat : utilisateurs, parcours, contraintes et critère de réussite.
Avancer sur les préparatifs indépendants pendant les questions. Choisir la stack après le besoin ; justifier les dépendances importantes.

Exécuter `python scripts/project.py init --name NOM --goal OBJECTIF` pour personnaliser la configuration.
Remplir `PROJECT.md` avec le besoin réel. Choisir les modules utiles dans `docs/modules.md`.
Installer une commande de développement et les tests de l'application, puis inscrire leurs argv dans `checks.application`.
Exécuter les vérifications du socle et `python scripts/project.py check --application` ; une configuration vide ne valide rien.
Adapter la CI aux dépendances réelles. Garder un README utilisable avec commandes de démarrage.

Pour une première livraison substantielle, utiliser `project-orchestrate`. Ne pas créer de service payant, compte ou déploiement par simple effet du kickoff.
Rapporter ce qui fonctionne, ce qui a été vérifié et les décisions encore nécessaires.
