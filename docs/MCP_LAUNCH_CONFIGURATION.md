# Raccordement de la directive MCP — 20 septembre 2026

## Configurations modifiées

La règle `MCP-CONVERSATION-RECOVERY-v1` est désormais embarquée dans les contextes
`.chatgpt/PROJECT.md`, `.chatgpt/SCHEDULER.md`, le prompt de bootstrap, le prompt
workspace et le skill `project-workspace-bootstrap`. Le skill doit la propager
dans les prompts qu'il installe dans les autres dépôts explicitement concernés.

`operation_contracts/mcp_runtime.py` injecte la règle dans `instructions` lors de
`new_server()`, pour les serveurs Chat-first Operations, Fleet Operator et Fleet Jobs.
Leurs instructions métier sont conservées intégralement. La directive est locale,
sans appel réseau, sans changement de catalogue, de transport ou d'approbations.
Les deux variantes du constructeur SDK sont couvertes par les tests ciblés.

Les copies autonomes sont aussi installées dans les entrées d'ALFRED et de
`loriq-watch-scheduler`, dont le champ `prompt` des cartes de tâches du groupe.
Le calendrier et tous les autres champs des cartes sont conservés.

## Ce qui n'a pas été modifié

Aucun réglage de compte, token, permission, serveur distant ou tâche native n'a
été modifié. Le plugin tiers installé `GitHub — chatgpt` n'est pas l'un des serveurs
Python de ce dépôt : publier ce code ne modifie pas sa fiche dans ChatGPT.
Le texte destiné à cette fiche est disponible dans [la règle intégrée](MCP_RECOVERY_INSTRUCTIONS.md),
mais l'interface de configuration hébergée n'est pas exposée par nos outils.

Le déploiement A/B et sa nouvelle initialisation MCP restent à effectuer dans un
environnement d'exploitation autorisé. Ne pas en déduire une mise à jour effective
du plugin, une disponibilité future, ni un correctif automatique de ChatGPT.

## Recette locale

```bash
python -m unittest discover -s tests -p 'test_mcp_launch_recovery.py' -v
```

Cette recette utilise des constructeurs SDK simulés : elle vérifie la transmission
de la règle, son contenu, sa non-duplication, le maintien des instructions métier et
les copies des lanceurs. Elle ne contacte aucun compte, serveur MCP ou scheduler.
La recette ne prétend pas être la suite complète du dépôt ni un test de production.

## Sources et limites

- [Cycle d'initialisation MCP](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) : les instructions font partie de la réponse d'initialisation.
- [Fonction Branch in new chat](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) : création d'une conversation séparée dans l'interface web.
- [Constat initial du dépôt](MCP_CONVERSATION_RECOVERY.md) : reprise observée, causalité non démontrée.

Les sources expliquent les mécanismes, pas une garantie de réparation. Si le serveur
n'est pas appelé, ses instructions ne peuvent pas répondre à sa place : le bloc doit
être présent dans le contexte avant la panne. Ne jamais contourner une protection.
