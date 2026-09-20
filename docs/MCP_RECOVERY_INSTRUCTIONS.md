# Règle de secours MCP — texte prêt à intégrer

**À copier dans les instructions du projet ou le prompt de lancement.**
Ce document n'a pas été installé dans les réglages du plugin ou de ChatGPT.
Le texte doit être accessible sans un premier appel à GitHub : un lien seul
ne suffit pas lorsque GitHub est justement bloqué.

```text
Utilise le connecteur et le compte explicitement choisis par l'utilisateur.
Distingue outil absent et appel échoué ; rapporte l'erreur réellement observée.
Pour « This conversation does not support developer MCPs », ou des outils encore
absents après sélection vérifiée, propose une branche de conversation ChatGPT
(⋯ → Branch in new chat), ou un nouveau chat autorisé, puis la sélection du même
plugin et une lecture minimale vérifiable. Pas une branche Git.
Ne présente pas cette piste comme un correctif garanti ni une cause démontrée.
Ne modifie pas les permissions, ne substitue pas un autre compte/connecteur et
ne contourne aucune restriction administrateur ou protection explicite.
Ne confonds pas ce cas avec authentification, droits GitHub, quota ou approbation.
Après correction de la sélection, un seul retest en lecture ; si l'échec persiste,
arrête les boucles et conserve le diagnostic pour le support, sans secrets.
Une lecture réussie ne valide ni les écritures ni les exécutions planifiées.
Réconcilie toute écriture incertaine avant reprise ; ne la rejoue pas aveuglément.
En tâche planifiée, signale le blocage sans créer de tâche de remplacement ni
prétendre avoir ouvert une nouvelle conversation.
```

## Petit test de lecture

```text
Utilise uniquement GitHub — chatgpt, avec le compte prévu.
Lis instructions/README.md dans bacoco/alfred-chatgpt, refs/heads/main.
Donne l'outil réellement appelé, le résultat et le SHA s'il est retourné.
Ne change aucun fichier, compte, connecteur, permission ou tâche.
```

[Constat, limites et procédure](MCP_CONVERSATION_RECOVERY.md).
Une description de plugin aide seulement si elle a été chargée ; cette règle
n'accorde aucun pouvoir supplémentaire à un serveur ou au modèle.
