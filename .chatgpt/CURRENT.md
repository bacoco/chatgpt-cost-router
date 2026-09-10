# Current project checkpoint

Task: T31 quota/budget-aware routing after live T30 broker validation
Status: `TWO_WORKER_BROKER_VALIDATED` — two distinct authorized ChatGPT accounts are isolated as local Codex workers; the broker can address either by alias. T31A budget-aware selection logic is implemented and locally tested. Automatic provider-quota ingestion remains unproven.

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

## Cost / quota boundary

T13 remains `PARTIAL_STOPPED`. Per-call Codex token counts are useful local telemetry but are not direct measurements of the provider's 5-hour or weekly allowance. T31A can consume trusted 5-hour/weekly percentage observations and local token counters, but it leaves unknown values `UNKNOWN` and never invents quota.

## Remaining gaps

- Automatic/reliable ingestion of live per-account 5-hour and weekly allowance.
- Remote worker transport / always-on nodes.
- Useful concurrency through the broker when operationally needed.
- Claude/other-provider workers and provider-neutral handoff.
- T14 canonical Gmail Developer MCP in ChatGPT/Scheduled Tasks only if still required.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed 403.

## Next useful direction

Local callability, account isolation, alias dispatch and budget-aware selection logic are now proven. The next high-value architectural step is a secure **remote worker node**: expose only the broker/worker interface over an authenticated private transport, not raw Codex or shell access. A remote user/controller should submit bounded work to a named worker; the worker executes locally under its own `CODEX_HOME` and returns telemetry/result. GitHub remains durable project state where appropriate.

T30 receipt: `.chatgpt/test-receipts/T30_TWO_WORKER_BROKER_LIVE_2026-09-10.md`.
T31 specification: `docs/T31_QUOTA_AWARE_SELECTION.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
