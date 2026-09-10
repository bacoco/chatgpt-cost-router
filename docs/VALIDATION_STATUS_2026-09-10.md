# Validation status — 10 September 2026

This file is the **current status snapshot** for the 10 September ChatGPT Cost Router experiments.

Use it together with `EXPERIMENT_LOG_2026-09-10.md`, `EXPERIMENT_LOG_ADDENDUM_2026-09-10_T05_T09.md` and `CLOUD_EXECUTION_LANE.md`. The large analysis document is a historical working record and contains earlier pending states that were later resolved.

## Current validated state

```text
T01 — GitHub Developer MCP identity + repository read       PASS
T02 — files / issues / PR / branches read                  PASS
T03 — temporary issue create / read / close                PASS
T04 — branch + bounded documentation write + commit + PR   PASS
T05 — formal PR review workflow                            PASS
T06 — autonomous defect discovery → deduplicated issue     PASS
T07 — Scheduled Task → GitHub Developer MCP read-only      PASS
T08 — Scheduled write + second-run idempotency             PASS
T09 — direct ChatGPT bounded patch + Python/shell tests    PASS
GitHub Actions Developer MCP interactive control            PASS
GitHub Actions hosted runner allocation                     BLOCKED — account free Actions allowance exhausted
T15 — scheduler-chat manual continuation clean-profile      NOT YET FORMALLY TESTED
T16 — fresh-chat recovery from GitHub checkpoint            NOT YET TESTED
T17 — Scheduled Task → Actions MCP detailed result          PENDING CAPTURE
Codex worker path                                            NOT YET TESTED / NOT YET NEEDED
Gmail Developer MCP                                         NOT YET TESTED
```

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
  -> idempotent second run
```

No Codex and no paid OpenAI API key were needed for T01–T09.

## GitHub Actions MCP result

A second Developer MCP was created with:

```text
https://api.githubcopilot.com/mcp/x/actions
```

It exposed `actions_get`, `actions_list`, `actions_run_trigger` and `get_job_logs`. ChatGPT successfully inspected workflow/run/job metadata and requested a failed-job rerun.

This proves **control-plane access**, not runner availability.

## GitHub runner/quota diagnosis

The repository workflow is still reported as `active` by GitHub and `.github/workflows/ci.yml` still exists.

However the account owner confirmed the free GitHub Actions allowance had reached zero. The observed jobs had:

```text
runner_id: 0
runner_name: empty
Ubuntu billable duration: 0 ms
usable executed-step logs: absent/unavailable
```

The same pattern existed on the repository's first workflow run on `main`, before PR #2 and PR #5. Therefore those red hosted checks were not evidence that either PR broke the Python suite.

Diagnostic issue #6 was updated with this account-level cause and closed. PR #5 was then merged after separate local verification; merge SHA:

```text
5e8d115f52446f507612a2f22f4926a09c4f1dc8
```

## T08 exact evidence

```text
run 1: exact marker absent → issue #3 CREATED
run 2: exact marker present → DEDUPLICATED #3
duplicate artifacts: 0
marker cleanup: issue #3 closed
Codex: not used
paid OpenAI API key: not used
```

## T09 exact evidence

The duplicate `push` + `pull_request` trigger was corrected on a separate branch/PR.

Local verification before push:

```text
workflow trigger structure                         PASS
python -m unittest discover -s tests -v            PASS (39/39)
python scripts/build_schemas.py                     PASS / no schema drift
documented synthetic CLI replay                    PASS
Codex                                               NOT USED
paid OpenAI API key                                 NOT USED
```

The local environment was not byte-identical to GitHub Actions, and package installation into a fresh environment could not be reproduced because the ChatGPT container lacked usable outbound DNS for pip. That limitation remains explicit.

## Scheduler-chat continuation technique

The user reports an additional useful cloud workflow: open the chat associated with a completed Scheduled Task and continue doing substantial interactive work there.

This is incorporated into `CLOUD_EXECUTION_LANE.md` as the **scheduler bootstrap + interactive continuation** route. It is not yet marked formally PASS because a clean-profile test has not recorded exactly which context and Developer MCP capabilities carry into the manual follow-up.

The design rule is already clear: durable state belongs in GitHub/checkpoints, not only in the scheduler chat.

## Next cloud tests

1. T15 — clean-profile scheduler-chat continuation with one harmless GitHub action.
2. T16 — prove a fresh Chat can recover solely from a compact GitHub checkpoint.
3. Capture the Scheduled Task → GitHub Actions MCP result before marking T17 PASS.
4. Add an explicit Actions-runner/quota capability gate so the router never selects hosted CI when no runner can be allocated.
5. Only after the cloud lane is characterized, build and compare the Codex desktop/CLI lane on macOS.
