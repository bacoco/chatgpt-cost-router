# Roadmap and actual status

## Implemented in this repository

- Canonical policy with cost comparison, feasibility and explicit blocked results.
- Typed capability, plan, decision and handoff v2 contracts.
- Two valid repository-backed skills and native repository discovery links.
- Deterministic CLI plus contextualized canonical and adversarial fixtures.
- Scope/freshness, budget, de-escalation and completed-return verification.
- Local durable operation ledger with atomic execution claims and no blind uncertain retry.
- Regression tests and GitHub Actions workflow; audit and remediation records.

## First integration milestone

Before changing real routing, collect the baseline described in TOKEN_ECONOMICS.
Implement one host observer/adapter for a bounded GitHub -> CI task. Verify the full
path against actual authorization, commit-specific CI evidence, capability expiry,
provider idempotency/reconciliation and output acceptance. The CLI alone does not
prove that this integration exists or has passed.

## Scheduling milestone

Implement the chosen scheduler's per-run preflight, durable checkpoint and stream
concurrency contract. Exercise publication/checkpoint crash points and late runs.
The local operation ledger is one building block, not a distributed scheduler.

## Optional specialist gateways

Add media/machine/VPS/model adapters only after workload and measured benefit justify
them. Measure shifted costs and quality continuously, tune a versioned policy and
retain the baseline. Do not postpone baseline collection until the final phase.
