# Current project checkpoint

Task: T33 worker-node registration / remote-user expansion after T32 live remote transport
Status: `REMOTE_WORKER_VALIDATED` — T32 is PASS from a second Tailscale device: private HTTPS Serve reached the loopback-only broker facade and remotely dispatched `openai-B` with redacted telemetry and no paid API path. The live caller used the owner's Tailscale identity; a separately shared external user remains an optional distinct smoke.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Validated core

- T01-T09: PASS where applicable.
- T10 local macOS Codex CLI persistent worker: PASS through T10A/T10B/T10C1/T10C2.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send including one verified self-send.
- T15/T16/T16A/T19: PASS for scheduler/chat continuation, fresh recovery and repo-backed workspace.
- T17/T18: PASS for Actions control-plane capability gate; hosted runner capacity was separately exhausted.
- T20/T23/T24: PASS for ChatGPT Cloud -> GitHub -> Codex -> GitHub -> ChatGPT round trip.
- T21/T22: PASS for workflow skills and project bootstrap.
- T25/T26: PASS for Codex Mac Work characterization plus pushed GitHub return.
- T27: PASS for headless `codex exec` from a normal shell using ChatGPT authentication.
- T28A: PASS for `CODEX_HOME` auth/state isolation.
- T28B: PASS for two distinct authorized OpenAI/ChatGPT account identities in isolated worker homes. No email, token, raw identifier or auth-derived fingerprint is stored in GitHub.
- T29: `DEFERRED_NOT_JUSTIFIED` as a standalone parallel quota-burn test.
- T30: PASS. Live broker `probe` saw both workers ready; zero-model `select` chose A; explicit broker dispatch to B returned `BROKER_OK`, model `gpt-6-astra`, 4,607 reported tokens, 5.527 s, exit 0, paid-API environment stripped, read-only/ephemeral sandbox, empty workspace afterwards.
- T31A: PASS for deterministic quota/budget-aware selection logic. Ten isolated worker/budget tests pass without a model call.
- T32: PASS. A second Tailscale device resolved/pinged the worker Mac, reached `/v1/health` and `/v1/workers`, then remotely dispatched `openai-B`. Result: `REMOTE_OK`, model `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, paid-API environment removed. The remote caller was the owner's Tailscale identity; separate external-user sharing remains untested.

## Cost / quota boundary

T13 remains `PARTIAL_STOPPED`. Per-call Codex token counts are useful local telemetry but are not direct measurements of the provider's 5-hour or weekly allowance. T31A can consume trusted 5-hour/weekly percentage observations and local token counters, but it leaves unknown values `UNKNOWN` and never invents quota.

## Remaining gaps

- Automatic/reliable ingestion of live per-account 5-hour and weekly allowance.
- Node registration/discovery across local and remote worker hosts.
- Separately shared external-user Tailscale identity/ACL smoke when such a user is available.
- Always-on/service supervision for remote nodes.
- Useful concurrency through the broker when operationally needed.
- Claude/other-provider workers and provider-neutral handoff.
- T14 canonical Gmail Developer MCP in ChatGPT/Scheduled Tasks only if still required.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed 403.

## Next useful direction

The private remote transport primitive is now proven. Next high-value work is to make remote nodes register their capabilities/availability/budget with the broker/control plane and route across nodes without hard-coding where a worker lives. A separate partner/external-user smoke is useful only when that person is available: share the node through Tailscale, add only that exact Tailscale login to the local allowlist, and verify the same `/v1/health` -> `/v1/workers` -> bounded `run` path.

T30 receipt: `.chatgpt/test-receipts/T30_TWO_WORKER_BROKER_LIVE_2026-09-10.md`.
T31 specification: `docs/T31_QUOTA_AWARE_SELECTION.md`.
T32 specification: `docs/T32_REMOTE_WORKER.md`.
T32 receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
