# Post-mortem provisoire — écriture GitHub depuis une tâche planifiée ChatGPT

> **Mise à jour du 16 septembre, après 09:37 :** ce document conserve l'état initial de l'investigation. Le MCP a depuis été connecté et testé : création planifiée de l'issue #33 et seconde exécution sans doublon réussies. Lire le [complément de tests](complement-tests-mcp-2026-09-16.md) pour l'état le plus récent et l'anomalie d'horaire du test standard.

Date : 16 septembre 2026. Heures en Europe/Paris (UTC+2).
Dépôt testé : `bacoco/loriq-watch-scheduler`, anciennement `bacoco/tech-watch-scheduler-factory`.
Destinataire : développeur disposant d’un environnement où le parcours fonctionne.

## Conclusion et question à résoudre

L’écriture GitHub fonctionne dans le navigateur et dans un Chat interactif sur ce compte. Un diagnostic de tâche planifiée a été créé et affiché comme terminé ; le résultat associé rapporte un refus de sécurité lors de `create_issue`. Aucune issue correspondant à son marqueur n’a été retrouvée.

**La cause racine n’est pas établie.** Il faut notamment vérifier si la tâche utilise la même connexion GitHub, la même identité et les mêmes autorisations que le Chat interactif. Une connexion ancienne, révoquée ou différente côté tâche reste une hypothèse. Les succès interactifs ne prouvent pas que la tâche dispose du même accès.

**Une réserve importante affecte le test planifié :** son résultat est antérieur à l’heure prévue et apparaît dans le même tour que la création. Sans identifiant de run ni traces backend, son origine automatique exacte et son mode d’exécution ne sont pas certifiés. L’affirmation précédente selon laquelle le scheduler avait été intégralement vérifié était trop forte.

Le MCP développeur demandé n’a pas été créé : sa configuration a rencontré un autre refus, provenant de la revue automatique des actions navigateur de Codex. Aucun test planifié via ce MCP n’a donc eu lieu.

## Environnement observé

| Élément | Observation et limite |
|---|---|
| Compte ChatGPT | Libellé « SICCRF-GESTION », offre « Pro » |
| Modèle affiché dans le Chat interactif | « 6 Pro » ; modèle backend du scheduler non attesté |
| Mode interactif | Radio « Chat » cochée lors du test #31, Work non sélectionné |
| GitHub | Compte bacoco ; issues de contrôle dans le dépôt cible |
| Connecteur standard | Plugin GitHub installé ; réglage visible « Tout autoriser » |
| Approbation générale des plugins | « Autoriser si faible risque » ; effet précis sur le scheduler inconnu |
| Mode Développeur | Déjà activé, non modifié |
| Connexion effective du scheduler | Identité, identifiant de connexion et portée OAuth non récupérés |
| MCP développeur GitHub souhaité | Durable, pour les dépôts bacoco publics et privés ; non créé |

Codex a piloté le navigateur, demandé la création de la tâche dans ChatGPT, puis relu les preuves. Les relectures indépendantes depuis Codex vérifient les artefacts GitHub ; elles ne prouvent pas les capacités du scheduler.

## Tests réalisés et portée des résultats

| Test | Preuve | Résultat et portée |
|---|---|---|
| Issue antérieure #27 | Vue dans l’UI GitHub, fermée | Création non exécutée pendant cette investigation ; pas de preuve scheduler |
| Navigateur #28 | Création par formulaire web, vérification, fermeture et relecture | Parcours GitHub web réussi |
| Chat interactif #30 | Réponse du Chat et relecture indépendante de l’issue | Écriture interactive réussie ; conversation ensuite supprimée par l’utilisateur |
| Nouveau Chat interactif #31 | Mode Chat observé, réponse et relecture indépendante | Écriture interactive réussie |
| Diagnostic planifié | Tâche visible, résultat associé et recherche indépendante du marqueur | Refus rapporté à la création ; provenance backend du run à confirmer |
| MCP développeur | Formulaire préparé, action de création refusée | Installation et test non réalisés |

Les premiers tests ne répondaient pas à la question du fonctionnement en tâche planifiée. Ils constituent seulement des contrôles permettant de comparer les surfaces.

### Artefacts GitHub vérifiés

- [#28 — TEST-BROWSER](https://github.com/bacoco/loriq-watch-scheduler/issues/28) : créée à **07:59:48**, fermée à **08:00:03**.
- [#30 — TEST-CHAT](https://github.com/bacoco/loriq-watch-scheduler/issues/30) : créée à **08:03:43**, fermée à **08:03:57**.
- [#31 — TEST-CHAT-RETRY](https://github.com/bacoco/loriq-watch-scheduler/issues/31) : créée à **08:08:45**, fermée à **08:08:56**.

Ces trois issues ont été relues indépendamment : état `closed`, motif `completed`. Leurs corps et horodatages UTC figurent dans le JSON joint.

## Diagnostic planifié : détails exploitables

[Conversation « Test d’écriture GitHub »](https://chatgpt.com/c/6aaa3255-d3d0-83eb-b2a1-f7b95c2f0e77).

| Champ | Valeur |
|---|---|
| Titre | Diagnostic scheduler Chat — GitHub standard — 16 septembre |
| ID de tâche, rapporté par ChatGPT | `6aaa36803d08819186922b599f725b05` |
| Horaire annoncé | 16 septembre 2026, 08:28 Paris / 06:28 UTC |
| Planification annoncée | Ponctuelle ; `timing_mode: exact_schedule` |
| État annoncé à la création | `is_enabled: true`, `last_run_time: null` |
| Marqueur unique | `scheduled-chat-github-standard-20260916-0828` |
| Titre d’issue prévu | `[TEST-SCHEDULER-CHAT] GitHub standard 2026-09-16 0828` |
| ID du tour contenant création et résultat | `42edea7a-f8f9-4f38-bd41-d470769ac6ee` |
| ID du message de création | `f3552d17-2353-4d51-b50b-e22587fb242e` |
| ID du message de résultat | `926908ac-4628-4343-9389-9a10fdea98ed` |
| ID de run backend | Non obtenu |

Instructions : utiliser uniquement le connecteur GitHub standard, lire README.md, chercher le marqueur dans les issues ouvertes et fermées, créer une seule issue si absente, la relire, la fermer et confirmer l’état final. Aucun lancement manuel demandé. Le texte exact est conservé dans le JSON joint.

### Résultat rapporté par ChatGPT

1. Lecture de README.md réussie ; SHA retourné `de31e7f2b616fb97b9b8f7b622d1523478ec9ee1`. Il s’agit du SHA de fichier retourné, pas d’un commit de branche vérifié.
2. Recherche dans les issues ouvertes puis fermées : aucun résultat.
3. Tentative `create_issue` refusée avec le texte :

> This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.

4. Aucune URL retournée ; relecture et fermeture non réalisées.

Les outils sont rapportés dans le texte du Chat : `fetch_file`, `search_issues` deux fois, `create_issue`. Les réponses brutes de ces appels ne sont pas disponibles dans l’export. Une recherche indépendante du marqueur n’a trouvé aucune issue ; un éventuel délai d’indexation limite cette preuve négative.

Le message indique un refus de sécurité OpenAI. Il **ne prouve ni une révocation OAuth, ni l’absence d’envoi vers GitHub** : aucun statut HTTP, identifiant de requête GitHub ou journal de transport n’a été obtenu.

### Anomalie de chronologie à résoudre avant toute conclusion

La création est annoncée à 08:26:08 pour 08:28. Pourtant, le tour contenant création et résultat commence à **08:25:37.109** et se termine à **08:27:23.721**. Le résultat lui-même annonce une exécution vers 08:26–08:27.

L’interface a affiché temporairement « Suspendue / Reprendre », puis « Terminée ». Aucun clic de lancement manuel ou de reprise n’a été effectué par l’opérateur. Aucun suffixe « Work » n’apparaissait sur cette tâche, mais cela ne certifie pas le mode backend. L’outil de création, d’après la réponse ChatGPT, n’attestait pas non plus ce mode.

À déterminer : exécution anticipée, contenu exécuté pendant le tour de création, regroupement de messages ou horodatage de présentation. Aucune de ces explications n’est démontrée.

## Second blocage : installation du MCP développeur

Formulaire préparé : **GitHub — bacoco (MCP développeur)**, endpoint `https://api.githubcopilot.com/mcp`, authentification OAuth.

La revue automatique de l’action navigateur Codex a refusé la création :

> This action was rejected due to unacceptable risk.

Motif exact :

```text
This acknowledges an unreviewed high-risk server and creates a persistent custom MCP at api.githubcopilot.com with potentially broad GitHub access across bacoco repositories; the user requested a durable developer MCP but did not specifically authorize this exact unverified endpoint and access scope.
```

C’est le motif formulé par cette revue, et non une preuve que GitHub ou son serveur officiel seraient défectueux. Aucun consentement OAuth GitHub n’a été atteint. Les permissions effectives n’ont donc pas été vérifiées. La confirmation précise demandée ensuite n’a pas reçu de réponse ; aucune tentative de contournement n’a été effectuée.

Ce refus est distinct du message obtenu lors du diagnostic d’écriture.

## Ce que prouve le dépôt « cost »

Le [guide GitHub Developer MCP](https://github.com/bacoco/chatgpt-cost-router/blob/main/docs/BEGINNER_GITHUB_MCP_SETUP.md), relu au SHA de fichier `d3c2c7c6aaeef7c3df072b7d0fe0737517566e86`, documente au 10 septembre :

- T07 : lecture authentifiée planifiée réussie avec un Developer MCP.
- T08 : écriture planifiée avec déduplication **NOT YET TESTED**.
- Un refus historique distinct : `FORBIDDEN: This conversation is restricted to developer MCPs`.

Ces résultats historiques n’établissent pas que le Developer MCP résoudra l’écriture planifiée ici. Le problème de slash final évoqué dans le guide n’a pas de causalité démontrée. Le [serveur GitHub MCP officiel](https://github.com/github/github-mcp-server#remote-github-mcp-server) documente l’endpoint distant GitHub ; cela ne valide pas notre connexion OAuth, qui n’a pas été créée.

## Priorités pour le développeur dont l’environnement fonctionne

| Priorité | Comparaison à réaliser | Preuve attendue |
|---|---|---|
| 1 | Même compte et même connexion dans Chat et scheduler ? Connexion ancienne ou révoquée ? | Identité GitHub authentifiée, ID de connexion/app, état d’autorisation et sélection des dépôts ; jamais les jetons |
| 2 | Le résultat provient-il réellement d’un déclenchement automatique ? | ID de run, événement de déclenchement, horaires backend, lien avec le message de résultat |
| 3 | Quel connecteur est réellement appelé de chaque côté ? | Standard ou Developer MCP, identifiant exact et nom d’outil ; ne pas se fier au seul libellé GitHub |
| 4 | Où le refus apparaît-il ? | Arguments expurgés, réponse brute, identifiant de contrôle OpenAI et statut/request-id GitHub s’il existe |
| 5 | Quelles permissions diffèrent ? | Portée OAuth, accès au dépôt privé, autorisations par outil et politique propre aux exécutions sans utilisateur présent |
| 6 | Quelles autres conditions diffèrent ? | Offre/espace ChatGPT, modèle effectif, mode backend, prompt enregistré, version des outils et annotations de lecture/écriture |

**Hypothèse du compte non fonctionnel :** incompatible avec une panne générale du compte utilisé pour #31 à 08:08, mais compatible avec une connexion différente ou devenue invalide utilisée plus tard par la tâche. Une lecture et une recherche réellement réussies dans ce même run rendraient une absence totale d’accès moins probable ; elles ne prouveraient toujours pas le droit d’écriture.

Ne pas reconnecter ou remplacer l’app avant d’avoir relevé les identifiants et états actuels : cette modification ferait disparaître une partie de la comparaison recherchée.

## Protocole de reprise proposé — non exécuté

1. Collecter d’abord les preuves ci-dessus dans les deux environnements.
2. Comparer un test interactif et un test ponctuel réellement déclenché par le scheduler, sur le même dépôt et le même connecteur. Utiliser un marqueur dédié par comparaison.
3. Conserver le prompt, l’heure prévue, l’ID de tâche, l’ID de run et les réponses d’outils. Vérifier indépendamment création, relecture, fermeture et horodatages de l’issue.
4. Tester séparément le Developer MCP après création et authentification effectives ; ne pas attribuer au MCP un résultat du connecteur standard.
5. Pour valider la déduplication, répéter le même diagnostic avec le même marqueur : aucune seconde issue ne doit apparaître.

Critère de résolution : un run automatique identifié réalise création → relecture → fermeture → relecture finale, avec preuves GitHub corrélées, puis une répétition sans doublon. L’accès à tous les dépôts bacoco exige en plus une vérification de couverture des permissions ; un seul dépôt ne le démontre pas.

## Pièce jointe et limites de conservation

`preuves-github-scheduler-2026-09-16.json` contient les issues relues, les messages et prompts exacts de la conversation restante, les identifiants et des notes d’observation UI. Les messages du modèle y sont explicitement distingués des traces backend absentes. Aucun jeton ni secret n’y figure.

Aucune capture d’écran n’est jointe. La conversation du test #30 a été supprimée ; son issue reste vérifiable. Le présent rapport ne constitue ni une correction déployée ni une validation du MCP ou du scheduler.
