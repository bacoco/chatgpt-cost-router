---
name: project-workspace-bootstrap
description: Bootstrap or refresh a GitHub repository as a ChatGPT cloud project workspace, install durable .chatgpt project state, and create or reuse a repo-specific Scheduled Task launcher without treating chat state as persistence.
---

# Project Workspace Bootstrap

Use this skill when the user gives a GitHub repository and wants ChatGPT to prepare it for the cloud-first workflow defined by `bacoco/chatgpt-cost-router`.

The user's explicit request to bootstrap a target repository authorizes only the bounded bootstrap actions described here. It does not authorize unrelated refactors, releases, deployments, destructive changes, or paid API use.

## Required input

- `TARGET_REPO` as `owner/repo`.
- Optional project objective, constraints, cadence, and existing Scheduled Task name.

If no cadence is supplied, do not invent frequent recurring work. Prefer a one-shot initialization or a light workspace launcher only when that serves a real purpose.

## Canonical source

Resolve `bacoco/chatgpt-cost-router` `main` freshly and pin one exact source SHA. Read at that same SHA:

- `docs/PROJECT_BOOTSTRAP_PROTOCOL.md`
- `docs/REPO_SCHEDULER_WORKSPACE.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/AB_VALIDATION.md`
- `docs/CHATGPT_TO_CODEX_HANDOFF.md`

Do not use a remembered copy.

## Secours MCP embarqué

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

## Preflight

1. Verify authenticated GitHub identity and read access to `TARGET_REPO`.
2. Resolve the target default branch and exact HEAD SHA.
3. Inspect existing `.chatgpt/`, `AGENTS.md`, `.agents/skills/`, project docs, open PRs/issues, and any Scheduled Task already relevant to this repo.
4. Never overwrite an existing project-control file blindly. Reconcile compatible content and preserve project-specific instructions.
5. Record unavailable capabilities as unavailable rather than silently substituting Codex, Work or a paid API. GitHub Actions is forbidden, not a fallback.

## Target repository structure

Install or reconcile:

```text
.chatgpt/
  PROJECT.md
  CURRENT.md
  SCHEDULER.md
  HANDOFF_POLICY.md
  handoffs/
    README.md

.agents/skills/
  cloud-to-codex-handoff/
    SKILL.md
  codex-to-cloud-return/
    SKILL.md
```

`PROJECT.md` contains stable project purpose, key paths, constraints, source-of-truth rules, source-kit SHA, and relevant authorized connectors/apps.

`CURRENT.md` is the compact recoverable checkpoint: current task, default/working branch, exact SHAs, issues/PRs, completed work, tests/evidence, blockers, next safe action, and whether Codex/API/Actions were used.

`SCHEDULER.md` contains the canonical repo-specific scheduler prompt, its cadence or one-shot behavior, idempotency rules, and allowed mutations.

Copy the complete `[MCP-CONVERSATION-RECOVERY-v1]` block above verbatim into
`PROJECT.md`, `SCHEDULER.md` and every launcher prompt installed or updated by this
bootstrap. Preserve project permissions and scheduler cadence. Never replace this
small embedded exception with a link requiring GitHub to work. Inspect the final
prompt and verify the literal block before declaring the launcher configured.
Existing live tasks are changed only when the user's request authorizes that change;
a repository update alone does not change native task or installed app settings.

`HANDOFF_POLICY.md` points to the cloud-to-Codex and Codex-to-cloud conventions and forbids scope expansion.

Copy the two handoff skills from the exact pinned source-kit SHA into `.agents/skills/` so a Codex checkout of the target repo has the workflow locally. Record the source-kit SHA in `PROJECT.md`; refresh these copies only through a later controlled bootstrap/update, never from memory.

## Safe installation

Prefer a dedicated bootstrap branch and PR for an existing repository. For a new/empty repository, direct initialization is acceptable only when clearly authorized.

Before merge, verify the diff is limited to the intended bootstrap files unless the user explicitly requested more. Do not change application code merely to install the workspace.

## Scheduler workspace

Create or reuse one primary project Scheduled Task only when useful.

The scheduler must:

- name the exact target repo;
- resolve current repo state freshly;
- read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, and `.chatgpt/SCHEDULER.md`;
- verify referenced branch/SHA/PR/issue state before acting;
- perform only due and authorized work;
- update `.chatgpt/CURRENT.md` after meaningful work;
- avoid duplicate external effects;
- make native Chat + authorized connectors/apps the default route;
- use current Chat/local verification when sufficient or an enrolled Fleet profile when machine execution is required;
- never create, restore or use GitHub Actions;
- hand off to Codex only through a persisted GitHub handoff;
- never silently use a paid API.

If the repo already has a meaningful Scheduled Task, prefer reusing it as the project entry point rather than creating a duplicate scheduler.

## Initial project work

After bootstrap, do not manufacture work. If the user supplied a concrete project objective, continue it using the cheapest sufficient route. Otherwise return the initialized state and exact next action.

## Output

Report source bootstrap SHA, target repo/base SHA, files created or updated, bootstrap branch/commit/PR or direct commit, scheduler created/reused, current checkpoint path, Codex/API usage, blockers, and next safe action.

Never claim the scheduler chat is a persistent VM. GitHub is durable state.
