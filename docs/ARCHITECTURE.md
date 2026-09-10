# Architecture

The model-facing skills interpret a user task into explicit requirements and candidate
plans. The deterministic engine validates those inputs, filters feasibility and
compares costs. A separate receiving adapter performs any actual execution.

| Component | Responsibility |
|---|---|
| skills/ | Interpret remaining work; preserve user constraints; prepare structured inputs |
| policy/routing.json | Canonical versioned policy and tie-break parameters |
| schemas/ + validation.py | Structural contracts, local schema resolution, policy and dates |
| capabilities.py | Scoped, fresh observations and latest-denial handling |
| router.py | Feasibility, recurrence, cost/budget, transfer limits and blocked/routed outputs |
| handoff.py | Versioned transfer and completion invariants |
| ledger.py | Local durable operation identity, claims and terminal states |
| External host adapters | Actual capabilities, authorization, transport, remote effects and reconciliation |

Scheduler, orchestrator, executor and transport are distinct roles. A single plan can
combine them without pretending that all surfaces have the same tools. The engine
has no intrinsic knowledge of a named machine's availability or ChatGPT product limits.

Schemas use fixed local registry resources; validation does not retrieve arbitrary
remote schemas. Runtime data is JSON and SQLite, never a command to execute. Native
skill links point to the full checkout, preserving referenced contracts.

Current scope is local recommendation/validation/state management. Integrations and
measured production economics remain external work described in [ROADMAP](ROADMAP.md).
