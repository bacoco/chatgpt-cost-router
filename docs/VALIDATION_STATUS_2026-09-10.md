# Validation status — 10 September 2026

This file is the **authoritative current status snapshot** for the ChatGPT Cost Router experiments. Historical analysis/log files preserve earlier pending states and failures; when they conflict with this snapshot, use this file plus durable receipts and current GitHub state.

## Status vocabulary

- `PASS`: requested behavior actually executed and verified with observable evidence.
- `PARTIAL`: meaningful bounded part verified, but the full measurement/test is incomplete.
- `BLOCKED_MISSING_CONNECTOR`: required connector is unavailable in the tested context.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built because current evidence does not justify it.
- `NOT_YET_FORMALLY_TESTED`: distinct test remains unexecuted even if adjacent capabilities are proven.

## Current validated state

```text
T01 — GitHub Developer MCP identity + repository read       PASS
T02 — files / issues / PR / branches read                  PASS
T03 — temporary issue create / read / close                PASS
T04 — branch + bounded documentation write + commit + PR   PASS
T05 — formal PR review workflow                            PASS
T06 — autonomous defect discovery -> deduplicated issue    PASS
T07 — Scheduled Task -> GitHub Developer MCP read-only     PASS
T08 — Scheduled write + second-run idempotency             PASS
T09 — direct ChatGPT bounded patch + Python/shell tests    PASS
T10 — Codex CLI persistent local Mac worker                PASS — T10A/T10B/T10C1/T10C2
T10-VM — distinct Ubuntu/cloud persistent-VM variant       NOT_YET_FORMALLY_TESTED — optional
T11 — Codex Worker MCP                                      DEFERRED_NOT_JUSTIFIED
T12 — Scheduler -> Codex Worker                             DEFERRED_NOT_JUSTIFIED
T13 — cost/quota experiment                                 PARTIAL_STOPPED
T14 — Gmail Developer MCP                                   BLOCKED_MISSING_CONNECTOR
T14-alt — Codex Mac Chat + standard Gmail connector         PASS — read/search/Sent/draft/send; real self-send verified
T15 — scheduler-chat manual continuation                    PASS
T16 — literal fresh-chat recovery from GitHub checkpoint   PASS
T16A — independent-context recovery from checkpoint         PASS
T17 — Scheduled Task -> Actions MCP detailed read           PASS
T18 — explicit Actions runner/capability gate               PASS
T19 — per-repo scheduler workspace launcher                 PASS
T20 — ChatGPT Cloud -> Codex -> ChatGPT full round trip     PASS
T21 — workflow skill files/frontmatter                      PASS
T22 — project-workspace-bootstrap end-to-end dogfood        PASS
T23 — cloud-to-codex handoff executed with real Codex       PASS
T24 — codex-to-cloud return verified back in ChatGPT        PASS
T25 — Codex Mac Work capability characterization             PASS
T26 — Codex Mac Work -> GitHub durable return                PASS — independently reverified
T27 — callable Codex CLI worker primitive                    PASS — headless codex exec via ChatGPT login
T28A — CODEX_HOME auth/state isolation                        PASS
T28B — distinct second-account worker                         PASS — two isolated authorized accounts
T29 — standalone parallel smoke                               DEFERRED_NOT_JUSTIFIED
T30 — two-worker local broker                                 PARTIAL — code + local unit tests PASS; live broker smoke next

GitHub Actions Developer MCP interactive/read control        PASS
GitHub Actions hosted runner allocation                     BLOCKED_EXTERNAL_CAPACITY — free Actions allowance exhausted during observed test
Repository creation through Developer MCP                   BLOCKED — create_repository returned 403
Paid OpenAI API                                             NOT USED
```

## Recent worker evidence

T27 proved a normal controller shell can call ChatGPT-authenticated Codex non-interactively with `codex exec`, exit 0, read-only sandbox, no work files and per-call token reporting.

T28A proved a fresh alternate `CODEX_HOME` does not inherit the default Codex login.

T28B attempt 1 used the same ChatGPT account and was correctly marked inconclusive. Worker B was then logged out, a second device-auth flow was completed with a different authorized ChatGPT account, and worker B executed a bounded read-only `codex exec` successfully (`gpt-6-astra`, exit 0, 4,432 reported tokens, no work file created) while worker A remained logged in. A local comparison of non-secret identity claims proved different OpenAI user and account/workspace identities. No email address, token, raw identifier or auth-derived hash is retained in GitHub. Therefore T28B is PASS for two distinct addressable local Codex workers.

## T30 — two-worker broker

The first broker implementation is now present: a non-secret worker registry, explicit/automatic selection, ChatGPT login probing under each worker's `CODEX_HOME`, forced `--ephemeral --sandbox read-only` Codex execution, removal of known paid-API-key environment variables, and per-call parsing of model/provider/tokens/duration/exit code. Five isolated unit tests using a fake Codex process passed locally, plus Python compilation checks. This does not yet count as a live broker PASS; one real broker dispatch remains required.

## Remaining gaps

1. **T14 canonical:** connect/test a real Gmail Developer MCP in a compatible ChatGPT/Scheduled-Task context only if scheduler-native Gmail is still required.
2. **T13:** quota/cost behavior remains `PARTIAL_STOPPED`; do not burn allowance merely to move a coarse percentage display.
3. **T10-VM:** remote/always-on variant remains optional and untested.
4. **T11/T12:** daemon/MCP worker remains deferred; add only if remote dispatch actually needs it.
5. **Worker mesh:** T28A/T28B are PASS for two distinct isolated local OpenAI workers. T30 broker code and fake-process unit tests are complete; one live broker dispatch remains before calling the dispatcher lane PASS. Quota-aware routing, remote nodes, useful concurrency and cross-provider workers remain unvalidated.
6. Repository creation from scratch through the tested GitHub Developer MCP remains blocked by the observed 403; existing-repository work is validated.

No paid OpenAI API was used for these validations.
