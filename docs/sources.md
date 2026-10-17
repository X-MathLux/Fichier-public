# Sources et compatibilité

Vérification documentaire : **17 octobre 2026**. Le template est rédigé pour les capacités exposées par la documentation officielle à cette date ; la disponibilité concrète dépend du runtime et de ses permissions.

- [Agents personnalisés et sous-agents](https://learn.chatgpt.com/docs/agent-configuration/subagents) : fichiers TOML autonomes dans `.codex/agents/`, champs `name`, `description`, `developer_instructions`, héritage des permissions et capacités désactivables.
- [Configuration Codex](https://learn.chatgpt.com/docs/config-file/config-reference) : configuration de projet après confiance, activation des agents et limite de concurrence.
- [Instructions AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) : instructions de dépôt et portée par dossier.
- [Skills](https://learn.chatgpt.com/docs/build-skills) : découverte de `.agents/skills`, métadonnées et chargement progressif.

Aucun `sandbox_mode` par rôle, modèle figé, commande slash inventée ni ancienne déclaration d'agents n'est nécessaire ici. Les restrictions par rôle sont détaillées dans [agents.md](agents.md).

La validation locale vérifie le format et la cohérence des fichiers, pas l'exécution des six rôles par tous les hôtes Codex. Pour valider un hôte réel, ouvrir le projet, vérifier la découverte des skills et réaliser une mission sans effet externe avec un spécialiste. Rapporter la capacité réellement observée.

Les actions GitHub sont épinglées sur des commits vérifiés des dépôts officiels : [checkout v7.0.1](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1) et [setup-python v7.0.0](https://github.com/actions/setup-python/tree/5fda3b95a4ea91299a34e894583c3862153e4b97). Releases et références vérifiées le 17 octobre 2026. Dependabot propose leurs mises à jour.
