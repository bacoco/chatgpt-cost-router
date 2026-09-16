# Test GitHub standard avec MCP personnel déconnecté

16 septembre 2026 — heures de Paris.

**Le test complet a réussi après déconnexion du MCP personnel.**

## Isolation réalisée avant création de la tâche

Dans les réglages du MCP `GitHub — chatgpt`, l'action **Déconnecter** a été utilisée, distincte de **Supprimer**. Le MCP a disparu des plugins installés. Sa fiche persistante, ID `asdk_app_6aaa3c09f1108191a103df830faa65b1`, affichait ensuite **Installer le plugin**. Cet état a été relu après l'échéance du test. La définition n'a pas été supprimée et le MCP n'a pas été reconnecté.

Le connecteur standard `GitHub` restait présent avec l'autorisation « Autoriser toutes les actions ». Une première requête de permissions par identifiant de catalogue ne l'a pas résolu ; la requête par nom exact et la liste de réglages ont confirmé sa présence. Aucune permission standard n'a été modifiée.

## Tâche et incident de planification

- Tâche : `6aaa507197188191910604c527d4be50`, TEST standard complet MCP déconnecté — 20260916-1022.
- Échéance : **10:22**, sans récurrence.
- Le prompt a été copié du test précédent, avec seulement les identifiants de test changés de `1003` à `1022`.
- Création rapportée activée à 10:16:50, `last_run_time: null`.
- L'interface a ensuite montré **Something went wrong** et une suspension avant échéance. Une relecture a confirmé `is_enabled: false`, `last_run_time: null`, `updated_at: 08:17:54.109527Z`. La cause de cet incident n'a pas été fournie.
- La même tâche a été réactivée avec **Reprendre**, avant échéance, puis constatée Planifiée. Aucun lancement manuel immédiat n'a été effectué. Cette réactivation est une différence par rapport au test #36 et doit rester documentée.

## Résultat vérifié

[Issue #38](https://github.com/bacoco/loriq-watch-scheduler/issues/38), titre `[TEST-SCHEDULER-STANDARD-FULL] 20260916-1022`, marqueur `standard-full-20260916-1022`.

| Événement | Heure Paris | Source |
|---|---|---|
| Échéance | 10:22:00 | Tâche enregistrée |
| Création #38 | **10:25:17** | Date de la page GitHub, concordante avec le compte rendu |
| Fermeture #38 | **10:25:23** | Date de l'événement GitHub, concordante avec le compte rendu |
| État final | **Closed / completed** | Page GitHub observée directement |

Le compte rendu de la tâche rapporte sept appels standard : `GitHub.fetch_file`, deux `GitHub.search_issues`, `GitHub.create_issue`, `GitHub.fetch_issue`, `GitHub.update_issue`, `GitHub.fetch_issue`. Deux découvertes de schémas ont également été rapportées, exclusivement pour le standard. Aucun outil du MCP personnel utilisé. SHA du README rapporté : `3310e7f51e123bc8d7c75ccbe31d99faea9f6505` (identifiant du fichier, pas preuve d'identité avec le README du tout premier échec).

La recherche avant échéance ne trouvait aucune issue pour ce marqueur. L'issue fermée a ensuite été vérifiée indépendamment par le navigateur. Celui-ci n'a effectué aucune écriture GitHub. Aucun fichier, commentaire, PR ou autre issue n'a été modifié par ce protocole.

## Conclusion et limites

**Le connecteur standard sait effectuer cette chaîne complète alors que le MCP personnel est déconnecté. La connexion active du MCP n'est donc pas nécessaire à ce succès.** Cela contredit une interdiction générale des appels GitHub multiples ou de la lecture d'un README avant écriture.

Ce test ne reconstitue pas l'environnement antérieur à l'installation du MCP et n'explique pas le premier refus de sécurité. Il ne prouve pas l'absence d'effets historiques persistants ni une fiabilité permanente. La suspension initiale reste inexpliquée. Le nom et l'ordre des outils proviennent du compte rendu ChatGPT, pas de journaux HTTP internes ; les dates et l'état de #38 ont une preuve indépendante GitHub.

Une limitation `Too many requests` de ChatGPT a temporairement bloqué la relecture finale, après la création et la fermeture réussies de #38. Le compte rendu a pu être récupéré ensuite. Le MCP reste déconnecté en fin de test ; sa fiche est conservée.

Preuves : `isolation-mcp-20260916-1022.json` et `resultat-mcp-deconnecte-20260916-1022.json`.
