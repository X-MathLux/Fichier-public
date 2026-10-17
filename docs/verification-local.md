# Vérification locale avant publication

Date : 17 octobre 2026. Environnement observé : Windows, Python 3.12.14, Git et CLI Codex 0.163.0-alpha.10.2.

## Contrôles exécutés

- `python scripts/validate_template.py` : rôles TOML, skills, cohérence de concurrence, liens locaux et références CI valides.
- `python scripts/project.py validate` : configuration et tableau initial vide valides.
- `python scripts/project.py check` : **25 tests exécutés, 24 réussis et 1 ignoré**, en 44,054 secondes sur cette machine. Le test ignoré nécessite une création de lien symbolique que Windows n'a pas autorisée.
- Le validateur fourni avec le skill système `skill-creator` a validé les quatre skills. Son dépendant PyYAML a été installé uniquement dans un dossier de travail temporaire, pas dans le socle.
- Le YAML de CI a été parsé et sa structure contrôlée.
- `codex features list` a accepté la configuration locale ; cela ne prouve pas à lui seul que les agents personnalisés sont chargés dans une session de confiance.

Les tests du moteur couvrent dépendances et cycles, conflits de chemins, concurrence, chemins invalides, verrou, sauvegarde atomique, worktrees, soumissions hors périmètre, avis indépendant, revue périmée, intégration du contenu revu et commandes applicatives absentes, échouées ou expirées.

## Revue indépendante

Un autre agent a parcouru les workflows et exercé un scénario dans une copie isolée : recherche, deux tâches indépendantes, interface dépendante et reprise après checkpoint.

Il a reproduit deux défauts, corrigés puis revérifiés :

1. Une clôture pouvait citer un ancien commit revu alors que HEAD avait changé. La clôture contrôle maintenant aussi les fichiers du HEAD courant.
2. Une tâche dépendante pouvait posséder un ancien worktree sans le code intégré de sa dépendance. Création, démarrage et soumission contrôlent maintenant cette ascendance.

Les tests de régression ciblés ont été exécutés indépendamment après correction. Aucun défaut concret restant n'a été relevé dans le périmètre de cette revue.

## Limites de cette preuve

Cette preuve ne remplace pas les tests d'une future application. Le chargement des six rôles dans un nouveau projet Codex de confiance et l'application effective de leurs restrictions doivent être observés dans cet hôte.
La CI GitHub est vérifiée après publication, à partir de son résultat réel dans l'onglet Actions ; elle ne fait pas partie de cette preuve locale préalable.
Les scénarios du dossier `evaluations/` restent un programme d'essais à rejouer selon le projet, pas une affirmation qu'ils ont tous été exécutés.
