# Current project checkpoint

Task: T30 two-worker Codex broker prototype
Status: TWO_DISTINCT_CODEX_WORKERS_VALIDATED — T28B proves two distinct authorized ChatGPT accounts can coexist as isolated Codex CLI workers on one Mac. T30 broker code is implemented and locally unit-tested; one real broker-dispatch smoke remains.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
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
- T27: PASS — from a normal macOS shell, `codex exec` 0.153.4 ran non-interactively using the existing ChatGPT login, model `gpt-6-astra`, provider `openai`, `read-only` sandbox and `approval: never`; it returned the requested worker response, exited 0, left the empty work directory unchanged, and reported `10,215` tokens used.
- T28A: PASS — a fresh alternate `CODEX_HOME` did not inherit the default login.
- T28B: PASS — worker B was deliberately authenticated with a second authorized ChatGPT account. Local identity comparison verified distinct OpenAI user/account identities without storing emails, raw ids, tokens or hashes in GitHub. Worker B executed a bounded read-only `codex exec` with exit 0 and 4,432 reported tokens while worker A remained logged in.

## Cost / quota decision

T13 remains `PARTIAL_STOPPED`, not FAIL. Do not deliberately burn quota merely to move a coarse percentage display. Per-call Codex token counts are useful telemetry, not direct 5-hour/weekly quota decrement measurements.

## Remaining gaps

- T10-VM: distinct Ubuntu/cloud always-on variant remains optional and not formally tested.
- T11/T12: original persistent Worker MCP design remains deferred. T27 proves the smaller callable `codex exec` primitive; only add a daemon/MCP layer if remote/always-on dispatch needs it.
- T13: `PARTIAL_STOPPED`.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` for Gmail Developer MCP in ChatGPT/Scheduled Tasks; Codex Mac Gmail remains separately PASS.
- T29: `DEFERRED_NOT_JUSTIFIED` as a standalone concurrency burn test.
- Worker mesh: T28A/T28B are PASS for two distinct local OpenAI account workers. T30 broker code is implemented with explicit/auto selection, zero-token `select`, ChatGPT-login probes, CODEX_HOME isolation, paid-API-env stripping and telemetry parsing; one real broker-dispatch smoke remains. Quota-aware routing, remote nodes, useful concurrency and Claude handoffs remain later work.

## Next safe action

Run `scripts/worker_broker.py select` first to verify automatic live selection without model/token use, then run exactly one real T30 broker dispatch to `openai-B` and verify worker/model/tokens/exit code plus an unchanged read-only workspace. Do not build concurrency, daemon/MCP or remote transport yet.

T30 specification: `docs/T30_TWO_WORKER_BROKER.md`.
T28B receipt: `.chatgpt/test-receipts/T28B_DISTINCT_MULTI_ACCOUNT_WORKERS_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
