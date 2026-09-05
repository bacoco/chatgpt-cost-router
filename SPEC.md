# Product Specification

## Objective and implemented scope

Recommend an authorized, sufficient plan with the lowest estimated total marginal
cost among supplied candidates. The skills perform task interpretation; the Python
engine deterministically checks a structured request. Live discovery and remote
execution require host-specific adapters and are not supplied by this repository.

## Requirements

- Canonical surfaces: CHAT, SCHEDULED_CHAT, LOCAL_TOOL, CODEX, WORK, EXTERNAL_API.
- HYBRID is a decision for a multi-surface plan, not an executable destination.
- Runtime capability evidence is action/resource/surface/session-scoped and expiring.
- User scope and restrictions take precedence over a surface preference.
- Required actions must exactly match the plan; duplicate actions are rejected.
- Recurring plans have exactly one initial scheduler and at least one executor.
- Unknown cost or capability yields ineligibility, never invented success.
- No feasible candidate yields `blocked` with reasons and no selected plan.
- Cost uses one comparable unit, all stated components and explicit limits.
- Transfer policy considers current-context feasibility, savings and hop count.
- Policy version and canonical-content hash accompany decisions and handoffs.
- Handoff v2 preserves identity, scope, state and verifiable completion criteria.
- A local durable ledger separates recommendation, acceptance and execution claims.
- Production adapters must enforce the execution/recovery protocol at each effect.

## Acceptance

The executable fixtures define scoped inputs and explicit expected results. All
canonical and negative cases must pass CI. The former >90% routing-agreement target
is reserved for a separate human-labeled evaluation set with defined capabilities,
accepted plans, confidence, exclusions and denominator; it is not a claim of model
quality from a deterministic test suite.

Economic targets (>=60% less Work/Codex usage, <10% unnecessary escalation and no
material quality regression) are hypotheses to validate on matched completed tasks.
A typical handoff should stay below 5 KiB by referencing artifacts. This is not a
universal validity limit; preserve essential instructions even when they are longer.
