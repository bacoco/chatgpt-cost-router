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
GitHub Actions hosted runner allocation                     BLOCKED_EXTERNAL_CAPACITY — free Actions allowance exhausted during the observed test
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

A real Codex session consumed that exact handoff. Attempt 1 preserved a legitimate environment block because `python` was not present and both literal commands exited 127. After explicit authorization to use the available Python 3 interpreter, Codex reported `/usr/bin/python3`, Python 3.9.6, then ran:

```text
python3 -m unittest discover -s tests -v
-> 40 tests passed, exit 0, 1.462s

python3 scripts/build_schemas.py
-> exit 0, no output, no file changes
```

Codex then pushed the required return artifact:

```text
.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md
final return commit: 16bb9c9dc5d691334c57897d7145df1a16b83d00
```

T24 independently verified through `GitHub — bacoco TEST` that the branch history is:

```text
be8b29f191b877072e1def641aa3aeec51ec2ab8  original TO_CODEX handoff
de7d7cb6ee5aff2094c8572181d99739f24e3566  blocked attempt return
16bb9c9dc5d691334c57897d7145df1a16b83d00  passing Python 3 retry
```

Both post-handoff commits change only `.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md`. No application code or workflow file changed, and no PR exists for this handoff branch. T24 therefore accepts the Codex return only after verifying the live GitHub state rather than trusting the return text alone.

Durable receipts on `main`:

```text
.chatgpt/test-receipts/T20_CLOUD_TO_CODEX_HANDOFF_READY_2026-09-10.md
.chatgpt/test-receipts/T23_CODEX_EXECUTION_2026-09-10.md
.chatgpt/test-receipts/T24_CODEX_RETURN_VERIFICATION_2026-09-10.md
```

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
```

This core Cloud -> Codex -> Cloud round trip is now empirically validated.

## Remaining gaps

1. **T14:** connect and test a real Gmail Developer MCP in a compatible context.
2. **T13:** quota/cost behavior remains PARTIAL until matched tasks measure allowance-pool behavior over time.
3. **T10:** the distinct persistent-VM Codex proof remains not formally tested; T23 proves the handoff path, not that specific architecture.
4. **T11/T12:** intentionally deferred until evidence justifies a persistent Codex Worker.
5. Repository creation from scratch through the tested GitHub Developer MCP remains blocked by the observed 403; work on an existing repo is independently validated.

No paid OpenAI API was used for these validations.