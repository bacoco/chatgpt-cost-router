# Current project checkpoint

Task: T28 isolated multi-account Codex worker identity after T27 callable-worker validation
Status: WORKER_IDENTITY_ISOLATION_VALIDATED — core surfaces plus callable Codex CLI are validated, and T28A proves a separate `CODEX_HOME` isolates Codex authentication/state from the default worker. T28B attempt 1 authenticated the isolated worker, but the owner confirmed it used the same ChatGPT account as worker A; therefore multi-account separation remains unproven.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before T27 consolidation: `11ee1c043e518e9ebc2af232d17b319ab52e322b`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T10 local macOS Codex CLI worker: PASS end to end through T10A/T10B/T10C1/T10C2 — persistent filesystem/workspace, repeatable local tests, and safe remote reconciliation.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.
- T25: PASS for Codex Mac Work characterization: direct GitHub read, Gmail search, local filesystem, shell and Python actually executed.
- T26: PASS after independent GitHub verification. Work read the historical T20 handoff and pushed exactly one allowed return file on `test/t26-work-return-20260910` in commit `290a40a87511c2696f37dc45fa885ef02bbdf647`.
- T27: PASS — from a normal macOS shell, `codex exec` 0.153.4 ran non-interactively using the existing ChatGPT login, model `gpt-6-astra`, provider `openai`, `read-only` sandbox and `approval: never`; it returned the requested worker response, exited 0, left the empty work directory unchanged, and reported `10,215` tokens used. `codex mcp` and `codex mcp-server` are present but were only discovered via help.
- T28A: PASS — the default worker reported `Logged in using ChatGPT` before and after, while fresh `CODEX_HOME=~/codex-worker-homes/openai-B` reported `Not logged in` with exit code 1 and did not inherit the default credentials. No credentials were copied; the isolated home contained only `tmp/` after the check.
- T28B attempt 1: `INCONCLUSIVE_SAME_ACCOUNT` — isolated worker B authenticated successfully and one read-only `codex exec` returned `WORKER_OK` with exit 0 and 4,432 reported tokens while A remained logged in, but the owner confirmed B was authenticated to the same ChatGPT account as A. This is not evidence of independent account quotas.

## Cost / quota decision

T13 remains `PARTIAL_STOPPED`, not FAIL. S0 -> S1 showed no observable change at UI precision (99%/100%/100%, credits €0 unchanged). Do not deliberately burn quota merely to move a coarse percentage display. T27's reported `10,215` tokens is useful per-call telemetry, not a direct measurement of 5-hour/weekly quota decrement.

## Remaining gaps

- T10-VM: distinct Ubuntu/cloud always-on variant remains optional and not formally tested.
- T11/T12: original persistent Worker MCP design remains deferred. T27 proves the smaller callable `codex exec` primitive; only add a daemon/MCP layer if remote/always-on dispatch needs it.
- T13: `PARTIAL_STOPPED`.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` for Gmail Developer MCP in ChatGPT/Scheduled Tasks; Codex Mac Gmail remains separately PASS.
- Worker mesh: T28A identity isolation is PASS. T28B attempt 1 used the same account in both isolated homes and is inconclusive for multi-account routing. A genuinely second authorized OpenAI account, multi-worker dispatch/concurrency, quota-aware routing, remote nodes and Claude handoffs remain to validate.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Next safe action

T28A is complete. Retry **T28B** with a genuinely second authorized ChatGPT account: first log out only `CODEX_HOME=~/codex-worker-homes/openai-B`, verify the default worker A remains logged in, then authenticate B deliberately with the second account (prefer `codex login --device-auth` and an incognito/separate browser profile to avoid automatic reuse of account A). Confirm both homes remain logged in, then run one bounded read-only `codex exec` under alias `openai-B`. Do not copy credentials between homes and do not disturb the default worker.

Specification: `docs/T28_CODEX_HOME_ISOLATION.md`.
T28A receipt: `.chatgpt/test-receipts/T28A_CODEX_HOME_ISOLATION_2026-09-10.md`.
T27 receipt: `.chatgpt/test-receipts/T27_CALLABLE_CODEX_CLI_WORKER_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Surface map: `docs/SURFACE_CAPABILITY_MAP.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.
