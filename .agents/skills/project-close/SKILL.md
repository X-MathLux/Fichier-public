---
name: project-close
description: Vérifier et clôturer une tâche substantielle de ce projet, après revue indépendante et intégration de son commit.
---

Lire le ticket et les preuves, puis `docs/operations.md` et `docs/release.md` si une livraison est demandée.
Vérifier le SHA candidat, les critères réellement satisfaits et le rapport indépendant lié à ce SHA.
Donner une disposition à chaque défaut : corrigé, rejeté avec preuve, ou suivi explicite. Un correctif de logique invalide la revue précédente.

Intégrer un candidat à la fois, sans prendre les changements d'un autre agent. Refaire les vérifications applicables sur l'assemblage.
Conserver les commandes et résultats, les décisions durables et les limites. Le coordinateur clôt via `task close` lorsque les conditions sont réunies.
Une action humaine restante devient une tâche ou une entrée de livraison, jamais une case implicitement terminée.

Rapporter résultat, tests, revue, état Git et travail restant. Une publication ou un déploiement suit le mandat utilisateur réel.
Si la revue indépendante est indisponible, dire que la clôture substantielle reste incomplète ; les petites corrections sans ticket gardent un contrôle proportionné.
