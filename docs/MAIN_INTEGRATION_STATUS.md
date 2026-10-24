# Main integration status — 24 October 2026

## Current source validation

The exact integrated main `d2438d95e2a3ceca994d60b7ec25522e23be5f83`, after
PR #21 then PR #20, completed **255 tests: 254 passed, no failures/errors, one
skipped** (optional official MCP SDK absent), on Python 3.12.3. The worktree and
source stayed unchanged; recorded file hashes match that commit. The
[receipt](../audits/main-integration-20261024/validation.json) and
[reproduction guide](../audits/main-integration-20261024/README.md) record the
environment, artifacts and limits. Later documentation/evidence commits do not
certify another source revision. Deployment and live acceptance remain separate.

## Source of truth

PR #12 merged the complete A/B source into `main` at `e96562155afd2c91e6dd05b8903746cd85557b20`. Use `main`, not the older ZIPs or parallel implementation branches. PR #14 consolidates the independent remaining A/MCP corrections and executable operator guides on that baseline; its GitHub state and the current `main` ref are authoritative for merge completion.

The consolidation retains ten A regression scenarios from PR #11 while preserving main's named endpoint configuration and explicit read-only reconciliation after a deadline. It fixes strict resource binding checks for missing null-bound arguments and boolean/number substitutions, and handles MCP HTTP transport settings without relaxing loopback binding.

The README/install demo and A/B CLI examples now use the actual script and parser options. Documentation-parser tests check those commands. Deployment archives include the tracked documentation required by validation. Older parallel implementations are not merged wholesale over the current gateway and lifecycle code.

## Historical verified candidate — 11 September 2026

Candidate `ed26e5e846652ca3552026677584ab83b1367885` completed **227 tests: 226 passed, zero failures, zero errors, one skipped**, on Python 3.13.5. Ten complete code/test/contract/example/skill directory Git hashes matched the GitHub candidate. The source remained unchanged during the suite. Subsequent integration-status/evidence additions do not change those directories.

The skipped test requires the optional official MCP SDK, unavailable in the local validation environment. SDK-startup fixtures are not a live SDK acceptance test. This is a local result, not GitHub Actions CI and not fresh owner-fleet or connector acceptance. The compact [validation receipt](../audits/main-integration-20260911/validation.json) records hashes and the reproduction command; older test counts certify only their original snapshots.

## Historical PR #13 — excluded from integration

PR #13 remains draft and must not be merged as-is. Its `fleet_operator/jobs/service.py` contains a malformed completion-receipt assignment in `Jobs.reconcile`. A fresh SHA-guarded correction was blocked by the platform security check. No alternate tool or branch was used to perform the blocked write. The main implementation's correct completion-receipt handling is unchanged by PR #14.

The queued-project revocation correction was excluded from the September consolidation and has now been implemented independently against current main in PR #21 (issue #19), reviewed and merged at `759ad607939dace6fa46030c8a972e239dc6f042`. The correct receipt handling needed no new patch. The independent MCP startup fix was included separately. The [triage proposal for #18](https://github.com/bacoco/chatgpt-cost-router/issues/18#issuecomment-6384618206) recommends retiring #13 without merging its historical branch. No code was copied wholesale from it. PR #11's obsolete implementation is superseded by PR #12 plus the retained regression coverage; preserve its history rather than restoring the older conflicting snapshot.

## Deployment is separate

This push/merge consolidation does not install or reload a service, submit fleet work, change a scheduler, call another model or resume T38. Read [deployment status](DEPLOYMENT_STATUS.md) for the last observed installed revisions and unresolved host/Chat-attachment gates. Source integration does not certify that every machine is running that source.
