# Current project checkpoint

Task: T10 persistent-environment Codex characterization
Status: CORE_ROUND_TRIP_VALIDATED — T13 quota-burn measurement intentionally stopped; T10A environment characterization, T10B cross-session filesystem persistence, and T10C1 persistent repository-state creation are PASS; T10C2 independent repository recovery is next.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before this checkpoint write: `aadd31f5b057511a9d9f23683c4aa3f5d7150ed8`
T10A receipt commit: `5575007aaf2d26903bd0e35cf34f6e8b9cd55f21`
T10B receipt commit: `4266e931e8aef7fa9dedfe2016236a97e8067d1e`
T10C1 receipt commit: `aadd31f5b057511a9d9f23683c4aa3f5d7150ed8`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.
- T10A: PASS for a real Codex CLI terminal session on macOS arm64 with ChatGPT-account login reported by `codex login status`, Codex CLI 0.153.4, git 2.50.1, gh 2.83.1, Python 3.9.6, Node v22.16.0, and creation of one controlled local persistence marker.
- T10B: PASS for a genuinely new independent Codex CLI session rediscovering exactly one marker under HOME without being given its path/hash/content, verifying 100 bytes, no trailing newline, SHA-256 `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`, and the exact content created by T10A.
- T10C1: PASS for a bounded persistent checkout at `/Users/loic/codex-t10-persistence-test/chatgpt-cost-router`, with `main` and `origin/main` both at `230e247cdd838f64a51b745df36fad6a8e73ec71`, clean before/after, 40 unit tests PASS, schema generation PASS, no repo files changed, and external state file SHA-256 `049d0dd34d31cfa72e16e96d8742e90b5d6a650c3a6f42e1714455aa406975f9`.

## T13 decision

T13 remains `PARTIAL_STOPPED`, not FAIL. S0 -> S1 showed no observable change at UI precision (99%/100%/100%, credits €0 unchanged). The owner stopped further quota-burning because the displayed granularity is too coarse to justify deliberately consuming allowance.

Receipt: `.chatgpt/test-receipts/T13_MEASUREMENT_STOPPED_2026-09-10.md`.

## T10 current state

- T10A `PASS`: environment/toolchain creation in one real Codex CLI session.
- T10B `PASS`: same-Mac filesystem persistence across a new independent Codex CLI session.
- T10C1 `PASS`: persistent local repository checkout created/reconciled and locally verified with no repository mutation.
- T10C2 `NEXT`: after fully exiting Codex, a new independent Codex CLI session must rediscover the existing checkout and external state file without being given their exact path/hash/SHA, verify that the checkout still has the expected recorded branch/HEAD/remote state, and distinguish local persistence from live remote advancement.
- A distinct Ubuntu persistent-VM test remains optional; do not infer VM behavior from local macOS persistence.

T10 durable receipts:
- `.chatgpt/test-receipts/T10A_CODEX_CLI_ENVIRONMENT_2026-09-10.md`
- `.chatgpt/test-receipts/T10B_CODEX_CLI_PERSISTENCE_2026-09-10.md`
- `.chatgpt/test-receipts/T10C1_CODEX_CLI_REPO_STATE_2026-09-10.md`

## Remaining gaps

- T10: `PARTIAL` — T10A/T10B/T10C1 PASS; T10C2 independent repository-state recovery next.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — persistent Codex Worker/MCP remains optional.
- T13: `PARTIAL_STOPPED` — preserve S0/S1; do not deliberately burn quota.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — Gmail Developer MCP in ChatGPT/Scheduled Tasks remains separate from the validated Codex Mac Gmail route.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Deferred synthesis

`docs/SURFACE_CAPABILITY_MAP_TODO.md` covers ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, multiple OpenAI accounts, Codex CLI/terminal lanes, Claude/Claude Code or other terminal workers, provider-neutral GitHub handoffs, separate branches/worktrees, and separate quota/cost accounting per account/provider. GitHub remains the durable source of truth and transfer bus.

## Next safe action

Run T10C2 from a completely new Codex CLI session after exiting T10C1. It must rediscover the bounded T10 persistence area under HOME without conversation history, read and verify the external T10C repository-state file, locate the persistent checkout, verify its local branch/HEAD/remote configuration and clean working tree, and report whether `origin/main` is only the stored remote-tracking value or whether a live fetch advances it. Do not reset or update the checkout merely because remote `main` has advanced since T10C1; the purpose is to prove persistence of the recorded local state. No push, PR, merge, application modification, dependency install, paid API or secret access.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.
Deferred map: `docs/SURFACE_CAPABILITY_MAP_TODO.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.