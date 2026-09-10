# Current project checkpoint

Task: T10 persistent-environment Codex characterization
Status: CORE_ROUND_TRIP_VALIDATED — T13 quota-burn measurement intentionally stopped; T10A environment characterization and T10B cross-session filesystem persistence are PASS; T10C repository-state persistence is next.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
T10A receipt commit: `5575007aaf2d26903bd0e35cf34f6e8b9cd55f21`
T10B receipt commit: `4266e931e8aef7fa9dedfe2016236a97e8067d1e`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.
- T10A: PASS for a real Codex CLI terminal session on macOS arm64 with ChatGPT-account login reported by `codex login status`, Codex CLI 0.153.4, git 2.50.1, gh 2.83.1, Python 3.9.6, Node v22.16.0, and creation of one controlled local persistence marker.
- T10B: PASS for a genuinely new independent Codex CLI session rediscovering exactly one marker under HOME without being given its path/hash/content, verifying 100 bytes, no trailing newline, SHA-256 `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`, and the exact content created by T10A. This proves same-Mac filesystem persistence across independent Codex CLI sessions, not conversational memory or cross-machine/cloud persistence.

## T13 decision

T13 remains `PARTIAL_STOPPED`, not FAIL. S0 -> S1 showed no observable change at UI precision (99%/100%/100%, credits €0 unchanged). The owner stopped further quota-burning because the displayed granularity is too coarse to justify deliberately consuming allowance.

Receipt: `.chatgpt/test-receipts/T13_MEASUREMENT_STOPPED_2026-09-10.md`.

## T10 current state

- T10A `PASS`: environment/toolchain creation in one real Codex CLI session.
- T10B `PASS`: same-Mac filesystem persistence across a new independent Codex CLI session.
- T10C `NEXT`: create a bounded local checkout of `bacoco/chatgpt-cost-router`, record exact remote/branch/SHA and local test evidence, then exit Codex and use another independent Codex CLI session to rediscover and verify the unchanged checkout state.
- A distinct Ubuntu persistent-VM test remains optional; do not infer VM behavior from local macOS persistence.

T10B durable receipt: `.chatgpt/test-receipts/T10B_CODEX_CLI_PERSISTENCE_2026-09-10.md`.

## Remaining gaps

- T10: `PARTIAL` — T10A/T10B PASS; T10C repository-state persistence next.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — persistent Codex Worker/MCP remains optional.
- T13: `PARTIAL_STOPPED` — preserve S0/S1; do not deliberately burn quota.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — Gmail Developer MCP in ChatGPT/Scheduled Tasks remains separate from the validated Codex Mac Gmail route.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Deferred synthesis

`docs/SURFACE_CAPABILITY_MAP_TODO.md` covers ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, multiple OpenAI accounts, Codex CLI/terminal lanes, Claude/Claude Code or other terminal workers, provider-neutral GitHub handoffs, separate branches/worktrees, and separate quota/cost accounting per account/provider. GitHub remains the durable source of truth and transfer bus.

## Next safe action

Run T10C in two phases. Phase 1 uses a new Codex CLI session to create a bounded local checkout under `~/codex-t10-persistence-test/`, verify the exact Git remote/branch/SHA, run the repository's local verification with Python 3, and leave the checkout unchanged. After fully exiting Codex, Phase 2 starts another independent Codex CLI session and verifies that exact checkout state without using conversation history. No push, PR, merge, application modification, dependency install, paid API or secret access.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.
Deferred map: `docs/SURFACE_CAPABILITY_MAP_TODO.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.