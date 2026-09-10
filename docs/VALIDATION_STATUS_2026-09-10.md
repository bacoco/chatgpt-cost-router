# Validation status — 10 September 2026

This is the **authoritative current status snapshot**. Historical experiment logs intentionally preserve earlier pending/failure states; when they conflict, use this file plus durable receipts and current GitHub state.

## Status vocabulary

- `PASS`: requested behavior actually executed and verified with observable evidence.
- `PARTIAL_STOPPED`: useful evidence preserved, but further measurement was intentionally stopped.
- `BLOCKED_MISSING_CONNECTOR`: required connector unavailable in the tested context.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built/tested because current evidence does not justify the cost.
- `NOT_YET_FORMALLY_TESTED`: distinct test remains unexecuted.

## Current validated state

```text
T01-T09     ChatGPT/GitHub cloud capabilities                 PASS where applicable
T10         Codex CLI persistent local Mac worker             PASS — A/B/C1/C2
T10-VM      distinct Ubuntu/cloud persistent VM               NOT_YET_FORMALLY_TESTED — optional
T11/T12     original persistent Worker MCP / scheduler lane   DEFERRED_NOT_JUSTIFIED
T13         quota/cost experiment                              PARTIAL_STOPPED
T14         Gmail Developer MCP in ChatGPT/Scheduled Tasks    BLOCKED_MISSING_CONNECTOR
T14-alt     Codex Mac Chat + built-in Gmail                   PASS
T15/T16/16A scheduler-chat continuation / repo recovery       PASS
T17/T18/T19 Actions control gate / repo scheduler workspace   PASS
T20/T23/T24 ChatGPT Cloud -> Codex -> ChatGPT round trip      PASS
T21/T22     workflow skills / project bootstrap               PASS
T25         Codex Mac Work capability characterization        PASS
T26         Codex Mac Work -> pushed GitHub return            PASS — independently reverified
T27         headless callable Codex CLI via codex exec        PASS
T28A        CODEX_HOME auth/state isolation                   PASS
T28B        two distinct authorized account workers           PASS
T29         standalone parallel smoke                         DEFERRED_NOT_JUSTIFIED
T30         two-worker local broker                           PASS — live alias dispatch verified
T31A        quota/budget-aware selection logic                PASS — deterministic local tests
T32         private remote worker over Tailscale Serve        PASS — live second-device dispatch

GitHub Actions control plane                                 PASS
GitHub hosted runner allocation                              BLOCKED_EXTERNAL_CAPACITY during observed test
Create repository via tested GitHub Developer MCP            BLOCKED — observed 403
Paid OpenAI API                                               NOT USED
```

## Worker evidence

T27 proved that a normal controller shell can invoke ChatGPT-authenticated Codex non-interactively with `codex exec`, read-only/ephemeral execution and per-call token telemetry.

T28A proved a fresh alternate `CODEX_HOME` does not inherit the default Codex login. T28B then established two distinct authorized OpenAI/ChatGPT account identities in isolated worker homes; worker B executed successfully while worker A remained authenticated. GitHub retains only aliases and the fact of distinct identity — no email address, token, raw identifier or auth-derived fingerprint.

## T30 — live broker PASS

A pinned checkout at `d4da83ada93df28bfdc80064c41f532827567880` ran **45/45 repository tests PASS**. Live broker `probe` saw both `openai-A` and `openai-B` ready. Zero-model `select` chose `openai-A`. An explicit broker dispatch to `openai-B` returned `BROKER_OK`, provider `openai`, model `gpt-6-astra`, `4,607` reported tokens, `5.527 s`, and exit code `0`. Paid-API environment variables were stripped, execution was `read-only` + `ephemeral`, and the workspace remained empty.

Receipt: `.chatgpt/test-receipts/T30_TWO_WORKER_BROKER_LIVE_2026-09-10.md`.

This proves a controller can address a specific isolated ChatGPT-authenticated Codex worker by alias without manual account swapping. It does not yet prove remote transport or useful concurrency.

## T31A — budget-aware selection

The broker now accepts a separate non-secret budget-state file. It supports per-worker `available/busy/quota_exhausted/unknown`, observed 5-hour remaining percentage, weekly remaining percentage, and local reported-token counters. Known busy/exhausted workers are excluded before a Codex probe. At equal cost class, known allowance headroom is preferred over unknown headroom and larger minimum 5-hour/weekly headroom wins before static priority. Explicit selection of a known exhausted worker fails before any model call.

Ten isolated worker/budget tests pass locally; the modified broker compiles. These tests use fake Codex processes and consume no Codex allowance.

Important boundary: automatic trustworthy ingestion of OpenAI's live 5-hour/weekly allowance is **not yet proven**. Local `tokens used` output is telemetry, not a direct provider-quota decrement measurement. Unknown values remain `UNKNOWN`; the broker never invents them.

Specification: `docs/T31_QUOTA_AWARE_SELECTION.md`.

## T32 — private remote worker transport

A loopback-only HTTP facade is implemented for use behind Tailscale Serve. It requires `Tailscale-User-Login` to match a local allowlist and separately limits which worker aliases may be called. Remote JSON accepts only `worker` and `prompt`; clients cannot supply local filesystem paths. Each call receives a temporary private task directory that is removed afterwards. Codex remains `--ephemeral --sandbox read-only`, paid-API environment variables are stripped by the existing broker, and returned JSON omits `CODEX_HOME`, task paths and Codex stderr/session ids.

Six isolated tests pass without a model call: identity allowlisting, request schema/size limits, worker allowlisting, remote path redaction, temporary-workspace cleanup and fake Codex dispatch.

Live proof was then completed from a second Tailscale device. MagicDNS resolved the worker Mac and `tailscale ping` reached it. Through the Serve HTTPS endpoint, `/v1/health` returned `ok=true` with `transport=tailscale-serve`, `/v1/workers` exposed only allowlisted `openai-B` as ready, and one bounded remote `run` returned `REMOTE_OK`, provider `openai`, model `gpt-6-astra`, `4,610` reported tokens, `6.753 s`, and exit `0`. The returned telemetry confirmed `read-only`, `ephemeral`, and paid-API environment removal.

Therefore T32 is PASS for **private second-device remote dispatch to a worker physically running on another Mac**. The live request used the owner's Tailscale identity. A separately shared external person's identity/ACL path remains untested and should not be conflated with the already-proven transport primitive.

Specification: `docs/T32_REMOTE_WORKER.md`.
Receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.

## Remaining gaps

1. Automatic/reliable live 5-hour and weekly allowance ingestion per account.
2. Node registration/discovery so the control plane can route across local and remote worker hosts without hard-coded placement.
3. Separately shared external-user Tailscale identity/ACL smoke when such a user is available.
4. Always-on supervision/service packaging for remote nodes.
5. Useful broker-managed concurrency when an actual workload benefits from it.
6. Claude/other-provider worker adapters plus provider-neutral handoff.
7. Canonical Gmail Developer MCP in ChatGPT/Scheduled Tasks only if still operationally required.
8. Repository creation through the tested GitHub Developer MCP remains blocked by the observed 403.

No paid OpenAI API was used for these validations.
