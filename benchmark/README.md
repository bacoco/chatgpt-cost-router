# Fidélité au but : banc d’essai préparé, comparaison non exécutée

## Résultat réel au 10 septembre 2026

**Aucun résultat A/B sur un LLM n’a été obtenu.** Le lancement GitHub Actions 34466688329 s’est terminé en échec avant l’attribution d’un runner (runner_id=0, steps=[]). Les journaux du job 102836807816 sont indisponibles ; la cause précise n’est pas établie. Aucun gain, taux de réussite ou recul des hallucinations ne peut être calculé.

Le correcteur a été exécuté dans le conteneur de cette conversation : 41 contrôles passent. Ce sont des tests du banc d’essai, PAS 41 réponses de LLM. Les fichiers Python passent aussi la compilation syntaxique.

## Protocole figé avant tout résultat

12 cas synthétiques, six familles, trois conditions (sans ajout, idée courte, prompt intégral), deux graines (11 et 29) : 72 réponses prévues. Modèle prévu, non exécuté : Qwen3-1.7B Q8_0, mode non-thinking. Les réponses attendues ne sont jamais envoyées au modèle. Même format JSON et plafond de 256 tokens de sortie dans chaque condition. Ordre aléatoire fixé à 20260910.

Familles : documents incomplets, calcul avec suggestion trompeuse, correction de code, révision après contre-preuve, preuves d’exécution, résistance à une fausse correction. Les cas de code sont corrigés par des tests fonctionnels et les autres par un résultat attendu explicite.

L’injection est réalisée en lisant les fichiers .md et en ajoutant leur texte à l’instruction système. Le pilote ne compare PAS la découverte automatique d’un fichier par un agent à une instruction directe.

## Limites même en cas d’exécution future

Un petit modèle quantifié et 12 exemples choisis ne permettent pas de généraliser aux modèles de pointe. Deux graines ne constituent pas deux tâches indépendantes. Les dialogues antérieurs sont des stimuli synthétiques, pas des trajectoires autonomes. Le score principal porte sur answer et ne détecte pas tous les détails inventés dans reason. La comparaison à budget de sortie identique laisse une différence de tokens d’entrée : mesurer le surcoût fait partie du protocole. La version longue combine plusieurs mécanismes ; elle ne permet pas d’attribuer un éventuel effet à une seule phrase.

## Exécution locale

Python 3.11+, accès au téléchargement Hugging Face, mémoire et ressources CPU suffisantes :

```bash
python -m pip install llama-cpp-python==0.3.16
python benchmark/grader.py
python benchmark/runner.py
```

L’installation du moteur et la génération de bout en bout ne sont PAS validées dans ce pilote bloqué. Les observations effectivement générées seront écrites dans benchmark/results/ ; ne pas confondre STATUS.json avec ces résultats futurs.

## Sécurité de la branche

main n’a pas été modifié. Après l’échec, tous les fichiers applicatifs du main de départ ont été rétablis dans la branche expérimentale : son état final ne contient que des ajouts sous benchmark/. Le workflow d’essai a été retiré de .github/workflows/ et conservé uniquement comme exemple inactif sous benchmark/workflow-example.yml. Il n’y a aucune exécution récurrente ni tâche laissée en cours. Ne pas fusionner ou activer ce pilote sans revue.

Preuve du lancement : https://github.com/bacoco/chatgpt-cost-router/actions/runs/34466688329
Protocole initial : 64497869619a0d2d057493447eb1bfbaf413275c
Base main : a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736
