# Project bootstrap protocol

This protocol is the canonical procedure used by the `project-workspace-bootstrap` skill.

## Input

```text
TARGET_REPO=<owner>/<repo>
```

Optional: project objective, cadence, constraints, existing Scheduled Task name.

## Source of truth

Resolve `bacoco/chatgpt-cost-router` `main` freshly and pin one SHA. At that SHA read:

- `skills/project-workspace-bootstrap/SKILL.md`
- `docs/REPO_SCHEDULER_WORKSPACE.md`
- `docs/CLOUD_EXECUTION_LANE.md`
- `docs/CHATGPT_TO_CODEX_HANDOFF.md`
- `docs/VALIDATION_STATUS_2026-09-10.md`

Do not use a remembered copy.

## Procedure

1. Verify target GitHub identity/access and exact default-branch SHA.
2. Inspect target repo instructions, open work, and existing `.chatgpt/` structure.
3. Install/reconcile `.chatgpt/PROJECT.md`, `CURRENT.md`, `SCHEDULER.md`, `HANDOFF_POLICY.md`, and `handoffs/README.md`.
4. Copy the exact pinned source versions of `skills/cloud-to-codex-handoff/SKILL.md` and `skills/codex-to-cloud-return/SKILL.md` into the target repository under `.agents/skills/<skill-name>/SKILL.md`. Preserve any unrelated existing target skills.
5. Persist the source-kit SHA inside `PROJECT.md` so future refreshes are reproducible and the copied skills can be traced back to their source.
6. Create/reuse a project Scheduled Task only if useful. Its prompt must read target repo state and `.chatgpt/` files freshly on every invocation.
7. If the user supplied concrete work, begin with ChatGPT + Developer MCPs and persist checkpoints after meaningful progress.
8. When a real capability boundary is reached, use `cloud-to-codex-handoff`; do not paste the whole conversation into Codex.
9. On return from Codex, use `codex-to-cloud-return` evidence and verify actual GitHub state before continuing.
10. Never silently use paid API capacity. GitHub Actions runner capacity is a separate cost/capability gate.

## Installation safety

For an existing repo, prefer a bootstrap branch/PR. Do not overwrite pre-existing project-control files blindly. Never delete unrelated files.

## Scheduler template

Store the adapted form in `.chatgpt/SCHEDULER.md` and use it for the Scheduled Task:

```text
This is the ChatGPT project workspace for repository `<owner>/<repo>`.

Resolve the repository default branch freshly. Read `.chatgpt/PROJECT.md`,
`.chatgpt/CURRENT.md`, and `.chatgpt/SCHEDULER.md`. Verify all referenced SHAs,
branches, PRs and issues against current GitHub state.

If scheduled work is actually due, execute only the authorized bounded work and
persist a fresh checkpoint. Otherwise do not invent work; return the concise current
state and exact next safe action.

Use ChatGPT + authorized Developer MCPs first. Do not rely on chat-local filesystem
persistence. Do not repeat verified external effects. If Codex becomes materially
useful, persist a cloud-to-Codex handoff in GitHub and stop at the handoff boundary.
Never silently use a paid API.
```

## Completion receipt

Return source-kit SHA, target base SHA, installed files, commit/PR, scheduler state, current checkpoint, and pending validation tests.
