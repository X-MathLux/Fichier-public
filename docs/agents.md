# Agents, pouvoirs et limites

Le coordinateur est l'agent principal de la session. Les autres rôles sont des fichiers TOML dans `.codex/agents/`.

| Rôle | Mission | Shell | Connecteurs et plugins | Écriture attendue |
| --- | --- | --- | --- | --- |
| Coordinateur | Besoin, tableau, missions, contexte, résultat final | Hérité | Hérités | Coordination et intégration autorisées |
| researcher | Rechercher, vérifier et citer | Hérité | Hérités | Retour au coordinateur |
| architect | Contrats et découpage depuis le paquet fourni | Désactivé | Désactivés | Retour au coordinateur |
| implementer | Réaliser une tâche de code | Hérité | Désactivés | Fichiers attribués dans son worktree |
| verifier | Reproduire les critères sur un SHA | Hérité | Désactivés | Aucun fichier suivi |
| reviewer | Revue indépendante d'un SHA | Hérité | Désactivés | Aucun fichier suivi |
| integrator | Assembler des candidats approuvés | Hérité | Désactivés | Intégration mandatée |

Les mémoires et la demande d'extension de permissions sont désactivées pour les spécialistes. Tous héritent du modèle et de l'effort de la session : le template n'impose pas un modèle susceptible d'être indisponible ou inadapté au budget.

## Restrictions effectivement appliquées

Quand le runtime charge ces agents personnalisés, `features.shell_tool = false`, `features.apps = false` et `features.plugins = false` désactivent les catégories correspondantes. Le chercheur garde les outils de documentation disponibles ; leur accès dépend de la session et des services connectés.

Les agents héritent des permissions de la session principale, de son fournisseur et de ses serveurs MCP. Désactiver les connecteurs applicatifs ne garantit pas l'absence de réseau : un shell peut avoir accès au réseau selon la politique de session, et les MCP peuvent être hérités.

Les instructions « lecture seule », les chemins possédés et l'interdiction de publication ne créent pas de sandbox par agent. Un reviewer doté du shell est techniquement capable d'écrire si la session le permet. Un nom de reviewer différent du worker est une vérification de cohérence du tableau, pas une preuve d'identité indépendante.

Pour des droits de sécurité différents, lancer des sessions ou conteneurs distincts avec un accès aux seuls répertoires et identifiants nécessaires. La création de ces environnements reste une extension du socle, décrite dans [la feuille de route](roadmap.md).

## Utilisation dans Codex

Demander au coordinateur de déléguer au rôle correspondant. Il utilise les outils de sous-agents réellement exposés par la session. Il doit donner le chemin du worktree dans la mission : un nouveau rôle ne crée pas automatiquement un checkout isolé.

Si les rôles personnalisés ne sont pas reconnus dans l'hôte utilisé, le coordinateur peut confier la mission avec les instructions du TOML, mais il doit signaler que les restrictions de capacités ne sont pas appliquées par ce simple prompt. En absence de sous-agents, le travail se poursuit en séquence ; une auto-revue n'est pas comptée comme revue indépendante.

Ajouter un nouveau rôle seulement pour une responsabilité répétée et distincte. Donner une mission, des entrées, une sortie et un périmètre. Un rôle « expert universel » augmente surtout le contexte et les ambiguïtés.
