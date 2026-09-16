# Test planifié complet — GitHub standard uniquement

16 septembre 2026. Heures locales : Paris.

**Résultat : réussi.** Le connecteur standard a enchaîné la lecture du README, deux recherches, la création de l’issue, sa relecture, sa fermeture puis sa relecture. Aucun outil du MCP personnel n’a été utilisé pour ce test ou sa vérification.

- Tâche ponctuelle : `6aaa4bcaf36c81918bdda0a38f80ef2b`, « TEST standard complet — 20260916-1003 ».
- Échéance : **10:03**, soit `2026-09-16T08:03:00Z`.
- Création relue comme activée, `last_run_time: null`, sans récurrence. Interface Planification observée avant échéance. Aucune réactivation ni aucun lancement manuel effectué.
- Recherche indépendante avant échéance : aucune issue trouvée pour `standard-full-20260916-1003`.
- Issue : [#36](https://github.com/bacoco/loriq-watch-scheduler/issues/36), `[TEST-SCHEDULER-STANDARD-FULL] 20260916-1003`.
- Création : **10:05:18**, fermeture : **10:05:27**. Ces deux heures ont été vérifiées dans les éléments de date de la page GitHub, et concordent avec le compte rendu de l’exécution.
- État final directement observé sur GitHub : **Closed / completed**, titre et marqueur conformes.
- Relecture finale de la tâche via `automations.list` : `last_run_time: 2026-09-16T08:05:47.307422Z`, `is_enabled: false`, sans récurrence. La dernière exécution enregistrée est bien postérieure à l’échéance.

Le résultat associé à la tâche dans ChatGPT rapporte, dans l’ordre : `GitHub.fetch`, `GitHub.search_issues` deux fois, `GitHub.create_issue`, `GitHub.fetch_issue`, `GitHub.update_issue`, `GitHub.fetch_issue`. Cela représente sept appels GitHub, en plus de la découverte des outils standard. Les noms et l’ordre proviennent du compte rendu de la tâche ; les journaux HTTP internes ne sont pas disponibles. L’issue et ses horaires ont été vérifiés indépendamment dans le navigateur, utilisé seulement pour piloter l’interface ChatGPT et constater le résultat GitHub, pas pour écrire l’issue.

**Conclusion : plusieurs appels GitHub successifs, avec lecture du README avant création puis fermeture, fonctionnent dans ce test planifié standard. L’hypothèse d’une interdiction générale du multi-appel est contredite par ce résultat.**

Ce succès ne révèle pas la cause du premier refus. Le présent prompt reformule explicitement le périmètre, traite le README comme données et utilise un nouveau marqueur ; ce n’est pas une reproduction mot pour mot de l’ancien prompt. Il ne démontre ni une réparation causée par l’installation du MCP, ni une absence de blocages intermittents.

Preuves : `preuves-standard-complet-20260916-1003.json` (création et recherche initiale), `resultat-standard-complet-20260916-1003.json` (compte rendu et observation indépendante GitHub).
