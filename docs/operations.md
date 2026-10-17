# Utiliser le cœur

Le point d'entrée est `python scripts/project.py`. `--root CHEMIN` se place avant la commande si le coordinateur travaille depuis un autre répertoire. Les sorties JSON sont destinées à Codex et restent lisibles à la main.

## Préparer le projet

```bash
python scripts/project.py init --name mon-projet --goal "Résultat attendu"
python scripts/validate_template.py
python scripts/project.py validate
python scripts/project.py check
python scripts/project.py doctor
```

`doctor` nécessite un commit Git existant. Si le dossier a été copié sans historique, configurer l'identité Git souhaitée et créer le premier commit avant de préparer des worktrees. Le moteur ne choisit pas l'identité à ta place.

`init` conserve le tableau existant. Pour réutiliser un projet ayant déjà des tâches, repartir d'une copie neuve du template afin de conserver l'historique de l'ancien projet.

## Créer et distribuer

```bash
python scripts/project.py task add --title "Créer le moteur de calcul" --role implementer --path src/calcul/ --path app_tests/calcul/ --accept "Les exemples métier convenus produisent les résultats attendus"
python scripts/project.py task ready T0001
python scripts/project.py plan
python scripts/project.py worktree T0001
python scripts/project.py packet T0001
python scripts/project.py task start T0001 --worker calcul-worker
```

Ajouter `--depends T0001` lors de la création d'une tâche dépendante. Ajouter `--research docs/research/sujet.md` pour lier une note existante.

Les rôles researcher, architect, verifier et reviewer n'ont pas de `--path` d'écriture. Le coordinateur conserve leurs résultats dans des documents. Les rôles implementer et integrator doivent recevoir des chemins et un worktree ; integrator peut être mandaté pour faire évoluer les fichiers du moteur.

Les chemins d'écriture sont relatifs, sans `..`, glob ou lien symbolique. `src/calcul/` possède le dossier ; `src/calcul.py` possède un fichier. Un dossier parent et un de ses descendants se recouvrent. Le moteur traite la casse de façon conservatrice pour rester compatible avec Windows.

Le code suivi doit être propre à la création du worktree, à l'exception du tableau. Ajouter au commit de départ les fichiers de code encore non suivis. Le moteur ne supprime ni branche ni worktree existant pour recommencer.

`plan` réserve les périmètres des tâches en cours ou en attente d'intégration. Seules les tâches running consomment les places d'agents actifs. Une dépendance doit être done pour débloquer ses consommatrices.
La création et le démarrage du worktree vérifient aussi que les commits intégrés des dépendances sont présents dans sa base ; un ancien checkout ne suffit pas.

Le script prépare la distribution. Le skill `project-orchestrate` lit les paquets, transmet les informations utiles et appelle les outils natifs de sous-agents. Sans session Codex active, aucun agent n'est lancé.

## Soumettre, revoir et clôturer

Enregistrer les preuves et le rapport dans le checkout coordinateur, par exemple sous `docs/evidence/` et `docs/reviews/`, en partant des modèles du dossier `templates/`. Ces documents deviennent des éléments du contexte durable.

Les valeurs `SHA_CANDIDAT` et `SHA_INTEGRE` ci-dessous sont à remplacer par les identifiants Git réels.

```bash
python scripts/project.py task submit T0001 --commit SHA_CANDIDAT --evidence docs/evidence/T0001.md
python scripts/project.py task review T0001 --reviewer calcul-reviewer --commit SHA_CANDIDAT --decision pass --report docs/reviews/T0001.md
```

Le reviewer doit être un autre agent ou une autre personne que le worker. Le nom seul ne prouve pas cette indépendance : le coordinateur doit avoir effectivement effectué la délégation.

Le candidat doit descendre de sa base et ses changements doivent rester dans les chemins déclarés. Une nouvelle soumission efface la revue précédente. Un avis fail remet la tâche à ready, dans la limite du nombre de tentatives.

Après intégration du candidat revu, exécuter les contrôles sur l'assemblage, puis :

```bash
python scripts/project.py check --application
python scripts/project.py task close T0001 --integrated-commit SHA_INTEGRE
```

Le moteur vérifie la présence du commit intégré dans l'historique du coordinateur et la correspondance du contenu des fichiers avec le candidat revu. Il ne sait pas prouver qu'un texte de rapport décrit des tests réellement exécutés : les résultats doivent être lus par le coordinateur.

Une intégration modifiant le contenu revu nécessite un nouveau candidat et une nouvelle revue. La commande close doit refuser une clôture lorsque le contenu diffère.
Le moteur contrôle également le contenu de HEAD courant : un ancien commit valide ne peut pas masquer une modification ultérieure des mêmes fichiers.

## État, interruption et verrou

```bash
python scripts/project.py status
python scripts/project.py task block T0001 --reason "Information métier nécessaire"
python scripts/project.py task ready T0001
```

Le tableau reste dans `tasks/board.json`, avec l'historique de chaque tâche. Le coordinateur le versionne avec les preuves lors des points de sauvegarde cohérents. Une tâche done n'est pas rouverte en effaçant son histoire ; une nouvelle demande corrective reçoit sa propre tâche.
Arrêter réellement le sous-agent concerné avant de bloquer ou réattribuer une tâche : changer son statut dans le tableau n'arrête pas son processus.

Un verrou `tasks/.board.lock` refuse une mutation concurrente. Un arrêt brutal peut laisser ce verrou. Vérifier qu'aucun coordinateur ne travaille encore, conserver le diagnostic et retirer le verrou uniquement après cette vérification ; ne pas automatiser sa suppression sur simple ancienneté.

La création Git du worktree et l'écriture du tableau ne forment pas une seule transaction. En cas d'erreur disque entre les deux, le moteur préserve le worktree : le coordinateur examine `git worktree list`, le dossier et le tableau avant toute récupération.

## Vérifications et CI

`check` exécute les tests du socle et renvoie le résultat réel de chaque commande. `check --application` exécute les listes d'arguments de `checks.application` sans shell. Les contrôles sont du code du projet : les examiner avant de les configurer.

Le délai est de 120 secondes par commande par défaut, réglable par `--timeout`. Il borne le processus direct ; les processus descendants d'un outil tiers peuvent nécessiter une gestion dédiée. Les tests de ce socle utilisent des ressources temporaires isolées.

La CI livrée vérifie le socle sur Windows et Linux, avec Python 3.11 et 3.12. Ajouter les dépendances et contrôles du produit lors du kickoff. Une première exécution GitHub ne peut être déclarée verte qu'après lecture de son résultat.

La configuration de protection de branche et l'exigence du contrôle CI se font dans GitHub selon les possibilités du compte. Le fichier YAML ne crée pas à lui seul cette protection.

## Publication du template

Créer un dépôt privé portant le nom choisi, y pousser le socle, puis activer l'option GitHub « Template repository » dans ses réglages si disponible. Cela ne rend pas le dépôt public.
Le partage ou une licence de distribution se décide séparément selon l'usage prévu.
