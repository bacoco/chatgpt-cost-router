# Validation status — 10 September 2026

This file is the **current status snapshot** for the 10 September ChatGPT Cost Router experiments.

The larger `CHATGPT-CLOUD-COST-ROUTER-ANALYSIS-2026-09-10.md` was started before all tests completed and should be read as the architectural/experimental analysis. For the latest pass/fail state, use this file together with `EXPERIMENT_LOG_2026-09-10.md`.

## Current validated state

```text
T01 — GitHub Developer MCP identity + repository read       PASS
T02 — files / issues / PR / branches read                  PASS
T03 — temporary issue create / read / close                PASS
T04 — branch + bounded documentation write + commit + PR   PASS
T05 — formal PR review workflow                            PASS
T06 — autonomous defect discovery → deduplicated issue      PASS
T07 — Scheduled Task → GitHub Developer MCP read-only      PASS
T08 — Scheduled write + second-run idempotency             PASS
T09 — direct ChatGPT bounded patch + Python/shell tests    PASS
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

## T08 exact evidence

```text
run 1: exact marker absent → issue #3 CREATED
run 2: exact marker present → DEDUPLICATED #3
duplicate artifacts: 0
marker cleanup: issue #3 closed
Codex: not used
paid OpenAI API key: not used
```

## T05/T06/T09 exact evidence

T05 submitted a real COMMENT review on PR #2 after reading its actual changed-file set. The review recorded that the PR contained four documentation files only and that independently reconstructed local tests passed.

T06 found a concrete cost/reliability defect in `.github/workflows/ci.yml`: both unrestricted `push` and `pull_request` were enabled. A deduplication search found no existing matching issue, then issue #4 was created.

T09 fixed that issue on branch `fix/avoid-duplicate-ci-runs` with one line of workflow configuration, commit `312f8ce93f37381bc8928047b15944cb28921de6`, PR #5.

Local verification before push:

```text
workflow trigger structure                         PASS
python -m unittest discover -s tests -v            PASS (39/39)
python scripts/build_schemas.py                     PASS / no schema drift
documented synthetic CLI replay                    PASS
Codex                                               NOT USED
paid OpenAI API key                                 NOT USED
```

## Current CI diagnosis

PR #2 showed 4 checks because the workflow ran twice (push + pull_request). PR #5, after restricting `push` to `main`, showed exactly 2 matrix checks. Therefore the duplicate-execution defect is verified fixed.

However PR #5 still showed `contracts (3.11)` failure and `contracts (3.12)` cancellation within roughly two seconds. Since the complete reconstructed test suite passes locally and schema generation is clean, the remaining CI failure is not demonstrated to be a code/test regression. Its exact GitHub Actions-level cause is still unknown because the currently exposed GitHub MCP toolset provides check-run status but not job log contents. Do not mark either PR MERGE_READY yet.

## Next critical tests / work

1. Obtain GitHub Actions job-log visibility and determine the exact early CI failure cause.
2. Once CI is understood/green, merge the isolated CI fix first, then rebase/update documentation PR #2 and re-check it.
3. Test a Gmail Developer MCP only if the standard Gmail connector remains forbidden in the required scheduler context.
4. Only after the no-Codex route is exhausted, evaluate whether a Codex worker is actually needed.
