---
name: surface-handoff
description: Prepare or validate a compact, versioned task handoff between execution contexts, preserving scope, evidence and completion criteria. Use for delegation or return of specialist results.
---

# Surface Handoff

Read the [v2 handoff contract](../../docs/HANDOFF_SPEC.md) and use
[handoff.schema.json](../../schemas/handoff.schema.json) as the structural contract.
The [delegation example](../../examples/handoff.json) and
[completed return](../../examples/completed-return.json) contain synthetic data;
replace it with actual task state, never treat it as capability evidence.

- Emit `version: 2` and all declared fields. Preserve task/operation identity,
  source and destination sessions, policy version/hash, user constraints and
  authorization. State why a transfer is useful and what remains.
- Record the exact repository, branch and commit where applicable. Link accessible
  artifacts and test evidence rather than copying the entire conversation.
- Require a nonblank objective and meaningful success criteria. Delegation has
  remaining work; a completed return has `remaining: []`, verified criteria and
  passing required tests tied to the resulting commit.
- Preserve required tests and scope on return. Never turn a review authorization into
  permission to edit, deploy or send. A completed return contains no new actions.
- Run `python -m cost_router validate handoff handoff.json` from the checkout when
  available. Without that runtime, report structural review as reasoned; do not claim
  machine validation. Destination preflight is a separate required execution check.
- A packet does not launch another surface. Follow the
  [acceptance and recovery protocol](../../docs/EXECUTION_PROTOCOL.md); distinguish
  recommended, accepted, running, uncertain and completed. Reconcile an uncertain
  external effect before considering any retry.
- Return to the originating context only when its current capabilities and the
  remaining task justify it. Otherwise explain the blocked transfer or propose a
  newly evaluated destination without silently changing the original authorization.

Version 1 packets require explicit reconstruction under v2; do not invent missing
permissions, evidence or identities. Unknown extension metadata belongs in
`extensions`. Native installation must preserve the full checkout references;
GitHub-only reads must pin the same revision for this skill and its contracts.
