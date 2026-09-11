# Architecture — distinguish published source from prepared continuation

Read [delivery status](AB_DELIVERY_STATUS_2026-09-11.md) first. Publication of the
full B continuation was blocked; this branch is not the complete prepared tree.

## Published A and shared contracts

`chat_ops` owns the action catalog, session-scoped observations, workflow engine,
exact approvals, native single-instruction driver, optional multi-account direct
MCP adapter and CLI/MCP interfaces. Per-run locks serialize decisions. Pending
instructions are not replayed. Preflight, mutation and read-back are separate phases;
cancellation/deadlines stop new effects but permit required read-back recovery.
The concurrent session/output-recovery fix at `cd897ddf...` is preserved.

`operation_contracts` owns operator-controlled project/resource grants, private
journals, account reservations, locks, bounded subprocess capture and owned child
identity helpers. Exact resource matching distinguishes booleans/numbers and absent/
null. Account budgets are operator observations within one authoritative journal,
not automatic provider quota ingestion. Session IDs are not authentication tokens.

Native A returns instructions for the actual Chat client's tools, then accepts
caller-observed results. A Python process does not inherit a Chat subscription or
connector credentials. The direct adapter requires explicit endpoint/account/tool
bindings and validates current schemas offline. Neither lane invokes another model.

## Retained B implementation

`fleet_operator/jobs` retains the earlier node profile/lifecycle implementation.
`fleet_operator` retains gateway/MCP/relay foundations. The new metrics helper is
present but not wired into the restored node runtime. Optional worker/mesh code
still resides in `cost_router` on this branch; the physical migration is only in
the prepared artifact. Its worker/prompt protocol is not a generic project-job API.

The blocked continuation includes stronger owned supervision, immutable artifact
snapshots, typed gateway wiring, no-replay outbox recovery, enrollment/template
rendering, release activation/rollback and packaging. Do not describe those prepared
files as deployed or all published. Dependent source changes were restored after
the block to prevent missing imports, without touching installed services.

## Verification and trust boundaries

Published source: 134 local regression tests passed. Full prepared artifact: 176
passed plus one skipped official-SDK smoke. No live external app mutation, current
Chat custom-app attachment, real SSH fleet lifecycle or container-engine enforcement
was established. Trusted-local profiles are not an OS sandbox. Private HTTP needs
separate authenticated exposure and configured identity. T38/deployments remain paused.
