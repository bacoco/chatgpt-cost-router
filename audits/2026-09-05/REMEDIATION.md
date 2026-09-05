# Resolution of the 2026-09-05 audit

Base: `ca763e51842cb1b53452fb41464232600572c6cd`.

The seven original findings are addressed. The eight design obligations now have
explicit contracts; the local recommendation, validation and operation-state
parts are implemented and tested. External adapters, live capability acquisition,
distributed scheduling and economic field measurements remain integration work.
No existing remote runtime was present in the audited repository.

Independent review of the new runtime found and verified one additional lifecycle
defect: a policy update could strand an in-flight operation. Completion now checks
the policy identity already accepted for that operation; new execution claims still
require the current policy. A regression exercises both outcomes.

## Findings

| ID | Resolution | Evidence |
|---|---|---|
| F01 | Both skills now have valid YAML `name` and `description`; native discovery links and complete-checkout installation instructions were added. | `tests/test_audit_regressions.py`; official skill metadata validator; `docs/INSTALLATION.md` |
| F02 | The handoff skill explicitly requires v2, links its canonical schema, and supplies full delegation and completed-return examples. | `schemas/handoff.schema.json`; `examples/handoff.json`; `examples/completed-return.json` |
| F03 | All context/control fields are typed and required. Unknown fields are rejected; optional future metadata belongs in `extensions`. Repository work requires branch and commit identity. | Wrong-type and typo regressions; `cost_router/handoff.py` |
| F04 | Goals, IDs and criteria require nonblank text; success criteria cannot be empty. Delegations require remaining actions; completed returns allow empty remaining work and require verified success. | Blank-content regressions and completion-negative tests |
| F05 | Six atomic surface names are canonical. `HYBRID` is a composed decision with explicit ordered steps; a handoff targets one surface/session. Scheduler and executor roles are separate. | `policy/routing.json`; shared schemas; `tests/routing_cases.json` |
| F06 | The original ten prose cases were replaced by ten explicit contextual scenarios plus ten negative cases, with independent expected decisions and a deterministic evaluator. | 20 JSON fixtures exercised by `tests/test_router.py`; these measure evaluator agreement, not model accuracy |
| F07 | Unsourced capability PASS/FAIL statements were removed from current documentation. Observations require action, resource, surface, session, time, expiry and evidence. Historical claims remain only in the original audit archive. | `docs/CAPABILITIES.md`; stale/expired/conflicting/session-scope tests; empty unverified manifest example |

## Design obligations

| ID | Resolution and implemented boundary | Verification |
|---|---|---|
| D01 | Feasible plans compete on comparable execution + transfer + retry + CI cost. Fixed surface preference only breaks equal-cost/equal-hop ties. Unknown costs block eligibility. | Budget, all-cost-components, tie and fixture tests; `docs/TOKEN_ECONOMICS.md` |
| D02 | Fresh action/resource/session observations are checked during routing, acceptance and execution claim. Caller evidence must be authenticated by a real adapter; the library does not infer access from tool names. | Scoped capability, newer-denial, expiry and execution preflight tests |
| D03 | Transfers require feasible destinations and sufficient estimated savings. Context changes count toward a hop limit. Return envelopes carry results; further work is re-routed rather than unconditionally sent to Chat. | Savings threshold, hop limit and current-context tests; both skills |
| D04 | No feasible plan produces a structured blocked decision, null plan/cost/route and rejection reasons; CLI exit code 3. Invalid input exits 2. | Negative fixtures and CLI tests |
| D05 | Recommended, accepted, running and terminal outcomes are distinct. The local durable ledger requires explicit acceptance and an atomic execution claim. Delivery mode is explicit. | Registration/idempotency/transition tests; `docs/EXECUTION_PROTOCOL.md` |
| D06 | Task, operation, handoff, source/destination session, repository SHA, policy version/hash and evidence identities are carried and validated. Completion preserves the original scope and required tests and ties passing proof to the resulting commit. | Stale-policy/state, wrong-commit evidence and completion-linkage tests |
| D07 | Local SQLite transactions, immutable operation keys and expected revisions prevent duplicate local claims; uncertain results cannot retry blindly. External adapters must provide provider idempotency/reconciliation and stream checkpoint ownership. | Concurrent-claim, conflicting-payload, terminal-state, restart/uncertain and required-test tests; external crash-point tests are an adapter acceptance requirement |
| D08 | A baseline-first, matched-task economics protocol defines quality gates, common units, all cost components, missing data and attribution. The 50–80% goal is labelled an unvalidated hypothesis. | `docs/TOKEN_ECONOMICS.md`; no field savings are claimed or fabricated |

## Simplifications

1. Synchronous isolation is a workspace/session requirement, not a scheduled Chat agent.
2. Scheduling, execution and delivery have distinct roles and contracts.
3. Changed-file counts no longer select a surface; actions, capabilities and cost do.
4. Five speculative gateways are an integration backlog. One measured adapter is
   the first acceptance milestone, with no unsupported claims that gateways exist.
5. Policy parameters and vocabulary are canonical, schemas share generated definitions,
   and skills refer to the contracts instead of maintaining conflicting rule copies.

## Compatibility and verification limits

Handoff **v2 intentionally rejects v1**. Follow the explicit migration steps in
`docs/HANDOFF_SPEC.md`; never invent missing authorizations or evidence to migrate.
The Python engine requires 3.11 or newer and the pinned JSON Schema dependency.

The regression suite was executed before schema/metadata corrections: 13 assertion
failures reproduced the old defects. The final suite adds deterministic routing,
CLI, evidence, scope, persistence and concurrency checks. See `verification.json`
and `tests-after.txt` for measured results.

No UI behavior changed, so application browser testing is not applicable. The
original review dashboard is preserved as a historical artifact. No paid API,
private repository capability, real scheduled task, external effect or economic
improvement was exercised by the synthetic tests.
