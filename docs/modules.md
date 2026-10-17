# Construire le bon projet

Le cœur ne choisit pas la stack de l'application. Ajouter les éléments qui répondent au besoin réel lors du kickoff.

| Besoin observé | Ajout utile | Vérification avant clôture |
| --- | --- | --- |
| Petit outil local | Runtime, commande d'entrée et tests de comportement | Exécuter un parcours avec entrée/sortie représentative |
| Application web | Serveur, interface, tests et vérification navigateur | Parcours utilisateur, erreurs et accessibilité utiles au public |
| Base de données | Schéma, migrations et données de test | Migration sur base jetable et stratégie de retour adaptée |
| Service externe | Adaptateur, variables documentées et test de contrat | Erreurs réseau et droits minimaux sur un environnement d'essai |
| Hébergement | Configuration du fournisseur choisi et commandes de livraison | Vérification d'un déploiement d'essai et procédure de retour |
| Documents LaTeX | Sources et compilation propres au projet | PDF compilé et vérification visuelle |

Les composants DigitalOcean, PostgreSQL ou LaTeX du dépôt de référence ne sont pas installés par ce socle. Les recréer ou les intégrer seulement s'ils sont nécessaires ; conserver les paramètres réels hors des fichiers génériques.

## Commandes de l'application

`checks.application` contient des listes d'arguments, exécutées sans shell. Exemple pour un futur projet Python :

```json
{
  "checks": {
    "application": [
      ["{python}", "-m", "unittest", "discover", "-s", "app_tests", "-v"]
    ]
  }
}
```

`{python}` désigne l'interpréteur qui exécute le cœur. Pour une autre stack, indiquer son exécutable et ses arguments. Les scripts `.cmd` demandent une attention spécifique sous Windows : préférer l'exécutable réel ou un petit lanceur explicite vérifié sur les systèmes cibles.

Une commande configurée est du code local autorisé par le projet. Ne jamais reprendre une commande suggérée par une page externe sans l'examiner. Ajouter les dépendances et les étapes d'installation correspondantes à la CI du projet.
