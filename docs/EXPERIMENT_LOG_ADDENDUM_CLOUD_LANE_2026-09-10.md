# Experiment log addendum — cloud lane / scheduler chat / GitHub Actions

**Date:** 10 September 2026  
**Rule:** preserve the failed paths and distinguish observed behavior from assumptions.

## A01 — historical cloud-first technique recovered from repository history

Inspection of the 4 September repository history recovered the original intended strategy:

- Standard Chat as the default execution surface;
- Scheduled Chat as the automation engine;
- "push Chat until a real capability boundary is reached";
- targeted coding through a `Chat -> GitHub -> CI` lane;
- compact handoffs to avoid copying large conversations;
- re-evaluate/return to Chat when an expensive specialist capability is no longer required.

**Result:** PASS as historical design evidence. It was an architecture concept, not proof that the required connectors actually worked.

## A02 — custom GitHub Developer MCP supplied the missing proof

`GitHub — bacoco TEST` was connected to GitHub's hosted MCP endpoint and refreshed until 44 tools appeared.

Interactive Chat then proved authenticated read/write, issues, branches, commits, PRs and review operations.

**Result:** PASS.

## A03 — Scheduled Task -> GitHub Developer MCP

A Scheduled Task successfully authenticated as `bacoco`, read `bacoco/chatgpt-cost-router`, listed branches and returned exact `main` SHA.

**Result:** PASS.

## A04 — scheduled write idempotency

First scheduled/manual execution created exactly one marker issue #3. The repeated execution found the existing marker and returned `DEDUPLICATED`, creating no second issue. The marker was then closed.

**Result:** PASS.

## A05 — bounded Chat coding without Codex

Normal Chat identified the duplicate GitHub Actions trigger, locally reconstructed/verifed the project, created a one-line workflow patch, branch and PR #5.

Local evidence:

```text
39/39 unit tests PASS
schema generation: no diff
synthetic CLI replay: PASS
Codex: not used
paid OpenAI API key: not used
```

**Result:** PASS for bounded Chat + GitHub MCP + local verification.

## A06 — GitHub Actions Developer MCP

A second Developer MCP was created:

```text
GitHub Actions — bacoco TEST
https://api.githubcopilot.com/mcp/x/actions
OAuth
```

It exposed:

```text
actions_get
actions_list
actions_run_trigger
get_job_logs
```

ChatGPT successfully inspected workflow/run/job metadata and requested `rerun_failed_jobs` for run `34458242831`; GitHub returned `201 Created`.

**Result:** PASS for Actions control-plane access.

## A07 — failed assumption: Actions MCP means runnable CI

False.

Observed jobs repeatedly showed:

```text
runner_id: 0
runner_name: empty
Ubuntu billable execution: 0 ms
```

Logs for the never-executed job were unavailable/404 or only metadata URLs were available.

The same pattern existed on the repository's first `main` workflow run, before the later PRs.

The account owner then confirmed that the free GitHub Actions allowance had reached zero.

**Result:** FAIL for hosted runner availability; root cause = account Actions allowance exhausted.

**Lesson:** `Actions MCP callable` and `GitHub runner available` are different capabilities.

## A08 — workflow file vs account-level Actions state

After the owner reported removing/disabling Actions usage to stop the quota warning, GitHub's API still reported workflow `Contracts and routing` as `active`, and `.github/workflows/ci.yml` still existed in the repository.

**Result:** important state distinction.

Do not equate:

```text
account Actions capacity/setting
workflow API state
workflow file existence
runner allocation
```

## A09 — PR #5 disposition

Issue #6 was updated with the account-level runner diagnosis and closed. Because PR #5's one-line duplicate-trigger change had separate local verification and the hosted red state did not represent executed project tests, PR #5 was squash-merged.

Merge SHA:

```text
5e8d115f52446f507612a2f22f4926a09c4f1dc8
```

Documentation PR #2 was then updated onto the new `main`.

## A10 — scheduler-result chat continuation

The user reports a separate practical technique used previously: after a Scheduled Task produces a result, open the associated scheduler-result chat and continue substantial interactive work there.

This can merge naturally with the proven Developer MCP lane:

```text
scheduler bootstrap
-> GitHub checkpoint
-> open scheduler-result chat
-> interactive Chat work
-> GitHub MCP effects
-> local verification
-> persist next checkpoint
```

**Result:** USER-OBSERVED, NOT YET FORMALLY REPRODUCED ON A CLEAN PROFILE.

Do not infer hidden persistent storage, unlimited quota or guaranteed connector carry-over from this observation.

## A11 — merged cloud route

The preferred zero-marginal-API-cost route is now:

```text
Chat first
-> GitHub MCP
-> Scheduler only when automatic triggering is required
-> interactive continuation in scheduler-result chat when useful
-> Chat Python/shell for bounded verification
-> GitHub Actions only when runner capacity exists
-> Codex only after a real capability boundary
-> paid API only by explicit exception
```

This route is documented in `CLOUD_EXECUTION_LANE.md` and `BEGINNER_CLOUD_WORKFLOW.md`.

## Next tests

- T15: clean-profile scheduler-chat continuation with one harmless GitHub write.
- T16: fresh-chat recovery from a durable GitHub checkpoint.
- T17: capture detailed Scheduled Task -> GitHub Actions MCP result before claiming PASS.
- T18: explicit no-runner/Actions-budget gate before hosted CI is selected.
