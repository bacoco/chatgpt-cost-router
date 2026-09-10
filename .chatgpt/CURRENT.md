# Current project checkpoint

Task: T28 isolated multi-account Codex worker identity after T27 callable-worker validation
Status: CALLABLE_WORKER_VALIDATED — ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, and Codex CLI local worker have bounded empirical capability evidence. T26 proves Work can consume/push a GitHub handoff return, and T27 proves a normal controller shell can invoke the ChatGPT-authenticated Codex CLI non-interactively with `codex exec`.

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

## Cost / quota decision

T13 remains `PARTIAL_STOPPED`, not FAIL. S0 -> S1 showed no observable change at UI precision (99%/100%/100%, credits €0 unchanged). Do not deliberately burn quota merely to move a coarse percentage display. T27's reported `10,215` tokens is useful per-call telemetry, not a direct measurement of 5-hour/weekly quota decrement.

## Remaining gaps

- T10-VM: distinct Ubuntu/cloud always-on variant remains optional and not formally tested.
- T11/T12: original persistent Worker MCP design remains deferred. T27 proves the smaller callable `codex exec` primitive; only add a daemon/MCP layer if remote/always-on dispatch needs it.
- T13: `PARTIAL_STOPPED`.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` for Gmail Developer MCP in ChatGPT/Scheduled Tasks; Codex Mac Gmail remains separately PASS.
- Worker mesh: multi-account/provider identity isolation, registration, dispatch, quota-aware routing, remote nodes and Claude handoffs remain to validate.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Next safe action

Run **T28 — isolated Codex worker identity / `CODEX_HOME`**. First prove that a fresh alternate `CODEX_HOME` does not inherit the default worker's login or state. Then, only if the owner intentionally authenticates another authorized ChatGPT account into that isolated home, run one bounded `codex exec` and verify the two worker identities remain isolated. This is the minimum proof needed before a broker can address `openai-A` and `openai-B` without manual account swapping.

Specification: `docs/T28_CODEX_HOME_ISOLATION.md`.
T27 receipt: `.chatgpt/test-receipts/T27_CALLABLE_CODEX_CLI_WORKER_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Surface map: `docs/SURFACE_CAPABILITY_MAP.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.
