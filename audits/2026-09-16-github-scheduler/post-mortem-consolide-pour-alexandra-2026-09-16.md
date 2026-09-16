# Écriture GitHub depuis ChatGPT : post-mortem consolidé pour Alexandra

> **Dernier résultat, MCP personnel déconnecté avant création de la tâche :** le test prévu à 10:22 a créé l’[issue #38](https://github.com/bacoco/loriq-watch-scheduler/issues/38) à 10:25:17 et l’a fermée à 10:25:23 avec GitHub standard. Sept appels, incluant README et fermeture, ont réussi. La fiche du MCP affichait « Installer le plugin » avant et après échéance ; sa définition est conservée. Une suspension initiale a nécessité « Reprendre » avant échéance. Voir `test-standard-mcp-deconnecte-20260916.md` pour les preuves et limites. Le MCP reste déconnecté.

> **Mise à jour après un nouveau test, le 16 septembre à 10:05 :** le parcours complet avec **GitHub standard uniquement** a réussi depuis une tâche prévue à 10:03 : lecture README, deux recherches, création, relecture, fermeture, relecture. L’[issue #36](https://github.com/bacoco/loriq-watch-scheduler/issues/36) a été créée à 10:05:18 et fermée à 10:05:27, heures et état vérifiés sur GitHub. Aucun MCP personnel utilisé. Le multi-appel et la lecture du README ne bloquent donc pas systématiquement ce parcours. La cause du premier refus reste inconnue. Voir `test-standard-complet-20260916-1003.md`. Le texte ci-dessous décrit l’état antérieur à ce nouvel essai.

16 septembre 2026 — Synthèse des observations recueillies jusqu’à environ 09:40, heure de Paris. Ce document remplace les conclusions provisoires des rapports précédents, conservés comme historique. Aucun nouveau test n’a été exécuté pour le rédiger.

## Les trois réponses à retenir

**Pourquoi cela fonctionnait chez Alexandra et semblait échouer chez Loïc ?** Les essais n’étaient pas équivalents. Alexandra décrit une tâche minimale : rechercher une issue, puis la créer si elle manque. Le premier essai chez Loïc ajoutait lecture du README, plusieurs recherches, relecture et fermeture. Une protection OpenAI a refusé la création. Nous ne savons pas quelle différence a déclenché ce refus. De plus, ce résultat est apparu avant l’heure programmée : il ne démontrait pas proprement une panne du scheduler.

**Pourquoi cela fonctionne maintenant ?** Deux parcours ont finalement réussi. Le connecteur GitHub standard a créé l’issue #32 avec une consigne simplifiée. Le MCP développeur, une fois ses outils disponibles dans un nouveau Chat où il était sélectionné, a créé l’issue #33 depuis une tâche planifiée, après l’heure prévue. Les deux essais ont ensuite retrouvé leur issue sans doublon. Cela établit des réussites concrètes, mais pas une cause unique de réparation : plusieurs paramètres ont changé entre les essais.

**Le compte GitHub était-il cassé ?** Aucune preuve ne l’établit. L’écriture standard fonctionnait déjà en conversation interactive. Le MCP a ensuite identifié le compte `bacoco` et écrit avec succès. Le refus initial citait la sécurité OpenAI, sans erreur GitHub 401/403 recueillie. Une éventuelle différence historique de connexion entre contextes n’a toutefois pas été entièrement retracée.

## Ce qui a réellement été testé

Toutes les heures ci-dessous sont celles de Paris, le 16 septembre 2026.

| Essai | Preuve et résultat | Ce que cela permet de conclure |
|---|---|---|
| Alexandra, connecteur standard | Son diagnostic rapporte un succès dans `Alexmacapple/ay11-pre-audit`, avec recherche puis création uniquement. | Succès rapporté par Alexandra. Son numéro d’issue et ses journaux d’exécution ne figurent pas dans les pièces reçues. |
| Navigateur GitHub chez Loïc | [#28](https://github.com/bacoco/loriq-watch-scheduler/issues/28), créée à 07:59:48, fermée à 08:00:03. | Le formulaire web fonctionne. Ce n’est pas un test du scheduler. |
| Conversations interactives standard | #30 puis #31 créées et fermées ; le second essai a été effectué en mode Chat explicitement vérifié. | Le connecteur sait écrire en Chat. Cela ne valide pas une exécution planifiée. |
| Premier essai standard complexe | Prévu à 08:28 ; refus produit vers 08:26–08:27. Aucune issue créée. | Refus de sécurité observé ; origine exacte du déclenchement et cause du refus non établies. |
| Premier essai MCP | Prévu à 09:07:18 ; dernière exécution enregistrée à 09:10:05. Résultat `OUTILS_MCP_ABSENTS`. | Aucun outil GitHub utilisable trouvé dans ce contexte ; aucune écriture tentée. Ce n’est pas une preuve de mauvais droits GitHub. |
| Standard minimal | [#32](https://github.com/bacoco/loriq-watch-scheduler/issues/32), créée à **09:24:43**, pour une échéance de **09:27**. | Écriture réelle, résultat associé à la tâche dans l’interface. L’exécution anticipée reste inexpliquée. |
| MCP sélectionné dans un nouveau Chat | [#33](https://github.com/bacoco/loriq-watch-scheduler/issues/33), créée à **09:28:09**, pour une échéance de **09:25**. | Parcours planifié MCP réussi : tâche visible avant échéance, résultat associé à la tâche, issue indépendante créée après échéance. |

L’ancienne issue #27 a été constatée visible et fermée ; sa création antérieure n’a pas été reproduite dans ces essais.

### Répétition et nettoyage

Les deux tâches finales ont été reprogrammées à **09:36**, chacune avec son prompt et son marqueur inchangés. Toutes deux ont retrouvé leur issue et répondu sans nouvelle création. La recherche indépendante n’a trouvé qu’une issue par marqueur.

- **MCP :** dernière exécution enregistrée à **09:37:34**, après échéance.
- **Standard :** dernière exécution enregistrée à **09:33:29**, de nouveau avant échéance.

Aucun bouton de lancement manuel n’a été utilisé. La tâche standard avait nécessité une réactivation avec « Reprendre » avant sa première exécution ; cette différence doit rester dans le diagnostic. Nous n’avons pas de journal interne expliquant les déclenchements anticipés.

Les fermetures ont été faites **séparément**, après le contrôle des doublons : #32 à 09:37:41, #33 à 09:38:50. Leur état final fermé a été relu indépendamment sur GitHub. Les tâches de test sont terminées, sans récurrence ; le MCP est conservé.

## Trois problèmes distincts avaient été mélangés

### 1. Un appel d’écriture refusé par la sécurité OpenAI

Le premier essai standard a retourné :

> This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.

Ce message établit un refus de sécurité de la plateforme. Il ne donne ni la règle déclenchée ni une réponse HTTP GitHub. Il ne permet donc pas de diagnostiquer un compte expiré, une permission manquante ou un README responsable.

### 2. Une installation MCP et une disponibilité des outils encore incomplètes

La création du connecteur a d’abord rencontré **un autre refus**, provenant du contrôle automatique des actions navigateur de Codex. Ce refus d’installation n’explique pas celui de la tâche standard.

Après validation par Loïc, l’application était indiquée connectée, mais ses actions n’étaient initialement pas visibles. La capture fournie à 09:12 montre ensuite des actions et « Autoriser toutes les actions ». Les contrôles ultérieurs ont confirmé les outils de lecture et d’écriture.

Il fallait distinguer trois étapes : **connexion créée → outils utilisables dans le Chat → outils utilisables lors de l’exécution planifiée**. La première ne prouvait pas les deux suivantes.

Le premier contexte MCP n’a pas trouvé les outils. Le nouveau Chat, ouvert avec l’application sélectionnée, a utilisé le namespace réel `GitHub_—_chatgpt`. Le chargement des actions, le contexte, les permissions observées et la référence aux outils ont évolué : nous n’avons pas isolé lequel de ces changements était décisif.

### 3. Des preuves de planification insuffisantes ou incohérentes

Une création d’issue en conversation ou dans le navigateur n’est pas une preuve d’exécution planifiée. Même un résultat associé à une tâche doit être confronté à l’heure prévue.

La chronologie finale du MCP est cohérente avec une exécution après échéance, deux fois. Celle du standard comporte deux avances inexpliquées. Aucun identifiant de run backend distinct ni journal HTTP brut n’a été obtenu. Nous pouvons attester le parcours MCP observé, sans promettre une précision horaire ni une fiabilité permanente.

## Ce que le diagnostic d’Alexandra confirme — et ce qu’il ne prouve pas

**Ses objections étaient fondées :** les protocoles différaient ; le premier horaire ne validait pas le scheduler ; un refus OpenAI ne démontrait pas une panne OAuth ; ajouter un MCP ne permettait pas d’expliquer à lui seul l’échec du connecteur standard.

Son hypothèse « lecture du README puis écriture » reste **plausible, non démontrée**. La série comparative qu’elle proposait — ajouter une seule étape à la fois : recherche des issues fermées, README, relecture, fermeture — n’a pas été exécutée de façon contrôlée. Le succès du test minimal ne permet pas d’accuser précisément le README.

Le test standard final reprend le principe de son test minimal, mais pas mot pour mot son titre et son corps. Il ne constitue pas une reproduction strictement identique de son environnement.

Le MCP répond à la demande de Loïc d’avoir une connexion durable et un parcours testé. **Il n’est pas démontré qu’il était nécessaire pour rétablir l’écriture**, puisque le standard a également créé #32. Le document du dépôt `chatgpt-cost-router` ne constituait pas non plus une preuve antérieure d’écriture planifiée : il indiquait une lecture planifiée réussie et l’écriture encore non testée.

## Mes erreurs dans la conduite et les comptes rendus

1. **J’ai commencé par tester les mauvaises étapes.** Navigateur et Chat répondaient à des questions partielles, alors que Loïc demandait surtout le scheduler. J’aurais dû rendre cette limite centrale immédiatement.
2. **J’ai surinterprété des résultats intermédiaires.** Un résultat avant échéance ne permettait pas d’annoncer le scheduler validé. Une application affichée connectée ne permettait pas d’annoncer ses outils opérationnels.
3. **La remise de la page de validation a échoué.** Loïc a vu une page blanche alors que le formulaire utile était dans un autre onglet. J’aurais dû vérifier l’onglet réellement présenté avant de lui demander d’intervenir.
4. **J’ai accumulé des rapports provisoires sans les remplacer assez clairement.** « Aucun outil », puis « connecté », puis « testé » concernaient des moments et des contextes différents. Présentés sans synthèse, ils donnaient des conclusions contradictoires.
5. **Je n’ai pas terminé l’analyse causale proposée par Alexandra.** Nous avons obtenu un parcours fonctionnel, mais pas identifié expérimentalement la cause du premier refus. Il fallait séparer ces deux objectifs.

## État final et questions encore ouvertes

**Vérifié :** compte MCP `bacoco`, lecture des métadonnées de `loriq-watch-scheduler` et `chatgpt-cost-router`, création planifiée MCP sur le premier dépôt, répétition sans doublon, fermeture vérifiée. Écriture standard et absence de doublon également constatées, avec réserve sur le déclenchement horaire.

**Non vérifié :** accès à tous les dépôts bacoco, remise en service de la veille de production, stabilité dans la durée, cause du refus initial et cause des exécutions anticipées standard. Aucune tâche de veille existante, aucun fichier, commit ou PR n’a été modifié par ces tests.

Pour comparer rigoureusement les deux environnements, il manque les preuves originales du succès d’Alexandra : URL de l’issue, prompt exact, heure prévue, heure de dernière exécution, connexion utilisée et réglages pertinents. Pour isoler le refus, il resterait ensuite à exécuter sa série comparative à une variable et à recueillir les traces de sécurité disponibles. **Ces investigations restent à faire ; ce document ne les présente pas comme réalisées.**

## Références pour le développeur

| Élément | Identifiant ou lien |
|---|---|
| Premier standard complexe | `6aaa36803d08819186922b599f725b05` |
| Premier MCP sans outils disponibles | `6aaa3ebeb0608191a48ac35eb1c9a41a` |
| Standard minimal final | `6aaa4349f0608191aacdd6363fae7822` — issue #32 |
| MCP final | `6aaa42f39e008191bd57f487573920b9` — issue #33 |
| Application MCP, identité stable | `asdk_app_6aaa3c09f1108191a103df830faa65b1` |
| Serveur déclaré | `https://api.githubcopilot.com/mcp`, OAuth |
| Chat standard | [Test d’écriture GitHub](https://chatgpt.com/c/6aaa3255-d3d0-83eb-b2a1-f7b95c2f0e77) |
| Chat MCP | [Vérification GitHub en lecture seule](https://chatgpt.com/c/6aaa41f3-edec-83eb-8c55-a3ba6ffda04e) |

Sources examinées : diagnostic d’Alexandra fourni par Loïc (« Diagnostic pour Loïc — pourquoi l’écriture GitHub planifiée ne marche pas », 16 septembre) ; `post-mortem-github-scheduler-2026-09-16.md` ; `complement-tests-mcp-2026-09-16.md`. Les pièces techniques associées sont `preuves-github-scheduler-2026-09-16.json` et `preuves-mcp-suite-2026-09-16.json`. Les réponses de modèles qui y sont conservées sont des comptes rendus, pas des journaux internes de la plateforme ; les relectures GitHub apportent la preuve indépendante des issues.
