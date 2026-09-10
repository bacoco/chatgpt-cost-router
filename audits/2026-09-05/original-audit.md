# Audit de chatgpt-cost-router

**Dépôt examiné :** [bacoco/chatgpt-cost-router](https://github.com/bacoco/chatgpt-cost-router/tree/ca763e51842cb1b53452fb41464232600572c6cd) — branche `main`, commit `ca763e51842cb1b53452fb41464232600572c6cd` (4 septembre 2026). Revue réalisée le 5 septembre 2026.

**Conclusion : le dépôt constitue un début de spécification, pas encore un routeur opérationnel.** Les 13 fichiers suivis ont été lus intégralement : 638 lignes logiques, 12 fichiers Markdown et un schéma JSON. Il contient deux skills de 21 et 6 lignes, dix fixtures en prose, aucune application exécutable, aucun serveur MCP, aucun test automatisé ou workflow CI. L’absence du moteur est explicitement annoncée dans la roadmap; elle n’est pas comptée comme un bug caché.

**Résultat : 4 défauts de format ou de contrat (F01–F04), 3 lacunes documentées de routage/évaluation/preuve (F05–F07), puis 8 questions de conception avant implémentation (D01–D08).** Les six premiers constats sont de priorité P2 et F07 de priorité P3. Aucun incident critique, crash, fuite de données ou contournement de sécurité en fonctionnement n’a été établi.

**Méthode et portée.** Skill ShipGuard `sg-ship` trouvé dans une copie locale du dépôt ShipGuard, puis application de ses principes : périmètre figé, contrats explicites, contre-exemples, séparation du mesuré et du raisonné, relecture indépendante et rapport unifié. Une seconde revue a lu les 13 fichiers et tenté de réfuter les constats. Adaptation nécessaire : les contrôles applicatifs, avant/après et visuels sont non applicables à ce dépôt. Le tableau de bord n’équivaut pas à un passage end-to-end de ShipGuard sur une application.

| Vérification | Résultat effectivement établi |
|---|---|
| Accès GitHub + clone de main | Même SHA, arborescence récursive complète; tous les fichiers suivis lus |
| Validateur de skills officiel local | 2 contrôles exécutés, 2 échecs : `No YAML frontmatter found` |
| Schéma JSON | JSON parsé; propriétés, champs requis et exemple comparés par script |
| Validation normative de paquets JSON | Raisonnée à partir du schéma; `jsonschema` et AJV indisponibles, aucun moteur de remplacement improvisé |
| Fixtures | 10 cas lus et confrontés aux prérequis; aucun test du routeur exécuté |
| Scénarios adverses | 19 scénarios recensés; 1 scénario de format mesuré (2 fichiers), 18 raisonnés |
| Application, UI, coûts réels, passerelles | Non testés : aucune implémentation dans le périmètre |
| Modifications du dépôt distant et des sources | Aucune; aucune issue, PR ou correction publiée |

**Constats prioritaires**

| ID | Priorité | Constat | Nature de la preuve |
|---|---|---|---|
| F01 | P2 | Les deux skills ne respectent pas le format de métadonnées | Validation de format mesurée |
| F02 | P2 | Le producteur de handoff peut omettre la version exigée par le schéma | Lecture complète et contre-exemple raisonné |
| F03 | P2 | Le schéma laisse les champs de contexte et de contrôle sans validation | Lecture complète et contre-exemple raisonné |
| F04 | P2 | Un handoff sans objectif ni critère de réussite satisfait le schéma | Lecture complète et contre-exemple raisonné |
| F05 | P2 | Le vocabulaire des routes et les routes composites ne sont pas stabilisés | Lecture complète et contre-exemple raisonné |
| F06 | P2 | Les dix fixtures ne permettent pas de mesurer un accord de routage reproductible | Lecture complète et contre-exemple raisonné |
| F07 | P3 | Les observations de capacités ne sont pas reliées à leurs preuves | Lecture complète et contre-exemple raisonné |

**F01 — Les deux skills ne respectent pas le format de métadonnées**

[skills/capability-router/SKILL.md:1](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L1), [skills/surface-handoff/SKILL.md:1](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/surface-handoff/SKILL.md#L1)

Les deux fichiers commencent par un titre Markdown et ne contiennent pas de frontmatter YAML avec name et description. Le validateur local officiel quick_validate.py renvoie pour chacun le code 1 et « No YAML frontmatter found ». Cela bloque leur conformité au format de skill natif. Leur lecture manuelle depuis GitHub reste possible.

**Contre-exemple / preuve :** Valider séparément chacun des deux répertoires de skills avec quick_validate.py : les deux contrôles échouent avant toute invocation du skill.

**Correction proposée :** Ajouter les métadonnées aux deux skills, définir leurs conditions de déclenchement et documenter la méthode d’installation ou de chargement depuis GitHub.

**Vérification après correction :** Les deux validations de format passent; vérifier ensuite séparément découverte et invocation sur la surface cible. Un format valide ne démontre pas que le skill a été exécuté.

**F02 — Le producteur de handoff peut omettre la version exigée par le schéma**

[skills/surface-handoff/SKILL.md:3–6](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/surface-handoff/SKILL.md#L3-L6), [schemas/handoff.schema.json:5–7](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L5-L7), [docs/HANDOFF_SPEC.md:5](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L5)

Le skill énumère les informations à produire mais omet version et ne renvoie ni au schéma ni à un exemple canonique. Le schéma impose version=1. L’exemple documentaire contient bien la version, ce qui ne corrige pas le contrat du skill chargé seul.

**Contre-exemple / preuve :** Un producteur fournit tous les champs demandés par le skill, avec recommended_surface, remaining et success_criteria, mais sans version : la condition required du schéma est violée. Il ne s’agit pas d’une sortie LLM effectivement observée.

**Correction proposée :** Faire du schéma une référence explicite du skill, fournir un exemple valide et exiger sa validation avant remise du handoff.

**Vérification après correction :** Un paquet sans version est rejeté; le paquet canonique généré selon le skill est accepté; une version inconnue est traitée explicitement.

**F03 — Le schéma laisse les champs de contexte et de contrôle sans validation**

[schemas/handoff.schema.json:5–14](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L5-L14), [docs/HANDOFF_SPEC.md:6–18](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L6-L18), [skills/surface-handoff/SKILL.md:4](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/surface-handoff/SKILL.md#L4)

Sept champs de l’exemple ne sont pas déclarés dans properties : task_id, from_surface, repo, files, constraints, tests et return_to_chat_when. Le skill demande aussi une branche et une raison d’escalade sans définir leurs clés JSON. Ces champs peuvent être absents ou porter n’importe quel type. Aucun autre contrat ou validateur n’existe dans les 13 fichiers suivis. Le schéma ne prouve donc pas la conservation des contraintes et des informations nécessaires à la reprise.

**Contre-exemple / preuve :** Ajouter à un paquet minimal par ailleurs conforme : {"repo":[],"constraints":null,"tests":42,"return_to_chat_when":false}. Ces valeurs ne sont soumises à aucune contrainte par le schéma actuel. Une faute de frappe dans un de ces champs facultatifs n’est pas détectée non plus.

**Correction proposée :** Déclarer et typer tous les champs connus; définir lesquels sont obligatoires selon le sens du transfert et la tâche. Décider séparément si les extensions inconnues restent autorisées. Ne pas simplement ajouter additionalProperties:false avant d’avoir déclaré les champs de l’exemple.

**Vérification après correction :** Tester les mauvais types et l’omission des champs indispensables; l’exemple complet doit continuer à être accepté. Tester les différences entre transfert vers un spécialiste et retour après achèvement.

**F04 — Un handoff sans objectif ni critère de réussite satisfait le schéma**

[schemas/handoff.schema.json:9–13](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L9-L13), [skills/capability-router/SKILL.md:3](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L3), [SPEC.md:7](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L7)

goal est seulement une chaîne; success_criteria est seulement un tableau de chaînes. Aucun minimum ni contrôle de contenu non blanc n’est prévu. Le contrat de structure accepte donc un paquet inutilisable pour définir ou vérifier la mission.

**Contre-exemple / preuve :** {"version":1,"goal":"","recommended_surface":"CODEX","remaining":[],"success_criteria":[]} satisfait les contraintes déclarées. Des chaînes constituées uniquement d’espaces restent également possibles. Attention : remaining=[] est légitime lors d’un retour de tâche terminée; ce n’est pas, à lui seul, un défaut.

**Correction proposée :** Exiger un objectif non blanc et des critères de réussite exploitables, avec règles adaptées aux handoffs terminaux. Les seules contraintes de longueur ne suffisent pas pour rejeter les espaces.

**Vérification après correction :** Rejeter objectif vide ou blanc et critères absents de sens; conserver un retour valide avec remaining=[] et des preuves d’achèvement.

**F05 — Le vocabulaire des routes et les routes composites ne sont pas stabilisés**

[SPEC.md:10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L10), [schemas/handoff.schema.json:8](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L8), [skills/capability-router/SKILL.md:8](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L8), [docs/ARCHITECTURE.md:11](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ARCHITECTURE.md#L11), [tests/routing_cases.md:8–12](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md#L8-L12)

Le contrat machine utilise LOCAL_TOOL alors que le skill et l’architecture utilisent LOCAL/MCP. HYBRID est autorisé par le schéma mais ne possède ni règle de sélection ni structure décrivant ses composants. Les fixtures comportent aussi un transport, une composition et un choix entre plusieurs surfaces. Les abréviations de prose ne démontrent pas une erreur de sérialisation déjà produite; elles signalent un contrat encore incomplet.

**Contre-exemple / preuve :** Si LOCAL/MCP est sérialisé tel quel dans recommended_surface, il est hors enum. À l’inverse, HYBRID est dans enum mais ne dit pas si le travail doit être planifié, calculé localement, ni dans quel ordre. La fixture « MCP + SCHEDULED_CHAT » n’apporte pas ce modèle.

**Correction proposée :** Utiliser un vocabulaire canonique unique et documenter les alias de présentation. Soit définir HYBRID avec étapes, ordonnanceur, exécutants et dépendances, soit le retirer tant qu’il n’est pas pris en charge.

**Vérification après correction :** Chaque route de sortie et chaque fixture se normalise sans ambiguïté; un plan hybride contient assez d’information pour être exécuté.

**F06 — Les dix fixtures ne permettent pas de mesurer un accord de routage reproductible**

[tests/routing_cases.md:3–12](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md#L3-L12), [SPEC.md:25](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L25), [skills/capability-router/SKILL.md:20](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L20)

Chaque fixture contient une tâche et une préférence de surface, mais aucune photographie des capacités, autorisations, contraintes utilisateur ou conditions de disponibilité. Les cas 6, 8 et 10 mêlent route, moyen de transport, composition et alternatives. Ces dix lignes sont des exemples humains, pas des tests exécutés ni un oracle suffisamment défini pour calculer le >90% annoncé.

**Contre-exemple / preuve :** La fixture 2 attend CHAT pour créer une issue. Une session Chat sans outil GitHub de création, ou sans autorisation d’écriture, ne peut satisfaire ce résultat tout en respectant l’obligation de preuve runtime. Les conditions permettant de distinguer les deux situations ne sont pas dans la fixture.

**Correction proposée :** Transformer les cas en données structurées : tâche, surface courante, capacités vérifiées et leurs portées, restrictions, sorties acceptées, motif et plan. Ajouter les variantes outil absent, lecture seule, authentification expirée et instruction de ne pas escalader.

**Vérification après correction :** Deux évaluateurs recevant la même politique et les mêmes capacités obtiennent une attente comparable. Le taux d’accord doit indiquer le dénominateur et les cas exclus.

**F07 — Les observations de capacités ne sont pas reliées à leurs preuves**

[docs/ARCHITECTURE.md:23–26](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ARCHITECTURE.md#L23-L26), [README.md:100](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L100), [schemas/handoff.schema.json:12](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L12)

La liste PASS / NOT EXPOSED / FAIL ne donne ni date, environnement, surface confirmée, compte ou portée de connexion, étapes du test, ni référence vers le résultat. Aucun procès-verbal de ces audits n’est présent parmi les fichiers suivis. Le README demande correctement une revérification runtime : le défaut est la traçabilité des observations historiques, pas une instruction de les croire universelles.

**Contre-exemple / preuve :** Une nouvelle session lit « GitHub read/write PASS » : ce document ne permet pas de savoir quelle action, quel dépôt et quel environnement ont réellement été vérifiés.

**Correction proposée :** Joindre un manifeste de capacités daté, contextualisé et sourcé; séparer visible, invocable et exécuté; conserver un état unknown quand la preuve manque.

**Vérification après correction :** Une observation sans provenance ne devient pas une capacité acquise; un résultat sur un dépôt ou une session ne vaut pas pour un autre.

**Portée de la validation du schéma**

Les comportements de F02–F05 découlent des règles JSON Schema; ce rapport ne les présente pas comme des sorties d’un validateur exécuté. La spécification autorise les propriétés supplémentaires en l’absence de restriction et n’impose pas une présence ou un minimum de contenu implicite. [Objets et propriétés supplémentaires](https://json-schema.org/understanding-json-schema/reference/object), [vocabulaire de validation 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation).

Le défaut de métadonnées F01 est corroboré par le format officiel : `name` et `description` dans le frontmatter, puis les instructions. [Construire des skills](https://learn.chatgpt.com/docs/build-skills), [erreurs de soumission des skills](https://developers.openai.com/plugins/deploy/submission-errors). Aucune installation native ni invocation des deux skills du dépôt n’a été tentée.

**Questions de conception et risques avant implémentation**

Ces points ne sont pas des vulnérabilités ou des erreurs runtime observées. Le dépôt annonce déjà comme futurs le moteur, le préflight, les hooks et les passerelles. Les scénarios ci-dessous servent à préciser leurs critères d’acceptation. Les priorités D ne sont pas additionnées au nombre de bugs.

**D01 — La priorité fixe ne démontre pas le coût minimal**

[skills/capability-router/SKILL.md:3–19](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L3-L19), [README.md:175–176](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L175-L176), [docs/TOKEN_ECONOMICS.md:10–17](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/TOKEN_ECONOMICS.md#L10-L17)

Le coût n’a ni unité, ni formule, ni poids relatif pour les quotas, le temps, les appels, les retries, CI, transfert et calcul local. La liste de préférence peut être une heuristique, mais ne suffit pas à prouver une minimisation. Réduire Work/Codex peut déplacer la dépense vers une API ou de la CI.

**Cas à traiter :** Scénario hypothétique : deux routes sont suffisantes, mais le transfert et les relances de la première dépassent le coût restant sur la surface courante. Aucun calcul ne permet de les départager.

**Décision proposée :** Définir le coût réellement optimisé et les contraintes de qualité/délai; traiter la préférence comme un départage après filtrage des capacités et estimation du coût marginal.

**Cas de vérification :** Comparer des routes suffisantes de coûts inversés et une estimation de coût inconnue.

**D02 — Le précontrôle doit vérifier une action et sa portée, pas seulement un nom d’outil**

[skills/capability-router/SKILL.md:20](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L20), [README.md:100](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L100), [docs/ROADMAP.md:9–10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md#L9-L10)

Le préflight est explicitement prévu pour une phase ultérieure. Il reste à distinguer outil visible, connexion authentifiée, action autorisée, action réellement réussie, fraîcheur et surface cible. Une preuve de lecture ne prouve pas l’écriture; un outil dans Work ne prouve pas sa présence dans Chat.

**Cas à traiter :** Lecture d’un dépôt réussie mais création de branche interdite; outil media visible mais Spark éteint; connexion valide dans la session courante mais absente chez le destinataire.

**Décision proposée :** Définir un manifeste par session, ressource et action, les états verified / unavailable / unknown et une stratégie de sondes sans effet de bord. Rafraîchir au transfert et après un échec.

**Cas de vérification :** Tests de lecture seule, permission partielle, expiration, machine hors ligne et absence de preuve côté destinataire.

**D03 — Le retour vers Chat doit dépendre de la tâche restante et du coût du transfert**

[skills/capability-router/SKILL.md:21](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L21), [docs/ROUTING_SPEC.md:24–25](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROUTING_SPEC.md#L24-L25), [README.md:141](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L141), [docs/HANDOFF_SPEC.md:18–22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L18-L22)

Le retour est formulé comme un réflexe. La règle générale de suffisance peut empêcher un mauvais retour, mais ni préflight explicite de destination, ni gain minimal, ni traitement d’une ré-escalade ne sont décrits.

**Cas à traiter :** L’implémentation est finie dans Codex; la revue restante nécessite un dépôt privé inaccessible depuis Chat. Un retour non conditionnel entraîne un blocage ou un aller-retour supplémentaire. C’est un scénario, pas une boucle mesurée.

**Décision proposée :** Réévaluer seulement le travail restant, vérifier les capacités de destination et ne transférer que si cela apporte un bénéfice. Conserver l’historique et une limite raisonnée aux bascules.

**Cas de vérification :** Destination incapable, tâche presque terminée, nouvelle erreur CI et absence de progrès après plusieurs transferts.

**D04 — Aucun résultat de routage bloqué n’est défini**

[SPEC.md:10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L10), [schemas/handoff.schema.json:5–8](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json#L5-L8), [skills/capability-router/SKILL.md:3–21](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L3-L21)

Toutes les sorties documentées désignent une route. Le résultat attendu quand aucune route n’est suffisante, autorisée ou démontrée n’est pas défini. Ce statut devrait appartenir à la décision de routage, sans nécessairement devenir une surface de handoff.

**Cas à traiter :** Aucun outil d’édition disponible et utilisateur interdisant Work, Codex et l’API : le routeur doit pouvoir expliquer son blocage sans inventer une capacité.

**Décision proposée :** Définir un statut blocked / needs-input avec cause, travail déjà accompli et plus petite information ou connexion nécessaire.

**Cas de vérification :** Aucune route disponible, routes disponibles mais interdites, coût inconnu sous plafond strict.

**D05 — Une recommandation de surface n’est pas un transfert confirmé**

[docs/HANDOFF_SPEC.md:3–22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L3-L22), [docs/MCP_PLAN.md:3–17](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/MCP_PLAN.md#L3-L17), [README.md:230–257](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L230-L257)

Le paquet indique recommended_surface; aucun protocole de remise, d’accusé de réception, de statut distant, de résultat ou d’annulation n’est défini. Le dépôt ne fournit aucun adaptateur lançant une surface. Il ne faut donc pas annoncer un transfert automatique effectif à partir de ce seul JSON.

**Cas à traiter :** Un handoff CODEX est produit, mais aucun destinataire ne le reçoit; ou submit_job répond de façon incertaine avant que l’orchestrateur ne sache si le travail a commencé.

**Décision proposée :** Distinguer recommandé, remis, accepté, en cours, terminé et échec. Définir un adaptateur par destination et une remise manuelle explicite lorsqu’aucun lancement automatique n’est disponible.

**Cas de vérification :** Destination indisponible, réponse perdue, reprise par un humain, annulation et résultat tardif.

**D06 — La reprise et les preuves doivent être rattachées à un état exact**

[docs/HANDOFF_SPEC.md:6–18](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L6-L18), [docs/HANDOFF_SPEC.md:22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md#L22), [README.md:251–255](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L251-L255), [SPEC.md:14–18](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L14-L18)

« Vérifier l’état courant » est demandé, mais aucune règle ne lie tâche, branche, commit, artefact, preuve de test et version de politique. Un repo et un nom de fichier ne suffisent pas à reconstruire l’état analysé. Ce problème subsiste même si les champs de F03 sont correctement typés.

**Cas à traiter :** Un résultat CI concerne le commit A, puis la branche avance à B avant réception; ou le skill chargé depuis main change entre deux exécutions de la même tâche.

**Décision proposée :** Référencer task/run/parent IDs, commit SHA, branche lorsque pertinente, preuves accessibles, politique/version de skill et état attendu. Prévoir le traitement d’un état devenu obsolète.

**Cas de vérification :** Branche avancée, résultat d’un autre commit, référence inaccessible et changement de politique entre deux runs.

**D07 — Les effets distants et la concurrence du scheduler restent à contractualiser**

[docs/ROADMAP.md:9–10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md#L9-L10), [README.md:292–313](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L292-L313), [docs/MCP_PLAN.md:5–13](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/MCP_PLAN.md#L5-L13), [docs/MCP_PLAN.md:21–22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/MCP_PLAN.md#L21-L22)

L’idempotence, les chevauchements, le checkpoint T-1, les retries et les limites d’autorisation entre surfaces ne sont pas définis. Les allowlists, secrets côté serveur, limites et journaux sont déjà prévus pour universal-api-mcp; il faut les transformer en critères applicables à chaque exécuteur. Aucun contournement de sécurité en fonctionnement n’a été démontré.

**Cas à traiter :** Une newsletter a été envoyée mais le checkpoint n’est pas enregistré; un retry peut renvoyer. Deux tâches quotidiennes se chevauchent. Une autorisation de revue ne doit pas devenir une autorisation de déploiement lors d’un handoff.

**Décision proposée :** Définir clés d’idempotence, limites de concurrence, ordre effet/checkpoint et reprise sur résultat incertain. Transmettre explicitement les contraintes utilisateur, permissions et plafonds; réévaluer l’autorisation au point d’effet.

**Cas de vérification :** Double livraison, échec après effet réussi, run tardif, chevauchement et tâche lecture seule reçue par une surface dotée de pouvoirs d’écriture.

**D08 — Les objectifs économiques ne disposent pas encore d’un protocole de mesure**

[SPEC.md:22–27](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L22-L27), [docs/TOKEN_ECONOMICS.md:3–17](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/TOKEN_ECONOMICS.md#L3-L17), [docs/ROADMAP.md:3–4](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md#L3-L4), [docs/ROADMAP.md:24–25](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md#L24-L25)

Les chiffres sont explicitement des hypothèses, ce qui est correct. Il manque toutefois l’unité d’usage, le périmètre du coût, la période de référence, la normalisation par charge et qualité, et le classement des tâches inachevées ou déplacées vers une API. La mesure est listée en fin de roadmap; la baseline réelle doit être prise avant les changements.

**Cas à traiter :** Un mois avec moitié moins de tâches affiche une baisse Work/Codex de 50% sans gain du routeur; une réduction de tâches terminées peut aussi faire baisser artificiellement la consommation.

**Décision proposée :** Mesurer une baseline dès le départ, comparer des tâches similaires réussies, publier coûts déplacés, délais et qualité, puis les gains de quota et de monnaie séparément.

**Cas de vérification :** Charge variable, tâches échouées, transfert de coûts CI/API, cache différent et changement de politique.

**Logiques à simplifier ou à rendre plus précises**

**Les pseudo-agents planifiés pour un besoin de vrais sous-agents.** Le tableau met des pseudo-agent schedulers en face de « True subagents », alors que la fixture exige trois agents synchrones et isolés. Séparer les travaux indépendants asynchrones du besoin de délégation synchrone; ne pas présenter l’un comme équivalent à l’autre. [docs/USE_CASES.md:23](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/USE_CASES.md#L23), [tests/routing_cases.md:12](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md#L12)

**La récurrence, la surface et le calcul local dans une seule liste.** Une tâche peut être déclenchée par le scheduler, orchestrée dans Chat et exécutée sur Spark via MCP. Décrire un plan composé avec déclencheur, orchestrateur, exécuteur et transport est plus précis que multiplier des surfaces mutuellement exclusives. [SPEC.md:10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md#L10), [skills/capability-router/SKILL.md:5–11](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L5-L11), [tests/routing_cases.md:10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md#L10)

**Le nombre de fichiers comme indicateur principal de difficulté.** Conserver 4/20/120 fichiers comme exemples. Une correction sur un fichier peut nécessiter une intégration lourde; 120 modifications mécaniques peuvent être simples. Décider surtout avec les outils requis, la boucle de validation, les dépendances et les limites de contexte. [docs/USE_CASES.md:9–10](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/USE_CASES.md#L9-L10), [tests/routing_cases.md:5–6](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md#L5-L6)

**Les cinq passerelles avant la preuve de valeur du routeur.** Prioriser un contrat de décision, un handoff valide, des fixtures contextualisées et un seul parcours mesuré. Reporter les passerelles spécialisées sans besoin démontré évite de transformer un outil d’économie en une grande plateforme d’orchestration. [docs/MCP_PLAN.md:3–22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/MCP_PLAN.md#L3-L22), [docs/ROADMAP.md:15–22](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md#L15-L22)

**Les règles dupliquées dans README, spécifications, skills et fixtures.** Définir une politique canonique versionnée et faire pointer les autres documents dessus. Le README dit au présent que le skill exécute cinq étapes, tandis qu’il annonce aussi un moteur futur; préciser ce qui existe comme instruction et ce qui reste à développer. [README.md:164–199](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md#L164-L199), [docs/ROUTING_SPEC.md:1–25](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROUTING_SPEC.md#L1-L25), [skills/capability-router/SKILL.md:1–21](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md#L1-L21)

**Relecture des dix fixtures existantes**

Il s’agit de conditions nécessaires et de décisions à formaliser, pas de résultats PASS/FAIL d’un moteur.

| Cas | Demande | Attente écrite dans le dépôt | Prérequis ou précision nécessaire |
|---|---|---|---|
| 1 | Papier arXiv + Loriq | CHAT | Recherche/lecture du papier et accès au dépôt vérifiés; volume compatible avec la session. |
| 2 | Créer une issue | CHAT | Action de création d’issue disponible, bonne portée de dépôt et autorisation utilisateur. |
| 3 | Quatre fichiers + PR + CI | CHAT | Écriture/branche/PR et récupération du résultat CI sur le bon commit disponibles. |
| 4 | 120 fichiers + tests locaux répétés | CODEX | Environnement et outils de test disponibles; la nécessité vient de la boucle de travail, pas seulement du nombre. |
| 5 | Veille quotidienne Spark | SCHEDULED_CHAT | Création de tâche, sources nécessaires et exécution future compatibles avec les outils autorisés. |
| 6 | ComfyUI sur Sparky | LOCAL_TOOL via media-mcp | Passerelle effectivement installée et machine disponible; séparer route et nom du transport. |
| 7 | Administration uniquement via UI | WORK | Navigateur adapté à la cible, accès authentifié et autorisation de l’action. |
| 8 | API privée horaire + delta | MCP + SCHEDULED_CHAT | Plan composite explicite, authentification, stockage du point T-1 et règles de reprise. |
| 9 | Revue Codex + notes de version | CHAT | Résultat et preuves accessibles dans Chat; transfert utile compte tenu du travail restant. |
| 10 | Trois agents synchrones et isolés | WORK/CODEX/SDK si nécessaire | Une route choisie avec preuve de véritable délégation synchrone; un scheduler de pseudo-agents ne suffit pas. |

**Contre-exemples et limites contrôlés**

| ID | Cas | Observation ou conclusion bornée | Preuve | Constat |
|---|---|---|---|---|
| C01 | Skill sans métadonnées | Échec de quick_validate sur les deux skills. | measured | F01 |
| C02 | Tous les champs demandés par le skill, sans version | Non conforme à required; sortie LLM non exécutée. | reasoned | F02 |
| C03 | repo=[], constraints=null, tests=42 | Aucune contrainte appliquée à ces champs inconnus du schéma. | reasoned | F03 |
| C04 | Objectif vide + critères vides | Compatible avec les seules contraintes actuelles. | reasoned | F04 |
| C05 | Objectif constitué d’espaces | Compatible avec type:string; pas de règle de contenu. | reasoned | F04 |
| C06 | Retour terminé avec remaining=[] | Cas légitime à conserver; pas un bug. | reasoned | F04 |
| C07 | Route sérialisée LOCAL/MCP | Hors enum; aucun appel réel d’un moteur ne l’a produite. | reasoned | F05 |
| C08 | Route HYBRID sans étapes | Enum satisfaite mais exécution sous-définie. | reasoned | F05 |
| C09 | Créer une issue sans outil d’écriture | L’oracle CHAT ne précise pas comment traiter ce contexte. | reasoned | F06 |
| C10 | Capacité historique dans une nouvelle session | Le PASS historique ne prouve pas la disponibilité courante. | reasoned | F07 |
| C11 | Deux routes suffisantes avec coûts inversés | Priorité heuristique sans arbitrage de coût défini. | reasoned | D01 |
| C12 | Outil visible mais permission lecture seule | Disponibilité apparente insuffisante pour conclure à l’écriture. | reasoned | D02 |
| C13 | Retour vers Chat sans accès au dépôt | Besoin de préflight de destination et de décision de rester. | reasoned | D03 |
| C14 | Toutes les routes indisponibles ou interdites | Résultat blocked à définir. | reasoned | D04 |
| C15 | Handoff recommandé mais jamais accepté | Ne peut pas être assimilé à un transfert accompli. | reasoned | D05 |
| C16 | Résultat CI de A, branche devenue B | Preuve à rattacher au SHA vérifié. | reasoned | D06 |
| C17 | Effet réussi puis checkpoint échoué | Politique anti-duplication et reprise à définir. | reasoned | D07 |
| C18 | Autorisation de revue reçue par un exécuteur de déploiement | Les capacités ne doivent pas étendre l’autorisation utilisateur. | reasoned | D07 |
| C19 | Baisse de charge indépendante du routeur | Une baisse de consommation brute ne prouve pas une économie du routage. | reasoned | D08 |

**Ce qu’il ne faut pas qualifier de bug**

- Le moteur, les hooks et les passerelles sont encore à développer : la roadmap le dit explicitement.
- Les économies de 50–80 % et le gain de contexte de 20–50 % sont déclarés comme des hypothèses; aucune économie réelle n’est démontrée, mais le dépôt ne les présente pas comme une garantie de facturation.
- Le dépôt explique correctement que faire appeler Codex/Claude par MCP ne rend pas leur usage gratuit.
- Un handoff de retour peut avoir `remaining=[]`. Le rejeter systématiquement casserait un cas utile.
- Le budget « typical handoff <5 KB » est un objectif statistique, pas une limite de validité universelle. Un hard cap nécessite une décision et une stratégie de références vers les détails.
- Les propriétés JSON supplémentaires peuvent servir à l’extensibilité. Le défaut actuel est surtout l’absence de déclaration des champs connus, pas l’absence universellement fautive de `additionalProperties:false`.
- Les phrases des fixtures ne sont pas la preuve qu’un moteur les sérialise telles quelles.
- Aucun code mort, SQL, autorisation contournée, retry effectivement dupliqué ou boucle infinie en fonctionnement ne peut être affirmé sans l’implémentation correspondante.

**Ordre de correction conseillé**

1. Corriger le format des deux skills et aligner le producteur de handoff sur un exemple et un schéma canoniques.
2. Déclarer les champs de handoff et les invariants minimaux; fixer les routes et le traitement de HYBRID.
3. Formaliser un résultat de décision avec capacités prouvées, restrictions, motif, état bloqué et plan de transfert.
4. Convertir les dix fixtures en cas contextualisés; ajouter les cas de refus, destination indisponible et preuve périmée.
5. Mesurer une baseline et implémenter un premier parcours complet, puis seulement les passerelles dont la valeur est établie.

**Couverture fichier par fichier**

| Fichier | Lignes logiques lues | Revue |
|---|---:|---|
| [README.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/README.md) | 396 | Lu intégralement; F07, D01, D02, D03, D05, D06, D07 |
| [SPEC.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/SPEC.md) | 27 | Lu intégralement; F04, F05, F06, D04, D06, D08 |
| [docs/ARCHITECTURE.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ARCHITECTURE.md) | 26 | Lu intégralement; F05, F07 |
| [docs/HANDOFF_SPEC.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/HANDOFF_SPEC.md) | 22 | Lu intégralement; F02, F03, D03, D05, D06 |
| [docs/MCP_PLAN.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/MCP_PLAN.md) | 22 | Lu intégralement; D05, D07 |
| [docs/ROADMAP.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROADMAP.md) | 25 | Lu intégralement; D02, D07, D08 |
| [docs/ROUTING_SPEC.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/ROUTING_SPEC.md) | 25 | Lu intégralement; D03 |
| [docs/TOKEN_ECONOMICS.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/TOKEN_ECONOMICS.md) | 17 | Lu intégralement; D01, D08 |
| [docs/USE_CASES.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/docs/USE_CASES.md) | 24 | Lu intégralement; pas de constat indépendant supplémentaire |
| [schemas/handoff.schema.json](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/schemas/handoff.schema.json) | 15 | Lu intégralement; F02, F03, F04, F05, F07, D04 |
| [skills/capability-router/SKILL.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/capability-router/SKILL.md) | 21 | Lu intégralement; F01, F04, F05, F06, D01, D02, D03, D04 |
| [skills/surface-handoff/SKILL.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/skills/surface-handoff/SKILL.md) | 6 | Lu intégralement; F01, F02, F03 |
| [tests/routing_cases.md](https://github.com/bacoco/chatgpt-cost-router/blob/ca763e51842cb1b53452fb41464232600572c6cd/tests/routing_cases.md) | 12 | Lu intégralement; F05, F06 |

**Traçabilité de l’audit**

Le dossier de preuves contient l’inventaire et les empreintes de chaque fichier, les recherches d’absence sur tout le périmètre, les résultats des deux validations, les contre-exemples, les données de revue et les fichiers ShipGuard. Le SHA de référence est `ca763e51842cb1b53452fb41464232600572c6cd`. Le comptage de 638 utilise les lignes logiques de `splitlines()`; `wc -l` compte 637 sauts de ligne car le README n’a pas de saut de ligne final.

Le rapport couvre intégralement les fichiers présents à ce commit, mais ne constitue ni une preuve formelle d’absence d’autres défauts, ni une vérification des capacités actuelles de toutes les surfaces ChatGPT. Les hypothèses d’environnement et les comportements futurs restent explicitement séparés des faits mesurés.
