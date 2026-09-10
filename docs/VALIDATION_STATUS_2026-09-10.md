# Validation status — 10 September 2026

This file is the **authoritative current status snapshot** for the 10 September ChatGPT Cost Router experiments. Historical analysis/log files intentionally preserve earlier pending states and failures; when they conflict with this snapshot, use this file plus durable receipts and current GitHub state.

## Status vocabulary

- `PASS`: the requested behavior was actually executed and verified with observable evidence.
- `PARTIAL`: a meaningful bounded part was verified, but the complete test definition was not.
- `BLOCKED_EXTERNAL_CAPACITY`: the test is ready or defined but cannot execute because an external capacity is unavailable.
- `BLOCKED_MISSING_CONNECTOR`: the required connector is not available in the tested context.
- `BLOCKED_USER_INTERACTION`: the remaining proof requires a user action that cannot be simulated by the running task.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built/executed because the preceding evidence does not justify the additional surface yet.

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

T10 — Codex CLI persistent-VM proof of concept              BLOCKED_EXTERNAL_CAPACITY — current Codex token allowance exhausted
T11 — Codex Worker MCP                                      DEFERRED_NOT_JUSTIFIED — worker build remains optional and requires a demonstrated need
T12 — Scheduler -> Codex Worker                             DEFERRED_NOT_JUSTIFIED — depends on T11
T13 — cost/quota experiment                                 PARTIAL — zero-paid-API cloud routes recorded; Codex quota interaction cannot be measured while Codex is unavailable
T14 — Gmail Developer MCP                                   BLOCKED_MISSING_CONNECTOR — no Gmail Developer MCP is available in this developer-MCP-restricted conversation; standard Gmail was not used as a substitute

T15 — scheduler-chat manual continuation clean-profile      BLOCKED_USER_INTERACTION — scheduler side ran; PASS still requires a manual reply in that Scheduled Task's associated chat
T16 — fresh-chat recovery from GitHub checkpoint            NOT YET FORMALLY TESTED — current chat is not a clean fresh-chat test
T16A — independent-context recovery from checkpoint         PASS — durable receipt on main
T17 — Scheduled Task -> Actions MCP detailed read           PASS — durable receipt on main
T18 — explicit Actions runner/capability gate               PASS — PR #10 merged; router rejects unavailable hosted route and selects verified local fallback
T19 — per-repo scheduler workspace launcher                 PASS — durable receipt on main
T20 — ChatGPT Cloud -> Codex -> ChatGPT full round trip     BLOCKED_EXTERNAL_CAPACITY
       Cloud -> persisted TO_CODEX handoff                  PASS — exact handoff commit recorded/read back
       Codex execution / return verification                BLOCKED_EXTERNAL_CAPACITY — current Codex token allowance exhausted
T21 — workflow skill files/frontmatter                      PASS — repository format checked
T22 — project-workspace-bootstrap end-to-end dogfood        PASS — PR #9 merged; seven installed paths re-verified; durable receipt on main
T23 — cloud-to-codex-handoff executed with real Codex       BLOCKED_EXTERNAL_CAPACITY — handoff ready, Codex unavailable
T24 — codex-to-cloud-return verified back in ChatGPT        BLOCKED_EXTERNAL_CAPACITY — depends on T23 real return

GitHub Actions Developer MCP interactive/read control        PASS
GitHub Actions hosted runner allocation                     BLOCKED_EXTERNAL_CAPACITY — account free Actions allowance exhausted
Repository creation through Developer MCP                   BLOCKED — real create_repository attempts returned 403 Resource not accessible by integration
Paid OpenAI API                                             NOT USED
```

## Exact current evidence added after the earlier snapshot

### T16A — independent-context recovery

Receipt:

```text
.chatgpt/test-receipts/T16A_INDEPENDENT_CONTEXT_RECOVERY_2026-09-10.md
```

Observed result: `PASS`. The independent Scheduled Task reconstructed repository identity, source-kit SHA, bootstrap branch and key workspace/skill paths from GitHub/checkpoint state without Codex or paid API use. Receipt commit on `main`: `5cdd3e19e8c8a78f2593fc97fa42d833b47f0793`.

### T17 — Scheduled Task -> GitHub Actions Developer MCP

Receipt:

```text
.chatgpt/test-receipts/T17_ACTIONS_MCP_2026-09-10.md
```

Observed result: `PASS` for read-only Actions control-plane access. The task read workflow `Contracts and routing`, latest completed run `34467121828`, event `push`, conclusion `failure`, and observed `0 ms` Ubuntu billable duration. It did not trigger/rerun/cancel anything. Receipt commit: `ae9b8d5e1cc50105df359ff32fe6b98cee3d1d5a`.

### T18 — runner/capability gate

PR #10 (`test: gate unavailable hosted Actions runner`) is merged. It adds a regression proving that a route whose scoped hosted-Actions capability is `unavailable` is rejected with a verified local fallback selected. The PR records a reconstructed local suite result of `40/40 PASS`. Merge commit: `d7fd61b512f366d3c4497dffe82cfc8362b68f78`.

This validates routing/gating logic **once runner-availability evidence exists**. It does not claim the current GitHub MCP can preflight remaining account Actions minutes before a run.

### T19 — repository scheduler workspace

Receipt:

```text
.chatgpt/test-receipts/T19_SCHEDULER_WORKSPACE_2026-09-10.md
```

Observed result: `PASS`. The Scheduled Task freshly resolved `main`, read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md` and `.chatgpt/SCHEDULER.md`, verified references, then wrote/read its single receipt with `Codex_used=no`, `paid_API_used=no`, and `GitHub_Actions_used=no`. Receipt commit: `2cd6a73d055acc949f434b4c33003f51ec41a480`.

### T20 — Cloud handoff boundary

The cloud half is now actually executed, not merely designed.

```text
branch: test/t20-cloud-to-codex-handoff-20260910
handoff: .chatgpt/handoffs/T20/TO_CODEX.md
handoff commit: be8b29f191b877072e1def641aa3aeec51ec2ab8
main receipt: .chatgpt/test-receipts/T20_CLOUD_TO_CODEX_HANDOFF_READY_2026-09-10.md
receipt commit: 28bb1abd13cb4c52c39662dc6dca5e268c12dab7
```

The handoff preserves exact repository/branch/SHA, completed work, remaining work, required local tests, constraints, authorization and expected return artifact. It was read back at the exact handoff commit. No Codex execution is inferred. Full T20 remains blocked until a real Codex session creates a verifiable `RETURN_FROM_CODEX.md` and ChatGPT checks it.

### T22 — self-bootstrap dogfood

PR #9 (`test: dogfood project workspace bootstrap`) is merged and changed exactly seven bounded workspace/skill files. Merge commit: `5a6652630629abe644afd19de44399bc36b4e567`.

Current `main` was re-read and contains:

```text
.chatgpt/PROJECT.md
.chatgpt/CURRENT.md
.chatgpt/SCHEDULER.md
.chatgpt/HANDOFF_POLICY.md
.chatgpt/handoffs/README.md
.agents/skills/cloud-to-codex-handoff/SKILL.md
.agents/skills/codex-to-cloud-return/SKILL.md
```

Receipt:

```text
.chatgpt/test-receipts/T22_PROJECT_WORKSPACE_BOOTSTRAP_2026-09-10.md
```

Receipt commit: `39a337a61eeb0ddbd9b71b89f0eb80b7aff7b554`. T19 subsequently proved that the installed workspace is consumable by a real Scheduled Task.

## Proven cloud path

```text
ChatGPT Chat
  -> GitHub Developer MCP
  -> authenticated repo read/write
  -> bounded branch/commit/PR
  -> local Python/shell verification when feasible

Scheduled Task
  -> GitHub Developer MCP
  -> authenticated read
  -> controlled write
  -> idempotent duplicate prevention
  -> repo-backed .chatgpt workspace recovery

ChatGPT Cloud
  -> exact GitHub checkpoint
  -> persisted TO_CODEX.md at exact SHA
  -> STOP while Codex unavailable
```

The key architectural rule remains: GitHub is durable state; chat and scheduler-local context are not the source of truth. Codex is an escalation target, not a prerequisite for ordinary repository work.

## Remaining blockers / next evidence

1. **T15:** user must open the T15 Scheduled Task's associated chat and perform the requested manual continuation there. Scheduler execution alone is insufficient evidence.
2. **T16:** requires a genuinely fresh Chat test; T16A already proves the stronger scheduler/independent-context checkpoint recovery path but is kept distinct for test fidelity.
3. **T23/T24 and full T20:** wait for real Codex capacity, then use the already-persisted T20 handoff. Do not rebuild or broaden it unless GitHub state invalidates it.
4. **T10/T13 Codex quota aspects:** wait for Codex capacity; do not infer quota-pool behavior.
5. **T14:** requires an actual Gmail Developer MCP connection in a developer-MCP-compatible context. A blocked standard Gmail connector is not equivalent evidence.
6. **T11/T12:** remain intentionally deferred unless evidence demonstrates that a persistent Codex Worker is worth building.

No paid OpenAI API was used to obtain the validations recorded here.
