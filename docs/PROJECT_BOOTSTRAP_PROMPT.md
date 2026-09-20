# One-prompt project bootstrap

Replace only `TARGET_REPO` for the simplest use.

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

TARGET_REPO=<owner>/<repo>

Bootstrap this GitHub repository for the ChatGPT cloud-first project workflow using
the current `main` of `bacoco/chatgpt-cost-router` as the installation source.

Resolve and pin the source repo SHA first. Read and apply
`skills/project-workspace-bootstrap/SKILL.md` and
`docs/PROJECT_BOOTSTRAP_PROTOCOL.md` from that exact SHA.

In TARGET_REPO, inspect existing instructions/state before writing. Install or
reconcile the canonical `.chatgpt/` workspace without deleting or blindly
overwriting project-specific information. Also copy the exact pinned
`cloud-to-codex-handoff` and `codex-to-cloud-return` skills into
`.agents/skills/` in TARGET_REPO, preserving unrelated existing skills. Use a
bootstrap branch/PR for an existing repo unless direct initialization is clearly
safer and authorized.

Create or reuse one primary repo-specific ChatGPT Scheduled Task/workspace launcher
when useful. Its prompt must re-read the target repo and `.chatgpt/` checkpoint
freshly on every run. Do not create a pointless frequent schedule only to keep a chat
alive.

After bootstrap, if there is already active project work, start with native ChatGPT +
the authorized connectors/apps and persist progress in `.chatgpt/CURRENT.md`.

If a real capability boundary is reached, use the source repo's
`cloud-to-codex-handoff` skill to write a GitHub handoff and give me the short prompt
for Codex. When Codex returns, use `codex-to-cloud-return` evidence and verify the
actual branch/SHA/diff/tests before continuing.

Do not use Codex merely because code is involved. Do not silently use paid APIs.
GitHub Actions is forbidden: do not create workflows, dispatch/rerun hosted jobs or
use an Actions control connector. Prefer current Chat/local verification or an enrolled
Fleet profile when execution is required.

At the end, report exactly what was installed, the source and target SHAs,
branch/commit/PR, scheduler created or reused, current checkpoint, tests actually
performed, and remaining validation gaps.
```

Optional inputs may be added below `TARGET_REPO`:

```text
PROJECT_GOAL=<optional goal>
SCHEDULER_CADENCE=<optional real cadence>
CONSTRAINTS=<optional constraints>
```

If cadence is omitted, the bootstrap must not invent expensive recurring work.
