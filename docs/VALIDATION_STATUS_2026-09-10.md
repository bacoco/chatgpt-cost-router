# Validation status — 10 September 2026

This file is the **current status snapshot** for the 10 September ChatGPT Cost Router experiments.

The larger `CHATGPT-CLOUD-COST-ROUTER-ANALYSIS-2026-09-10.md` was started before all tests completed and should be read as the architectural/experimental analysis. For the latest pass/fail state, use this file together with `EXPERIMENT_LOG_2026-09-10.md`.

## Current validated state

```text
T01 — GitHub Developer MCP identity + repository read       PASS
T02 — files / issues / PR / branches read                  PASS
T03 — temporary issue create / read / close                PASS
T04 — branch + bounded documentation write + commit + PR   PASS
T05 — formal PR review workflow                            NOT YET TESTED
T06 — autonomous bug discovery → deduplicated issue        NOT YET TESTED
T07 — Scheduled Task → GitHub Developer MCP read-only      PASS
T08 — Scheduled write + second-run idempotency             NOT YET TESTED
T09 — direct ChatGPT code patch + Python/shell tests       NOT YET TESTED
T10+ — Codex worker path                                   NOT YET TESTED / NOT YET NEEDED
Gmail Developer MCP                                        NOT YET TESTED
```

## T07 exact evidence

The Scheduled Task used only `GitHub — bacoco TEST` and returned:

```text
Authenticated GitHub login: bacoco
Repository: bacoco/chatgpt-cost-router
Repository root read: PASS
Branches listed: PASS
main SHA: 6273cb87b98e94a1e04d9d439dfa400bbbb321cc
other branch: docs/chatgpt-cloud-cost-router-analysis-2026-09-10
other branch SHA: ab5f66a556eab82bb7d80fcff71341f2dbbe7d13
repository mutations: none
```

Therefore the critical statement now supported by evidence is:

> A ChatGPT Scheduled Task can invoke the custom GitHub Developer MCP and read authenticated GitHub repository state without Codex and without a paid OpenAI API key.

## Current GitHub documentation PR

The documentation work is on:

```text
branch: docs/chatgpt-cloud-cost-router-analysis-2026-09-10
PR: #2
```

The PR is intentionally **not merged automatically**. CI/check status must be treated independently from PR creation.

## Current CI state observed after documentation updates

The latest check runs were not green: `contracts` jobs showed failure/cancellation states. This must be investigated before merge. The project must not claim `MERGE_READY` merely because documentation changes and the PR itself were created successfully.

## Next critical tests

1. T08 — scheduled write with explicit deduplication, executed twice.
2. T09 — a bounded real code change by normal ChatGPT, with local Python/shell verification and a PR, without Codex.
3. Determine the current CI failure cause before merging PR #2.
4. Test a Gmail Developer MCP only if the standard Gmail connector remains forbidden in the required scheduler context.
