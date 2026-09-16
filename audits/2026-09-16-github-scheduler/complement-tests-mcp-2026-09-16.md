# Complément au post-mortem — MCP GitHub et tâches planifiées

État vérifié le 16 septembre 2026 vers 09:40. Les heures locales sont celles de Paris (UTC+2).

**Résultat : le MCP est connecté et son parcours de création d'issue planifiée fonctionne. Une seconde exécution retrouve l'issue et ne crée pas de doublon. Les deux issues de test sont fermées ; le MCP est conservé.** Le test standard minimal écrit aussi, mais ses horaires présentent une anomalie documentée ci-dessous. Les droits sur tous les dépôts bacoco n'ont pas été vérifiés exhaustivement.

## Évolution depuis le premier rapport

Le MCP **GitHub — bacoco (MCP développeur)** a été créé par validation de l'utilisateur. L'application porte l'identifiant `asdk_app_6aaa3c09f1108191a103df830faa65b1`, endpoint `https://api.githubcopilot.com/mcp`, OAuth. La capture utilisateur à 09:12 montre des actions exposées et « Autoriser toutes les actions ». L'ancien constat « aucune action » est donc historique, non l'état actuel.

## Premier test planifié : application non disponible dans le contexte testé

- Tâche : `6aaa3ebeb0608191a48ac35eb1c9a41a`, « TEST MCP bacoco — exécution automatique ».
- Échéance : 09:07:18. Création initialement annoncée activée ; une relecture l'a trouvée désactivée sans cause exposée. Réactivation de cette seule tâche, relue à 09:05:18 avec `is_enabled: true`, `last_run_time: null`.
- Relecture après échéance : `last_run_time: 2026-09-16T07:10:05.999980Z`, `is_enabled: false`.
- L'interface Planification affiche cette tâche terminée avec le résultat **OUTILS_MCP_ABSENTS**. Cela rattache visuellement le résultat à la tâche ; aucun identifiant de run backend distinct n'est disponible.
- Erreur de découverte : `No tool was defined under the given paths. Please try again with the correct paths.` Aucun outil GitHub invoqué, aucune issue créée. Recherche indépendante du marqueur `scheduler-mcp-bacoco-20260916-v1` : aucun résultat.
- Ce test échoue avant l'écriture. Il ne démontre pas que les droits GitHub sont insuffisants.

## Test interactif avec MCP explicitement sélectionné : lecture réussie

Depuis la fiche de l'application, « Essayer dans le chat » a ouvert un compositeur initialement en Work. Le mode **Chat** a été sélectionné et vérifié avant tout envoi, tout en conservant la pastille du MCP.

[Conversation de vérification](https://chatgpt.com/c/6aaa41f3-edec-83eb-8c55-a3ba6ffda04e).

Le résultat rapporte `GitHub_—_chatgpt.get_me` : login **bacoco**, ID **48750774**. Deux recherches de dépôts via `GitHub_—_chatgpt.search_repositories` ont retourné :

| Dépôt | ID | Permission rapportée |
|---|---|---|
| bacoco/loriq-watch-scheduler | 1359842396 | maintain: true |
| bacoco/chatgpt-cost-router | 1356755498 | maintain: true |

Aucune erreur d'authentification. Aucune écriture lors de ce contrôle. La disponibilité dans ce Chat ne prouve pas encore celle des tâches planifiées, ni la couverture de tous les dépôts bacoco. Le changement de contexte et le chargement des actions ont varié : l'attachement seul n'est pas établi comme cause unique.

## Comparaison planifiée suivante — création d'issues réussie

1. **MCP attaché v2**, tâche `6aaa42f39e008191bd57f487573920b9`, échéance 09:25. Création et relecture rapportent `is_enabled: true`, `last_run_time: null`. Le prompt cible le MCP et son namespace observé. L'outil de planification ne fournit pas de champ attestant la transmission de l'attachement.
2. **Connecteur standard minimal v2**, tâche `6aaa4349f0608191aacdd6363fae7822`, échéance 09:27 : recherche d'une issue ouverte puis création si absente, sans lecture de fichier ni fermeture. Création relue comme activée ; l'UI l'a ensuite affichée suspendue. Le bouton « Reprendre TEST standard minimal — bacoco v2 » a été utilisé pour réactiver cette seule tâche. Aucun bouton « exécuter maintenant » n'a été utilisé.

### Résultat MCP attaché v2

La tâche apparaît **Terminée** dans l'interface avec son résultat : namespace `GitHub_—_chatgpt`, appels `search_issues`, `list_issues`, puis `issue_write`. Le résultat annonce un début à 09:27:38 (fuseau non précisé dans cette phrase).

La relecture GitHub indépendante confirme [l'issue #33](https://github.com/bacoco/loriq-watch-scheduler/issues/33), titre `[TEST-SCHEDULER-MCP] bacoco 2026-09-16 v2`, marqueur `scheduler-mcp-bacoco-20260916-v2`, créée à **07:28:09 UTC / 09:28:09 Paris**, soit après l'échéance de 09:25. État initial observé : ouvert. Une relecture ultérieure du scheduler rapporte `last_run_time: 2026-09-16T07:28:23.618887Z` pour cette première exécution.

**Le parcours de création d'issue par une tâche ciblant le MCP développeur est désormais réussi.** Preuves : contexte Chat avec application sélectionnée, tâche créée et affichée planifiée avant échéance, résultat rattaché à cette tâche dans l'UI et artefact GitHub indépendant créé après échéance. Aucun identifiant de run backend distinct ni trace HTTP brute n'est fourni ; ne pas affirmer une précision d'exécution à la seconde.

### Résultat standard minimal v2 et anomalie d'horaire

La tâche apparaît **Terminée**, avec un résultat annonçant `GitHub.search_issues`, puis `GitHub.create_issue`. Relecture indépendante de [l'issue #32](https://github.com/bacoco/loriq-watch-scheduler/issues/32) : titre `[TEST-SCHEDULER-STANDARD] bacoco 2026-09-16 minimal`, marqueur `scheduler-standard-bacoco-20260916-minimal`, créée à **07:24:43 UTC / 09:24:43 Paris**. État initial : ouvert.

La relecture du scheduler rapporte `last_run_time: 2026-09-16T07:24:54.245656Z`, `is_enabled: false`, alors que l'horaire reste **09:27 Paris**. L'issue et la dernière exécution sont donc antérieures à l'échéance. L'écriture et son rattachement UI à la tâche sont établis ; le respect de la planification et la nature exacte du déclenchement restent inexpliqués. La réactivation UI est une différence de protocole à conserver dans l'analyse.

### État des conclusions

- Le compte GitHub authentifié par ce MCP fonctionne : identité, lecture et création d'issue réussies.
- Le connecteur standard sait également créer une issue avec le protocole minimal testé. Le premier refus de sécurité ne permettait pas de conclure à une impossibilité générale d'écriture planifiée.
- Le premier Chat ne disposait pas des outils du MCP ; le nouveau Chat avec sélection explicite les possède. Les actions ont été chargées et le contexte a changé entre les essais : causalité unique non isolée.
- Le nom affiché actuellement dans les réglages est **GitHub — chatgpt**, avec la connexion **GitHub — bacoco (MCP développeur)** et le même ID d'application. Le namespace `GitHub_—_chatgpt` est cohérent avec cet affichage.
- Les réglages exposent `get_me`, `search_issues`, `issue_write`, OAuth et « Autoriser toutes les actions ». Cela ne prouve pas une absence de contrôles de sécurité plateforme.
- L'hypothèse README → écriture n'a pas été isolée expérimentalement. Le succès du protocole minimal ne prouve pas que le README était la cause du refus initial.

## Contrôle de doublon et nettoyage réussis

Une seconde échéance ponctuelle à **09:36** a été enregistrée puis relue pour chacune des deux mêmes tâches, sans changement de prompt ni de marqueur ; `is_enabled: true` et horodatages des premières exécutions conservés. Modifications à 07:30:27 UTC (MCP) et 07:30:30 UTC (standard). Aucun nouveau scheduler récurrent n'est demandé. Le résultat attendu est NOOP avec l'issue existante. Les issues restent ouvertes pendant ce contrôle, puis leur fermeture sera vérifiée séparément. Le MCP doit rester installé.

Résultats obtenus :

- **MCP : NOOP avec #33**, heure rapportée **09:37:06 Europe/Paris**, seul outil GitHub annoncé `GitHub_—_chatgpt.search_issues`.
- **Standard : NOOP avec #32**, seul outil annoncé `GitHub.search_issues` ; l'outil ne retourne pas d'heure exacte de cet appel.
- Recherche indépendante après les deux réponses : **une seule issue par marqueur**, #32 et #33. Aucun doublon trouvé. Cette recherche s'appuie sur l'index GitHub ; elle complète les résultats NOOP, sans être une preuve exhaustive hors index.

La fermeture de #32 via le standard et de #33 via le MCP a été effectuée séparément après les résultats NOOP, avec contrôle du titre et du marqueur avant toute modification. Les états suivants ont été **relus indépendamment sur GitHub** :

| Issue | Création UTC | Fermeture UTC | État final |
|---|---|---|---|
| #32, standard minimal | 07:24:43 | 07:37:41 | closed / completed |
| #33, MCP développeur | 07:28:09 | 07:38:50 | closed / completed |

Les dernières relectures du scheduler rapportent :

| Tâche | Seconde échéance UTC | Dernier last_run_time UTC | État |
|---|---|---|---|
| MCP v2 | 07:36:00 | 07:37:34.199073 | is_enabled: false, aucune récurrence |
| Standard v2 | 07:36:00 | 07:33:29.077603 | is_enabled: false, aucune récurrence |

L'avance du standard se reproduit sur la seconde exécution. Le test MCP possède, pour les deux exécutions, des horodatages après échéance. Aucun bouton de lancement manuel n'a été utilisé. L'origine précise de l'avance du standard reste à faire examiner par le développeur ; le test ne justifie pas d'affirmer que toutes les tâches respectent leur horaire.

Le MCP n'a été ni supprimé ni déconnecté. Les tâches de test sont terminées et leur historique est conservé. Aucun fichier, commit, PR ou tâche de veille existante n'a été modifié au cours de ces tests.

## Portée de la validation

- **Vérifié :** disponibilité des outils du MCP, identité bacoco, lecture des métadonnées de deux dépôts, création par tâche planifiée MCP sur loriq-watch-scheduler, répétition sans doublon, fermeture et relecture de l'issue.
- **Vérifié avec réserve temporelle :** écriture et NOOP du standard, rattachés dans l'UI à sa tâche ; exécutions enregistrées avant leurs échéances.
- **Non établi :** cause exacte du premier refus OpenAI, rôle causal du README, accès exhaustif à tous les dépôts bacoco, robustesse à long terme ou fonctionnement de la veille de production. Le succès sur deux dépôts en lecture et un en écriture ne prouve pas une couverture universelle.

Pièce jointe : `preuves-mcp-suite-2026-09-16.json`, avec identifiants, prompts, réponses conservées et relectures finales. Les messages du modèle sont des comptes rendus ; ils ne sont pas présentés comme des journaux HTTP bruts.
