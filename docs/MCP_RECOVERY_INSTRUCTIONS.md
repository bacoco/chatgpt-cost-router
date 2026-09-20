# Règle MCP — intégrée aux sources et aux contextes de lancement

La règle ci-dessous est embarquée dans `.chatgpt/PROJECT.md`, `.chatgpt/SCHEDULER.md`,
les prompts de bootstrap/workspace et le skill qui initialise les autres projets.
`operation_contracts/mcp_recovery.py` la fournit également à `new_server()` :
Chat-first Operations, Fleet Operator et Fleet Jobs la reçoivent à l'initialisation.
Les copies sont contrôlées par `tests/test_mcp_launch_recovery.py`.

```text
[MCP-CONVERSATION-RECOVERY-v1]
Utilise le connecteur et le compte explicitement choisis par l'utilisateur.
Distingue outil absent et appel échoué ; rapporte l'erreur réellement observée.
Pour « This conversation does not support developer MCPs », « This conversation
is restricted to developer MCPs », ou des outils absents après sélection vérifiée,
en Chat interactif propose une branche de conversation ChatGPT autorisée
(⋯ → Branch in new chat), ou un nouveau chat autorisé, puis la sélection du même
plugin et un seul test de lecture minimale vérifiable. Pas une branche Git.
Ne présente pas cette piste comme un correctif garanti ni une cause démontrée.
Ne modifie pas les permissions et ne substitue pas un autre compte/connecteur.
Ne contourne aucune restriction administrateur, protection ou approbation explicite.
Ne confonds pas ce cas avec authentification, droits GitHub, quota ou approbation.
Si le retest échoue, arrête les boucles et conserve le diagnostic sans secrets.
Une lecture réussie ne valide ni les écritures ni les exécutions planifiées.
Réconcilie toute écriture incertaine avant reprise ; ne la rejoue pas aveuglément.
En tâche planifiée, signale le blocage dans le résultat disponible, sans créer
une tâche de remplacement ni prétendre avoir ouvert une nouvelle conversation.
Sauve un checkpoint seulement si le stockage reste accessible et autorisé.
```

## Déploiement et limites

Ces changements modifient les sources et modèles du dépôt, pas rétroactivement
les réglages d'une application installée, les tâches natives ni un serveur distant.
La fiche de `GitHub — chatgpt` dans ChatGPT n'est pas éditable par l'outil GitHub.
Sa configuration hébergée n'a pas été modifiée par ce commit. Ne pas annoncer
le contraire. Le texte ci-dessus est aussi le contenu autonome destiné au champ
d'instructions du plugin quand l'opérateur en dispose ; il n'ajoute aucun droit.

Le serveur A/B modifié transmet la règle via les instructions MCP lorsqu'il est
installé puis initialisé. Un refus de ChatGPT avant initialisation ne peut pas être
intercepté par ce serveur : le contexte de lancement doit donc embarquer la règle.
Un fichier sur GitHub n'est pas automatiquement une instruction chargée dans ChatGPT.

Voir [le raccordement et sa recette](MCP_LAUNCH_CONFIGURATION.md) et
[les observations initiales](MCP_CONVERSATION_RECOVERY.md).
