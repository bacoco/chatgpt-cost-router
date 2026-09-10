# Current project checkpoint

Task: T10 persistent-environment Codex characterization
Status: CORE_ROUND_TRIP_VALIDATED — T13 active quota-burn measurement intentionally stopped; next bounded experiment is T10.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before this checkpoint write: `f27dd12ce351ae95ec3c2e163e38c3e4676f4e32`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.

## T13 decision

T13 remains `PARTIAL_STOPPED`, not FAIL.

Observed S0 -> S1 after the ChatGPT.com + GitHub Developer MCP leg:
- general weekly: 99% left -> 99% left;
- GPT-5.3-Codex-Spark 5h: 100% left -> 100% left;
- GPT-5.3-Codex-Spark weekly: 100% left -> 100% left;
- credits: €0 -> €0.

This proves only `no observable change at UI precision`. The owner stopped further quota-burning because the percentage display is too coarse and forcing a visible delta would waste allowance. Operationally, ordinary ChatGPT Chat is kept separate from the agentic/Codex pool for routing unless future higher-resolution product evidence makes the distinction material.

Receipt: `.chatgpt/test-receipts/T13_MEASUREMENT_STOPPED_2026-09-10.md`.

## Remaining gaps

- T10: `NOT_YET_FORMALLY_TESTED` — characterize persistent Codex terminal/local environment first; require a separate Ubuntu VM only if that distinct architecture remains useful.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — persistent Codex Worker/MCP remains optional.
- T13: `PARTIAL_STOPPED` — preserve S0/S1; do not deliberately burn quota.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — Gmail Developer MCP in ChatGPT/Scheduled Tasks remains separate from the validated Codex Mac Gmail route.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Deferred synthesis

`docs/SURFACE_CAPABILITY_MAP_TODO.md` now also covers multi-account and multi-provider operation: ChatGPT account A, multiple Codex accounts/surfaces, Claude/Claude Code or other terminal workers, provider-neutral GitHub handoffs, separate branches/worktrees, and separate quota/cost accounting per account/provider. GitHub remains the durable source of truth and transfer bus.

## Next safe action

Run T10 as a bounded characterization of the actual Codex Mac/terminal persistent environment. Verify persistence, git/GitHub access, Python/toolchain and Codex CLI/account-auth behavior without application mutation. Only after that evidence decide whether a distinct Ubuntu persistent-VM test is still worth building.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.
Deferred map: `docs/SURFACE_CAPABILITY_MAP_TODO.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.