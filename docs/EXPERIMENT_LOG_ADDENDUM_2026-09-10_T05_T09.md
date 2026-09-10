# Experiment log addendum — T05 to T09 — 10 September 2026

This file appends evidence gathered after the first `EXPERIMENT_LOG_2026-09-10.md` snapshot. It deliberately records both successes and failures. Do not rewrite earlier failures away.

## Current result summary

```text
T05 — real PR review                                      PASS
T06 — evidence-backed defect discovery → issue           PASS
T07 — Scheduled Task → GitHub Developer MCP read         PASS (previously recorded)
T08 — Scheduled Task write + second-run deduplication    PASS
T09 — bounded ChatGPT change + local verification + PR   PASS
Codex                                                     NOT USED
Paid OpenAI API key                                       NOT USED
```

## T05 — real PR review — PASS

PR `#2` was read through `GitHub — bacoco TEST`, including its current file set and diff. A COMMENT review was submitted against head commit `d855315b80e6e84cd66b7e91e927362ff4c2404d`.

Observed PR #2 scope at review time:

```text
changed files: 4
all changed files: docs/*
production Python changed: no
policy changed: no
schemas changed: no
workflow changed: no
tests changed: no
```

Independent local reconstruction from files fetched through the GitHub Developer MCP produced:

```text
python -m unittest discover -s tests -v    39/39 PASS
python scripts/build_schemas.py            PASS; no schema drift
documented synthetic CLI replay            PASS
```

The review explicitly did **not** equate those local results with GitHub Actions success. PR #2 remained not merge-ready because its hosted checks were red/cancelled.

## T06 — defect discovery → issue — PASS

A concrete CI cost/reliability defect was identified in `.github/workflows/ci.yml`:

```yaml
on:
  push:
  pull_request:
```

For a push to a branch with an open PR this launches both a `push` workflow and a `pull_request` workflow. PR #2 empirically showed two matrix workflow executions, yielding four check runs for the same update.

Before creating an issue, GitHub issues were searched for an equivalent report. No match was found.

Created issue:

```text
#4 — CI: avoid duplicate workflow runs for pull-request branch pushes
```

This is an evidence-backed defect, not a hypothetical optimization.

## T08 — scheduled write idempotency — PASS

Exact marker title:

```text
[MCP T08] Scheduler idempotency marker 2026-09-10
```

Run 1:

```text
search exact marker → absent
create exactly one issue → #3
read back → PASS
result → CREATED
```

Run 2, with the same scheduled-write logic:

```text
search exact marker → issue #3 found
new issue created → no
other repository mutation → no
result → DEDUPLICATED
```

After the test, marker issue #3 was closed as completed.

This proves the tested Scheduled Task can perform a controlled GitHub write through the Developer MCP and can avoid a duplicate on an identical second run when existence checking is part of the instruction.

It does **not** prove every future scheduler prompt is automatically idempotent. Idempotency remains a workflow property that must be designed and verified.

## T09 — bounded ChatGPT patch + local verification + PR — PASS

The issue from T06 was fixed without Codex.

Branch:

```text
fix/avoid-duplicate-ci-runs
```

Base:

```text
main @ 6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

Change:

```diff
 on:
   push:
+    branches: [main]
   pull_request:
```

Only `.github/workflows/ci.yml` changed.

Commit:

```text
312f8ce93f37381bc8928047b15944cb28921de6
```

Pull request:

```text
#5 — ci: avoid duplicate runs on pull-request branch pushes
```

Local verification before GitHub write:

```text
workflow trigger structure                         PASS
python -m unittest discover -s tests -v            PASS (39/39)
python scripts/build_schemas.py                     PASS / no schema drift
documented synthetic CLI replay                    PASS
```

Execution environment used for the reconstructed suite:

```text
Python 3.13.5
PyYAML 6.0.3
jsonschema 4.26.0
```

The repository requirements themselves currently pin PyYAML 6.0.2 and jsonschema 4.25.1; therefore this local run proves behavioral compatibility with the available ChatGPT environment, not byte-for-byte equivalence with GitHub Actions' dependency environment.

## Post-fix hosted-CI observation

PR #2 previously exposed four check runs for a documentation update because both event paths fired.

PR #5, after the trigger fix, exposed exactly two matrix checks:

```text
contracts (3.11)  completed / failure
contracts (3.12)  completed / cancelled
```

Both started at `2026-09-10T09:00:27Z` and ended at `2026-09-10T09:00:29Z`.

Therefore:

```text
duplicate workflow execution defect   FIX VERIFIED
hosted CI overall                      STILL NOT GREEN
exact Actions-level failure cause      UNKNOWN
```

The extremely short hosted run plus the successful reconstructed test suite suggests the remaining failure occurs very early, but **the exact failing step has not been observed and must not be guessed**.

The currently exposed default GitHub Developer MCP toolset can read check-run status but does not expose GitHub Actions job-log contents. A separate Actions-capable toolset or a human read of the job log is required for exact diagnosis.

## Secret-scanning attempt — FAIL / capability unavailable

A GitHub MCP `run_secret_scanning` call was attempted on the PR #5 diff.

Actual result:

```text
Repository does not have GitHub Advanced Security enabled.
```

Therefore the correct state is:

```text
GitHub secret scanner executed successfully   NO
secret-scanning capability available          NO (for this repo/configuration)
scanner found no secrets                      NOT CLAIMED
```

The diff is a one-line branch filter and contains no credential-looking material by direct inspection, but that is not equivalent to a successful GitHub secret-scanning result.

## New failure/recovery lessons

1. A full local PASS does not establish GitHub Actions PASS.
2. A red PR can contain more than one independent problem: PR #2 had duplicate workflow execution and an underlying early Actions failure.
3. Fixing duplicate triggers reduced four checks to two, which is direct behavioral evidence that the trigger fix worked even though the remaining checks are not green.
4. `run_secret_scanning` being exposed as an MCP tool does not prove the repository has the GitHub Advanced Security entitlement/configuration required to execute it.
5. Do not merge merely because the PR is `mergeable_state=clean`; CI_PASS and MERGE_READY remain separate gates.

## Next gate

Before merging PR #5 or PR #2, obtain the actual GitHub Actions job failure detail. Once the underlying Actions problem is understood or fixed:

1. re-run PR #5 checks;
2. merge PR #5 only if the merge gate is satisfied;
3. update/rebase PR #2 onto the corrected `main`;
4. re-run its checks;
5. then merge documentation if green/reviewed.
