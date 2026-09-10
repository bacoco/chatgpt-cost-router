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
- `docs/CLOUD_EXECUTION_LANE.md`
- `docs/CHATGPT_TO_CODEX_HANDOFF.md`
- `docs/VALIDATION_STATUS_2026-09-10.md`

Do not use a remembered copy.

## Preflight

1. Verify authenticated GitHub identity and read access to `TARGET_REPO`.
2. Resolve the target default branch and exact HEAD SHA.
3. Inspect existing `.chatgpt/`, `AGENTS.md`, `.agents/skills/`, project docs, open PRs/issues, and any Scheduled Task already relevant to this repo.
4. Never overwrite an existing project-control file blindly. Reconcile compatible content and preserve project-specific instructions.
5. Record unavailable capabilities as unavailable rather than silently substituting Codex, Work, GitHub Actions, or a paid API.

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
```

`PROJECT.md` contains stable project purpose, key paths, constraints, source-of-truth rules, source-kit SHA, and relevant Developer MCPs.

`CURRENT.md` is the compact recoverable checkpoint: current task, default/working branch, exact SHAs, issues/PRs, completed work, tests/evidence, blockers, next safe action, and whether Codex/API/Actions were used.

`SCHEDULER.md` contains the canonical repo-specific scheduler prompt, its cadence or one-shot behavior, idempotency rules, and allowed mutations.

`HANDOFF_POLICY.md` points to the cloud-to-Codex and Codex-to-cloud conventions and forbids scope expansion.

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
- make ChatGPT + Developer MCPs the default route;
- hand off to Codex only through a persisted GitHub handoff;
- never silently use a paid API.

If the repo already has a meaningful Scheduled Task, prefer reusing it as the project entry point rather than creating a duplicate scheduler.

## Initial project work

After bootstrap, do not manufacture work. If the user supplied a concrete project objective, continue it using the cheapest sufficient route. Otherwise return the initialized state and exact next action.

## Output

Report source bootstrap SHA, target repo/base SHA, files created or updated, bootstrap branch/commit/PR or direct commit, scheduler created/reused, current checkpoint path, Codex/API usage, blockers, and next safe action.

Never claim the scheduler chat is a persistent VM. GitHub is durable state.
