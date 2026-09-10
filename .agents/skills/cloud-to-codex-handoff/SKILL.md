---
name: cloud-to-codex-handoff
description: Hand remaining repository work from ChatGPT Cloud to Codex through a compact, verifiable GitHub handoff while preserving scope, exact commit state, tests, evidence, and user authorization.
---

# Cloud to Codex Handoff

Use this skill only when a concrete remaining requirement is better served by Codex than by the current ChatGPT + Developer MCP route.

This skill specializes the repository's `surface-handoff` contract. Read `skills/surface-handoff/SKILL.md`, `docs/HANDOFF_SPEC.md`, and `docs/EXECUTION_PROTOCOL.md` at the same pinned `bacoco/chatgpt-cost-router` revision.

## Principle

Route the remaining work, not the whole project. A code task does not itself require Codex.

## Before handoff

1. Re-read the target repository and exact working branch HEAD.
2. Reconcile existing issues, PRs, tests, and external effects.
3. Update `.chatgpt/CURRENT.md`.
4. Preserve the user's original constraints and authorized actions.
5. State the concrete capability boundary that justifies Codex.
6. Do not copy the full chat transcript.

## Write the handoff

Create or update:

```text
.chatgpt/handoffs/<task-id>/TO_CODEX.md
```

It must include task ID and definition of done; target repo; base branch and exact SHA; working branch and exact SHA; issue/PR IDs; completed work; files inspected/changed; tests and results; environment limitations; completed external effects; remaining work only; required tests; constraints/forbidden actions; authorized scope; and expected return artifact.

When practical, also write `handoff.json` conforming to Surface Handoff v2. Do not fabricate fields merely to satisfy the schema.

Commit the handoff to GitHub and obtain the exact handoff commit SHA before producing the takeover prompt.

## Codex takeover prompt

Return a short prompt in this shape:

```text
Take over task <task-id> from ChatGPT Cloud.

Repository: <owner/repo>
Handoff: .chatgpt/handoffs/<task-id>/TO_CODEX.md
Expected handoff commit: <40-character SHA>

Fetch/reconcile the repository first. Verify the handoff, working branch and exact
commit against GitHub. Read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, the handoff,
and only the project files needed for the remaining work.

Do not redo verified completed work unless its evidence is stale. Do not broaden scope
or permissions. Complete only the remaining work and run the required tests.

When finished, apply the `codex-to-cloud-return` skill and commit
`.chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md` with the resulting code changes.
Do not merge unless explicitly authorized.
```

## Completion

This skill is complete only when the handoff exists in GitHub at the reported commit and the takeover prompt points to that exact state.

Do not claim that Codex has started merely because the prompt was generated.