# Piloter le travail

## Responsabilité du coordinateur

L'agent principal transforme la demande en critères observables, choisit l'effort approprié, tient le tableau et rassemble les preuves. Les agents spécialisés lui retournent des résultats ; ils ne prennent pas le contrôle global du projet.

Pour une coquille ou une modification locale simple : agir, vérifier et expliquer. Le tableau et la revue séparée concernent le travail substantiel. Ajouter des agents seulement si les tâches sont indépendantes ou si une revue indépendante apporte une vérification utile.

## Avant la distribution

1. Lire le besoin actif et les décisions pertinentes. Repérer les questions métier qui changent le résultat.
2. Faire rechercher les incertitudes déterminantes. Un researcher peut comparer des solutions pendant qu'un architecte analyse un contrat déjà connu.
3. Fixer les interfaces partagées : noms, formats, erreurs, données d'entrée/sortie et critères. Faire ce travail avant les implémentations dépendantes.
4. Enregistrer des tâches avec des dépendances explicites. Un chemin de dossier finit par `/` ; un chemin de fichier n'a pas de barre finale. Pas de glob ni de chemin absolu.
5. Exécuter `plan`. Le moteur sélectionne une vague déterministe sans dépendance ouverte ni conflit de périmètre.

Une tâche dépendante ne commence pas parce que son fournisseur « a presque fini ». Le résultat requis doit être intégré et vérifié.

## Paquet de contexte

`packet ID` produit du JSON comprenant le ticket, les critères, les dépendances, le projet, le worktree et les références des résultats précédents. Le coordinateur le complète avec :

- Le résultat attendu et le format de retour.
- Le SHA de départ et le chemin absolu du worktree, si écriture de code.
- Les contrats ou extraits réellement nécessaires.
- La synthèse de recherche, ses sources, ses dates et ses incertitudes.
- Les commandes de vérification et les contraintes de budget.

Le moteur transmet des références de fichiers de preuve et de recherche, pas leur contenu brut. Le coordinateur lit et sélectionne les informations utiles avant d'envoyer le paquet. Les fichiers privés `.local/PERSONAL.md`, les secrets et les journaux sensibles ne sont jamais recopiés.

Une recherche n'est pas un changement approuvé. Une source peut expliquer un comportement ; elle n'autorise ni une migration ni une dépense.

## Exécution isolée

Le coordinateur crée une branche `task/T0001` et un worktree dans `.local/worktrees/T0001`. Le développeur reçoit ce chemin absolu et vérifie sa branche avant toute modification.

Les worktrees partagent la base d'objets Git, mais chacun possède ses fichiers et son index. Ils ne séparent ni les identifiants, ni le réseau, ni les permissions de la machine. Pour des agents non fiables, il faut des environnements et identifiants réellement séparés.

Le coordinateur est le seul écrivain du tableau principal. Un verrou et une écriture atomique protègent les commandes simultanées dans ce checkout ; cela ne constitue pas un verrou distribué entre machines ou worktrees. Ne lancer les commandes de mutation du tableau que depuis le checkout coordinateur, jamais dans les worktrees des développeurs.

La création d'un worktree exige un commit existant et du code suivi propre. Les changements du seul `tasks/board.json` sont admis : le tableau principal peut évoluer pendant les tâches. Les fichiers applicatifs non suivis doivent être ajoutés au commit de départ avant distribution.

Chaque worker retourne : SHA candidat, chemins modifiés, tests réellement exécutés, preuves, limites et éventuels blocages. Il ne pousse pas la branche et ne fusionne pas les travaux des autres.

## Vérification et assemblage

Le verifier reproduit les critères. Le reviewer reçoit le ticket, la base et le SHA candidat avec un contexte neuf. Il cherche des erreurs concrètes et rapporte leur conséquence. Le coordinateur conserve le rapport dans `docs/reviews/` lorsqu'il est utile à la traçabilité.

Un avis `pass` doit être lié au commit soumis. Changer le candidat invalide l'avis précédent. Le moteur vérifie également que les fichiers intégrés correspondent au candidat revu lors de la clôture d'une implémentation.

Intégrer une tâche à la fois. Après l'assemblage, exécuter les contrôles applicatifs ; des changements compatibles textuellement peuvent produire une régression ensemble. En cas de conflit qui exige de modifier le candidat revu, produire et faire revoir un nouveau candidat cohérent avant de clôturer. Ne pas masquer le conflit derrière une clôture forcée.

## Budgets et reprise

Par défaut, trois spécialistes simultanés et deux démarrages par tâche. Ces limites bornent la distribution et les tentatives ; elles ne plafonnent pas les tokens consommés par Codex. Limiter aussi chaque mission par une question précise et un résultat attendu. Les vérifications ont un délai maximal configurable.

En cas d'interruption : lire `status`, l'historique du ticket, les worktrees et les résultats déjà produits. Une tâche `running` n'est pas automatiquement relancée. Vérifier l'état de son agent et de son travail. Si nécessaire, la bloquer avec un motif puis la remettre à ready lorsqu'une reprise est justifiée.

À la limite des tentatives, garder la preuve de l'échec et créer une tâche révisée après diagnostic. Ne pas augmenter silencieusement la limite pour répéter le même essai.

Le script ne fait ni planification horaire, ni surveillance permanente, ni appel de modèle. Les outils natifs de Codex assurent les délégations pendant la session. Une automation future doit être demandée et configurée séparément.
