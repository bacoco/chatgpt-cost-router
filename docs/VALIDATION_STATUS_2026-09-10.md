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
T10 — Codex CLI persistent-VM proof of concept              NOT_YET_FORMALLY_TESTED
T11 — Codex Worker MCP                                      DEFERRED_NOT_JUSTIFIED
T12 — Scheduler -> Codex Worker                             DEFERRED_NOT_JUSTIFIED
T13 — cost/quota experiment                                 PARTIAL
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

GitHub Actions Developer MCP interactive/read control        PASS
GitHub Actions hosted runner allocation                     BLOCKED_EXTERNAL_CAPACITY — free Actions allowance exhausted during observed test
Repository creation through Developer MCP                   BLOCKED — create_repository returned 403
Paid OpenAI API                                             NOT USED
```

## T20 / T23 / T24 exact evidence

Original Cloud handoff:

```text
branch: test/t20-cloud-to-codex-handoff-20260910
handoff: .chatgpt/handoffs/T20/TO_CODEX.md
handoff commit: be8b29f191b877072e1def641aa3aeec51ec2ab8
```

A real Codex session consumed that exact handoff. Attempt 1 preserved the environment block because `python` was absent and both literal commands exited 127. After explicit authorization to use Python 3, Codex reported Python 3.9.6 and ran:

```text
python3 -m unittest discover -s tests -v
-> 40 tests passed, exit 0, 1.462s

python3 scripts/build_schemas.py
-> exit 0, no output, no file changes
```

Codex pushed `.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md` in final return commit `16bb9c9dc5d691334c57897d7145df1a16b83d00`. T24 independently verified through `GitHub — bacoco TEST` that the only post-handoff changed file across the blocked and passing Codex commits is that return artifact, with no PR on the handoff branch.

Durable receipts:

```text
.chatgpt/test-receipts/T20_CLOUD_TO_CODEX_HANDOFF_READY_2026-09-10.md
.chatgpt/test-receipts/T23_CODEX_EXECUTION_2026-09-10.md
.chatgpt/test-receipts/T24_CODEX_RETURN_VERIFICATION_2026-09-10.md
```

## T14-alt — Codex Mac Chat standard Gmail connector

A real Codex Mac Chat session tested the built-in `Gmail` connector in that surface. This is **not** evidence for Gmail Developer MCP availability inside ChatGPT or Scheduled Tasks.

Observed/executed:

```text
Gmail profile/authentication                 PASS
recent search newer_than:7d                 PASS — 3 results under a 3-result limit
Sent search in:sent newer_than:7d           PASS — 3 results under a 3-result limit
message read                                PASS
draft create                                PASS — exactly one self-addressed test draft
draft read-back                             PASS — exact subject + DRAFT label verified
exact-subject Sent search                   PASS — 0 results, confirming test draft not sent
draft delete/discard                        NOT AVAILABLE — no dedicated safe action exposed
send capability                             PASS — Gmail.send_email executed once to SELF after exact-subject dedup precheck
send verification                           PASS — exact subject, Sent state, 1 exact-subject Sent match; user confirmed receipt
paid API                                    NOT USED
```

Draft test subject: `[T14 TEST] Codex Mac Gmail capability validation`. The earlier draft requires manual cleanup if it is still present because no dedicated safe discard/delete-draft action was exposed.

Send test subject: `[T14 SEND TEST] Codex Mac Gmail capability validation`. Precheck found no exact-subject Sent message; Codex invoked `Gmail.send_email` exactly once to the authenticated self-address, then verified exact subject, Sent state, and exactly one matching Sent message. The user independently confirmed receiving the email.

Durable receipt:

```text
.chatgpt/test-receipts/T14_CODEX_MAC_GMAIL_2026-09-10.md
```

This establishes a useful alternative route for Gmail work from Codex Mac Chat. It does not close canonical T14, whose definition remains a Gmail Developer MCP usable in a developer-MCP/scheduler-compatible ChatGPT context.

## Proven execution path

```text
ChatGPT / Scheduled Task
  -> GitHub Developer MCP
  -> durable .chatgpt workspace/checkpoint
  -> scheduled read/write + idempotency
  -> scheduler-associated chat continuation
  -> fresh-chat recovery from GitHub
  -> exact Cloud TO_CODEX handoff
  -> real Codex bounded execution
  -> durable RETURN_FROM_CODEX
  -> ChatGPT independent GitHub verification

Codex Mac Chat
  -> built-in Gmail connector
  -> authenticated search/read
  -> Sent search
  -> draft create/read-back
  -> deduplicated self-send
  -> Sent verification + user receipt confirmation
```

## Remaining gaps

1. **T14 canonical:** connect/test a real Gmail Developer MCP in a compatible ChatGPT/Scheduled-Task context. Codex Mac standard Gmail is separately PASS for read/search/Sent/draft/send, including a real deduplicated self-send and independent user receipt confirmation.
2. **T13:** quota/cost behavior remains PARTIAL until matched tasks measure allowance-pool behavior over time.
3. **T10:** distinct persistent-VM Codex proof remains not formally tested; T23 proves the handoff path, not that architecture.
4. **T11/T12:** intentionally deferred until evidence justifies a persistent Codex Worker.
5. Repository creation from scratch through the tested GitHub Developer MCP remains blocked by the observed 403; work on an existing repo is independently validated.

No paid OpenAI API was used for these validations.