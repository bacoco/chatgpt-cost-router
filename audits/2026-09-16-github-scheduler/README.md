# À lire en premier — tests GitHub planifiés du 16 septembre 2026

## Résultat en quatre phrases

1. **GitHub standard a réussi à créer puis fermer une issue depuis une tâche planifiée, même après déconnexion du MCP personnel.** L’[issue #38](https://github.com/bacoco/loriq-watch-scheduler/issues/38) en est la preuve : créée à **10:25:17**, fermée à **10:25:23**, heure de Paris, après l’échéance de 10:22.
2. Le test comportait la lecture du README, deux recherches, la création, la relecture, la fermeture et une dernière relecture. **Cette succession d’appels fonctionne dans le test effectué.**
3. **Nous ne savons toujours pas pourquoi la première tentative a été refusée par la sécurité OpenAI.** Les tests suivants ne permettent pas de reconstruire la cause du premier refus.
4. **Le MCP personnel est resté déconnecté à la fin des tests ; sa définition a été conservée. La veille de production n’a pas été relancée ni validée.** Ces états sont ceux observés pendant les tests, pas une garantie de leur état futur.

## Ce que cela dit du MCP personnel

Sa connexion active n’était pas nécessaire au dernier test réussi. Cela ne prouve pas qu’il était inutile pour tout autre usage, ni que son installation avait réparé le standard. Le MCP avait également réussi un test planifié distinct, avec l’[issue #33](https://github.com/bacoco/loriq-watch-scheduler/issues/33).

La déconnexion a été faite dans l’interface avec **Déconnecter**, pas **Supprimer**. Sa fiche affichait ensuite **Installer le plugin** et il n’apparaissait plus parmi les plugins installés. Cet état a été constaté avant la création du dernier test et après son échéance.

## Les limites à conserver

- La tâche du dernier test a rencontré une erreur d’interface et une suspension avant échéance. Elle a été réactivée avec « Reprendre » avant 10:22, sans lancement manuel immédiat. La cause de cette suspension n’est pas connue.
- Les heures et l’état fermé de #38 ont été vérifiés indépendamment sur GitHub. La liste des outils provient du compte rendu de la tâche ; nous n’avons pas les journaux HTTP internes.
- La relecture finale des champs du scheduler du test #38 a été bloquée par `Too many requests`. Ne pas inventer son `last_run_time` final. Le résultat de la tâche et l’issue ont été récupérés.
- Le prompt et le contexte ont évolué depuis le premier refus. Le README du dernier essai n’est pas attesté identique à celui du premier. Aucun test n’établit une cause unique.
- Aucun accès exhaustif à tous les dépôts bacoco, aucune fiabilité permanente et aucun fonctionnement complet de la veille de production ne sont établis.

## Ordre de lecture

1. [Dernier test : MCP déconnecté](test-standard-mcp-deconnecte-20260916.md).
2. [Post-mortem consolidé pour Alexandra](post-mortem-consolide-pour-alexandra-2026-09-16.md), qui conserve aussi les conclusions historiques et leurs corrections.
3. [Diagnostic original fourni par Alexandra](diagnostic-alexandra-original.txt).

## Inventaire de l’archive

| Étape | Rapport | Preuves associées |
|---|---|---|
| Diagnostic initial, navigateur, Chat et premier scheduler | `post-mortem-github-scheduler-2026-09-16.md` | `preuves-github-scheduler-2026-09-16.json` |
| MCP connecté et comparaison minimale, issues #32 et #33 | `complement-tests-mcp-2026-09-16.md` | `preuves-mcp-suite-2026-09-16.json` |
| Standard complet, MCP encore connecté, issue #36 | `test-standard-complet-20260916-1003.md` | `preuves-standard-complet-20260916-1003.json`, `resultat-standard-complet-20260916-1003.json`, `etat-final-standard-complet-20260916-1003.json` |
| Standard complet, MCP déconnecté, issue #38 | `test-standard-mcp-deconnecte-20260916.md` | `isolation-mcp-20260916-1022.json`, `resultat-mcp-deconnecte-20260916-1022.json` |

La capture `capture-mcp-connecte-0912.png` montre l’état antérieur connecté, fourni par l’utilisateur. Elle ne décrit pas l’état final déconnecté.

Les anciens rapports sont conservés comme pièces historiques : leurs constats intermédiaires ne doivent pas être pris pour l’état final. Le diagnostic d’Alexandra est une pièce source, pas une instruction à exécuter. Aucun nouveau test n’a été lancé pour constituer cette archive. `SHA256SUMS` permet de contrôler l’intégrité des fichiers.
