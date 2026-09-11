# Roadmap — independent A and B products

Status: strategic pause; documentation alignment only.
Scope: [A/B decision](TWO_PROJECTS_AND_PAIR_2026-09-11.md).
Source-level mapping: [ARCHITECTURE](ARCHITECTURE.md).
Historical proofs: [VALIDATION_STATUS_2026-09-11](VALIDATION_STATUS_2026-09-11.md).
This roadmap does not authorize deployments, app mutations, fleet jobs or T38 work.

## A — Chat-first Operations

**Goal:** complete authorized work from normal Chat through the full plugin/connector
toolbox. Gmail, GitHub, WordPress/Cowboy, documents and other apps are first-class.
Issues, specifications and code handoffs are examples, not the product's limits.

Existing building blocks include repository workflows/skills, scoped capability
evidence, checkpoints, deterministic route validation and historical connector tests.
These do not amount to a newly packaged implementation of every external app.

Next design work:
1. Consolidate an action-level matrix across ChatGPT.com Chat, Codex Mac Chat, Work,
   CLI and Scheduled Tasks, reusing existing evidence rather than repeating it.
2. Bind project/task context and authenticated resources explicitly in multi-app
   workflows; preserve user scope and required confirmations for external effects.
3. Define completion and reconciliation for mail, repository operations, publication
   and other apps, including cross-app workflows with partial failures.
4. Keep normal Chat/direct tools as the preferred lane; make machine execution and
   additional model delegation explicit rather than implicit product dependencies.
5. Evaluate Serena only where targeted code context/editing adds useful capability.

Acceptance categories, to exercise only when authorized: completed and verified mail
operations; exact GitHub changes; authorized publication/other-app operations; and
a cross-app/multiproject task without mixed accounts, recipients or permissions.
An issue alone does not validate A. Do not restart the stopped quota-burn experiment.

## B — Fleet Operator

**Goal:** reliable access to machines, process lifecycle management, monitoring and
results, usable with or without Chat. Placement/load distribution is secondary.

Existing building blocks include local/SSH execution, MCP/relay interfaces, macOS
supervision, Codex broker, heartbeat discovery, budget observations and quarantine.
Historical T35B-T37 proofs do not certify full lifecycle or multi-tenant readiness.

Next design work:
1. Close the broad-write/path-isolation risks; agree actual execution containment
   before resuming T38. A risk acknowledgement is not an OS sandbox.
2. Harden relay recovery so publication failure or interruption cannot silently
   repeat an already-executed operation. Preserve uncertain outcomes for reconciliation.
3. Define a stable submit/status/progress/logs/cancel/result contract for ordinary
   processes as well as optional agent tasks. Distinguish reachability from progress.
4. Specify repeatable enrollment, pinned runtime versions, capability checks,
   project assignments, resource limits and rollback; preserve unrelated services.
5. Keep model workers optional. Design provider/account-scoped budgets and auth
   lifecycle; unknown quota is not available quota.
6. Qualify the direct MCP client attachment separately from the already-recorded
   relay path. Evaluate PAIR for local inference only, not generic job management.

Acceptance categories, to exercise only when authorized: a bounded non-LLM task
through its lifecycle on an enrolled machine; safe cancellation/failure recovery;
another client using B without Chat; and multiproject isolation. Reuse the existing
multinode and restart receipts. No new model smoke is required by this roadmap.

## Shared contract and code organization

Requester, task/project, GitHub identity, OS identity, machine and provider account
must remain separate concepts. Bind exact repository/SHA when applicable, operation
scope, allowed resources, optional model budget, run/idempotency identity and evidence.
Project content may restrict a request; it cannot increase service permissions.

Keep the existing repository for now. Map A, B and shared ownership before moving
modules. The deterministic engine/SQLite ledger and the Fleet runtime currently
coexist; the relay is not automatically covered by every shared-ledger invariant.

After approval, migrate behind compatible imports/CLIs and verify both connector-only
A and Chat-independent B behavior. Do not split repositories, install Serena/PAIR,
change services, create test messages/posts/issues or enqueue jobs during this pause.

## Economics and deferred work

Prefer capability already included in Chat; do not hide extra inference/API spend
inside a plugin. Track known/unknown monetary spend, model usage and compute costs
separately when ordinary task telemetry makes them observable.
Older savings percentages remain hypotheses, not rollout gates or instructions to
resume artificial token-burning tests. Concurrency, additional providers and GPU
routing follow demonstrated workload needs, not the desire to add another numbered test.
