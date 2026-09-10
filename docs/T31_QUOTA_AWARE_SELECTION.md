# T31 — quota/budget-aware worker selection

Status: `T31A CODE COMPLETE — LOCAL TESTS PASS; LIVE QUOTA INGESTION NOT YET PROVEN`

## Goal

Extend the validated two-worker broker so routing can consider per-worker allowance/budget observations without invoking a model merely to choose a worker.

## Implemented

- `cost_router/worker_budget.py` parses a non-secret budget-state file.
- `examples/worker-budgets.json` provides the schema-shaped local state for `openai-A` and `openai-B` with unknown values by default.
- `scripts/worker_broker.py --budget-state ...` can print budgets and use them for `select` / `run`.
- Known `busy` or `quota_exhausted` workers are excluded.
- At the same cost class, a worker with known allowance headroom is preferred over one with unknown headroom; larger minimum 5-hour/weekly headroom wins before static priority.
- Explicit selection of a worker known to be exhausted/busy fails before any Codex probe/model call.
- Unknown allowance values remain `UNKNOWN`; the broker never invents quota.

The state supports:

- `five_hour_remaining_pct`;
- `weekly_remaining_pct`;
- `reported_tokens_5h`;
- `reported_tokens_weekly`;
- availability state (`available`, `busy`, `quota_exhausted`, `unknown`).

The reported-token counters are local telemetry and are **not** treated as equivalent to OpenAI's 5-hour or weekly percentage allowance.

## Verification

Ten isolated worker/budget tests pass locally and the modified broker compiles. These tests use fake Codex processes, so they consume no Codex allowance.

## Remaining boundary

Automatic, reliable ingestion of the provider's live 5-hour/weekly allowance remains unproven. Until such telemetry is available, those percentages must be supplied by a trusted observation or left `null`. This is intentionally separate from T13's stopped quota-burn experiment.
