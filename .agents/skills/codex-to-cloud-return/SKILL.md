---
name: codex-to-cloud-return
description: Return completed or blocked Codex repository work to ChatGPT Cloud through a verifiable GitHub artifact tied to the exact resulting commit, preserving tests, evidence, remaining work, and original scope.
---

# Codex to Cloud Return

Use this skill in Codex after work was accepted from a `cloud-to-codex-handoff`.

Read the original `TO_CODEX.md`, `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, and any `handoff.json` before acting. If available, read the canonical `surface-handoff` skill and contracts from the pinned `bacoco/chatgpt-cost-router` revision referenced by the project.

## Preflight

1. Fetch/reconcile the checkout.
2. Verify the original handoff commit and working branch.
3. Verify that current repository state has not invalidated the task.
4. Preserve original scope, constraints, required tests, and authorization.
5. If the branch moved unexpectedly or an external effect is ambiguous, reconcile before continuing.

## Execute only remaining work

Do not redo completed ChatGPT work unless evidence is stale or a required test proves it invalid.

Use the local Codex environment only for work that remains in scope. Never infer deploy, merge, release, secret access, or paid API authorization from the fact that Codex has those capabilities.

## Required return artifact

Write:

```text
.chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md
```

Include task ID; status (`completed`, `blocked`, or `failed`); source handoff and handoff commit; resulting branch and exact commit SHA; files changed; tests actually run and exact results; evidence/outputs; external effects actually performed; remaining work; blockers/uncertainties; and confirmation that scope/authorization were preserved.

When a formal `handoff.json` exists, produce a matching return envelope when practical and validate it before claiming completion.

Commit the return artifact with the resulting code changes so the artifact and code refer to one verifiable repository state.

## Return prompt for ChatGPT

Provide:

```text
Resume task <task-id> in ChatGPT Cloud.

Repository: <owner/repo>
Return artifact: .chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md
Expected resulting commit: <40-character SHA>

Re-read the actual GitHub branch, commit, diff and test evidence. Treat the return
artifact as a claim to verify, not proof by itself. Continue only the remaining work.
```

## Completion rule

Do not say the task is completed unless all required tests and success criteria assigned to Codex actually passed and are tied to the resulting commit.

Do not merge unless explicitly authorized.
