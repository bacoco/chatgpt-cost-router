# GitHub MCP : refus lié au chat et reprise vérifiable

**Retour d'expérience du 20 septembre 2026.** Dépannage dans les interfaces
et permissions autorisées, pas contournement de sécurité ni réparation garantie.

## Constat et preuve

La conversation avait rapporté :

```text
FORBIDDEN: This conversation does not support developer MCPs
```

Une lecture réelle ultérieure avec **GitHub — chatgpt**, distinct du connecteur
GitHub standard, a réussi. Elle a été reproduite pendant cette documentation :
`GitHub_—_chatgpt.get_file_contents`, dépôt `bacoco/alfred-chatgpt`,
`instructions/README.md`, référence `refs/heads/main`.
Les 4 241 octets téléchargés donnent le SHA Git blob
`088b5ba0909c3bbf1c0b83df482553e550cb75e1`, recalculé et identique au retour outil.
[Reçu structuré](../audits/2026-09-20-mcp-conversation/read-recovery.json).

**Lecture rétablie : vérifiée. Cause attribuée à la branche : non démontrée.**
Une branche de conversation avait été proposée avant le succès, mais sa création
réelle dans l'interface n'est pas observée. Aucun journal serveur de l'échec ni
comparaison contrôlée entre chats n'est disponible. Ne pas transformer une
succession d'événements en preuve de causalité ou de réparation permanente.
Les écritures documentaires suivantes sont distinctes du test de lecture ;
aucune exécution planifiée n'a été testée dans ce retour d'expérience.

## Distinguer les erreurs

| Signal observé | Diagnostic prudent |
| --- | --- |
| `This conversation does not support developer MCPs` | Refus visant le contexte Chat ; vérifier sélection, compte et surface. Une nouvelle conversation autorisée est une piste. |
| `This conversation is restricted to developer MCPs` | Restriction inverse ; ne pas confondre intégration standard et MCP personnel. |
| Outils absents à la découverte | Appel non effectué, authentification du serveur non testée. |
| `403 — Resource not accessible by integration` | Vérifier l'action et les droits de l'intégration sur la ressource. Une branche ne donne aucun droit GitHub. |
| `401`, `404`, `429`, réseau ou `5xx` | Examiner respectivement authentification, existence/accessibilité, quota et transport. Pas de branche systématique. |
| Approbation requise, restriction administrateur ou sécurité | Respecter la procédure d'autorisation ; aucun nouveau chat pour l'éluder. |

## Procédure bornée

1. Conserver application exacte, outil, compte prévu, ressource et erreur réelle.
   Ne pas annoncer un appel quand seule la découverte a été tentée.
2. Vérifier la sélection de **GitHub — chatgpt** et la surface autorisée. Après
   correction de la sélection, permettre un seul retest minimal en lecture.
3. Si le refus de contexte persiste, ou si les outils restent absents après cette
   vérification, proposer **⋯ → Branch in new chat**, ou un nouveau chat si l'option
   manque. Respecter les restrictions du compte. C'est une **branche de conversation
   ChatGPT, pas une branche Git**. Aucun outil disponible ici ne crée cette branche.
4. L'utilisateur sélectionne le même plugin dans cette conversation et demande
   une lecture précise. Rapporter outil réel, résultat et SHA retourné. Recalculer
   le hash seulement si les octets et l'outil de calcul sont réellement accessibles.
5. Si le test échoue encore, arrêter les boucles ; conserver le diagnostic et
   préparer un signalement au support sans secrets. Pas de reconnexions répétées.

Le SHA historique identifie la version lue, pas une valeur que `main` doit garder.
Une lecture réussie ne prouve ni les écritures, ni le scheduler, ni la disponibilité
future. Avant de reprendre une mutation, relire son état : un envoi ou commit peut
avoir réussi malgré une réponse perdue. Conserver `UNCERTAIN` jusqu'à réconciliation.
Un nouveau chat ne remet pas à zéro l'identité ni l'historique de l'opération.

## Message utilisateur prévu

> Le refus vise l'utilisation du connecteur dans ce chat ; il ne prouve pas une
> perte de tes droits GitHub. Essaie une branche de cette conversation
> (⋯ → Branch in new chat), puis sélectionne GitHub — chatgpt et demande une
> lecture simple. C'est une piste de dépannage, pas un correctif garanti.

Ne pas afficher cette aide pour toute panne indistinctement.

## Modifier le plugin : faisabilité et limite

**Une consigne de reprise est réalisable ; un serveur non appelé ne peut pas
répondre lui-même à un refus de ChatGPT.** Si le blocage intervient avant l'appel
ou la découverte, un gestionnaire d'erreurs uniquement côté serveur est insuffisant.
C'est une limite d'architecture, pas une localisation prouvée de notre incident.

La [règle courte autonome](MCP_RECOVERY_INSTRUCTIONS.md) doit être copiée dans le
contexte de lancement ou les instructions du projet accessibles sans GitHub.
Un simple lien vers ce fichier ne suffit pas quand GitHub est indisponible.
Les métadonnées du plugin peuvent aussi porter l'aide si l'interface permet de les
éditer et si elles sont effectivement chargées. Conserver les consignes existantes.
Un pilote ou serveur sous notre contrôle peut traiter les erreurs qu'il observe,
mais il ne peut forcer l'hôte à exposer un outil ni modifier son interface.

Le [guide historique](BEGINNER_GITHUB_MCP_SETUP.md) décrit un serveur hébergé par
GitHub ; ce n'est pas une preuve d'accès à son code déployé ni aux réglages actuels.
Aucun outil de cette session ne permet d'éditer les instructions du plugin installé.
**Ces commits modifient les dépôts, pas le plugin, ses permissions ou son serveur.**

## Cas du scheduler

Le prompt du futur pilote doit contenir la règle de secours, pas seulement un lien.
Un blocage doit apparaître dans le résultat accessible ; ne pas déclarer le travail
terminé ni créer une nouvelle tâche. Un reçu privé n'est écrit que si le stockage
est accessible et autorisé. Ne pas prétendre ouvrir automatiquement un nouveau chat.
La reprise planifiée exige sa propre vérification et la réconciliation des effets.

## Références primaires et recette

Sources consultées le 20 septembre 2026 :
[OpenAI : dépannage des apps](https://help.openai.com/en/articles/20001497),
[branche de conversation, entrée du 4 septembre 2025](https://help.openai.com/en/articles/6825453-chatgpt-release-notes),
[apps MCP](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt-beta),
[instructions de serveur MCP](https://developers.openai.com/api/docs/mcp).
Elles documentent des capacités et pistes de dépannage, pas la cause de ce cas.

Recette future : lecture réussie, refus de contexte, outils absents, refus GitHub,
approbation, quota, écriture incertaine et blocage planifié. Vérifier que seule
l'erreur pertinente déclenche l'aide « nouvelle conversation », sans boucle ni
élargissement des droits. Cette recette n'est pas un test d'intégration déjà exécuté.
