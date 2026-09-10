# Current project checkpoint

Task: T10 persistent-environment Codex characterization
Status: CORE_ROUND_TRIP_VALIDATED — T13 quota-burn measurement intentionally stopped; T10A Codex CLI environment characterization is PASS and T10B independent-session persistence is next.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
T10A receipt commit: `5575007aaf2d26903bd0e35cf34f6e8b9cd55f21`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.
- T10A: PASS for a real Codex CLI terminal session on macOS arm64 with ChatGPT-account login reported by `codex login status`, Codex CLI 0.153.4, git 2.50.1, gh 2.83.1, Python 3.9.6, Node v22.16.0, and creation of one controlled local persistence marker. The running session's authentication was not independently observable, so the receipt does not overclaim that point.

## T13 decision

T13 remains `PARTIAL_STOPPED`, not FAIL.

Observed S0 -> S1 after the ChatGPT.com + GitHub Developer MCP leg:
- general weekly: 99% left -> 99% left;
- GPT-5.3-Codex-Spark 5h: 100% left -> 100% left;
- GPT-5.3-Codex-Spark weekly: 100% left -> 100% left;
- credits: €0 -> €0.

This proves only `no observable change at UI precision`. The owner stopped further quota-burning because the percentage display is too coarse and forcing a visible delta would waste allowance. Operationally, ordinary ChatGPT Chat is kept separate from the agentic/Codex pool for routing unless future higher-resolution product evidence makes the distinction material.

Receipt: `.chatgpt/test-receipts/T13_MEASUREMENT_STOPPED_2026-09-10.md`.

## T10 current state

T10 is now split into bounded subtests:

- T10A `PASS`: environment/toolchain creation in one real Codex CLI session.
- T10B `NEXT`: start a genuinely new Codex CLI session and independently rediscover/verify the marker without being given its path or hash in the new prompt.
- T10C `PENDING`: only after T10B, use the persistent local environment for a bounded repository clone/test exercise and verify state across another session if useful.
- A distinct Ubuntu persistent-VM test remains optional; do not infer VM behavior from local macOS persistence.

T10A marker evidence:
- path: `/Users/loic/codex-t10-persistence-test/T10_PERSISTENCE_MARKER.txt`
- SHA-256: `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`
- exact size: 100 bytes, no trailing newline.

Durable receipt: `.chatgpt/test-receipts/T10A_CODEX_CLI_ENVIRONMENT_2026-09-10.md`.

## Remaining gaps

- T10: `PARTIAL` — T10A PASS; T10B persistence proof next.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — persistent Codex Worker/MCP remains optional.
- T13: `PARTIAL_STOPPED` — preserve S0/S1; do not deliberately burn quota.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — Gmail Developer MCP in ChatGPT/Scheduled Tasks remains separate from the validated Codex Mac Gmail route.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Deferred synthesis

`docs/SURFACE_CAPABILITY_MAP_TODO.md` covers ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, multiple OpenAI accounts, Codex CLI/terminal lanes, Claude/Claude Code or other terminal workers, provider-neutral GitHub handoffs, separate branches/worktrees, and separate quota/cost accounting per account/provider. GitHub remains the durable source of truth and transfer bus.

## Next safe action

Run T10B from a completely new Codex CLI session after exiting T10A. The new prompt must not disclose the marker path or hash. The session must locate the T10 marker under the user's home directory, report its absolute path, exact content metadata, size and SHA-256, and state whether that proves filesystem persistence across Codex CLI sessions. No repository mutation, install, global configuration change, paid API or secret access.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.
Deferred map: `docs/SURFACE_CAPABILITY_MAP_TODO.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.