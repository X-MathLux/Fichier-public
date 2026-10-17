# Ce qui complète le système

## Présent dans ce socle

Instructions Codex courtes, six spécialistes, quatre skills, préférences privées, contexte sourcé, dépendances, répartition sans conflit de fichiers, worktrees neufs, état atomique, limites de tentatives, revue liée au commit et contrôles du socle en CI.

La partie déterministe contrôle l'état et les conditions de distribution. Le jugement sur la qualité d'une recherche, l'indépendance réelle d'un agent et la pertinence d'un test reste vérifié par le coordinateur.

## Priorités au démarrage de chaque projet

1. **Critères utilisateurs mesurables** : le système doit savoir ce qui constitue une réussite.
2. **Contrats et tests de l'application** : ils donnent aux agents une cible commune et vérifient leur assemblage.
3. **Sources et décisions maintenues** : vérifier les hypothèses déterminantes et conserver les raisons des choix.
4. **Livraison reproductible** : installation, migration éventuelle, vérifications et retour.
5. **Évaluations d'agents** : rejouer les scénarios utiles après un changement majeur de workflow.

## Extensions lorsque l'usage le justifie

| Extension | Gain | Travail restant |
| --- | --- | --- |
| Sessions ou conteneurs par rôle | Droits système réellement distincts | Exécution, réseau et identifiants séparés ; validation des échanges |
| Mesures de coût et durée | Ajuster le nombre d'agents sur des données | Collecter l'usage réellement exposé par l'hôte ; aucun budget de tokens garanti aujourd'hui |
| Profils de stack éprouvés | Initialisation plus rapide | Créer et tester un profil après plusieurs usages réels, sans imposer une stack à tous |
| Adaptateur de CI applicative | Vérifier le produit à chaque PR | Installer les dépendances propres au produit et lancer ses checks |
| Suivi GitHub Issues ou Projects | Collaboration avec d'autres personnes | Choisir une source de vérité et une synchronisation unidirectionnelle au départ |
| Reprise programmée | Continuer plus tard sur un événement | Automation explicitement demandée, déclencheurs, état durable et condition d'arrêt |
| Suivi de production | Détecter les problèmes après livraison | Choisir les métriques et alertes réellement utiles, puis connecter le service |

Ajouter un moteur API externe seulement si les outils natifs de Codex ne couvrent plus le besoin. Cela introduirait clés, coûts, stockage de session et maintenance supplémentaires.

L'objectif est de rendre le travail reproductible et vérifiable. Multiplier les agents sans contrats ni preuves augmente surtout les conflits et le coût.
