# Exact-main source validation — 24 October 2026

**SOURCE-TESTED:** `d2438d95e2a3ceca994d60b7ec25522e23be5f83`, the exact
`origin/main` after PR #21 (issue #19) and PR #20 (issue #16) merged, in that order.
The guarded merge commits are `759ad607939dace6fa46030c8a972e239dc6f042`
and `d2438d95e2a3ceca994d60b7ec25522e23be5f83` respectively.

The complete existing local suite ran **255 tests: 254 PASS, 1 SKIP, zero failures
or errors**, on Python 3.12.3. It includes schema/contract and documentation-parser
checks, synthetic connectors, temporary local processes and loopback transports.
The skipped test is the optional official MCP SDK discovery/health test; the SDK
is not installed. No dependencies were installed for this run. PyYAML 6.0.1 was
available instead of the development pin 6.0.2; all available tests passed with
that recorded environment. See the dependency inventory in the receipt.

The worktree was clean before and after validation; HEAD stayed at the exact SHA.
Every file hash recorded by the validator was compared with the Git blob at that
commit. The receipt records the repository tree and ten source/test/contract/skill
directory trees. All 37 relative links in the current guides resolved. No GitHub
Actions workflow exists at the tested revision.

## Evidence

- [Validation receipt](validation.json): tested commit, environment, counts,
  skip reason, unchanged-source checks, Git tree IDs and artifact SHA-256 hashes.
- [Full original validator report](full-validation.json): per-case results,
  source-file hashes and live gates explicitly not run.
- [Test log](unittest.log) and [guide-link inventory](doc-links.json).

The unchanged validator embeds the historical constant
`source_baseline=cd897ddf3856ffdabef68ba1a71b43dd99efad46`. It is retained in the
original report and identified explicitly in the receipt; it is **not** the
identity of this run. Use `tested_commit` and `verified_git_trees` in the receipt.

## Reproduce in an isolated copy

Choose fresh output/worktree paths, with the recorded interpreter and dependency
versions available; installing the optional SDK changes the skipped gate.

```bash
git worktree add --detach /tmp/cost-router-source-20261024 d2438d95e2a3ceca994d60b7ec25522e23be5f83
cd /tmp/cost-router-source-20261024
python3 scripts/validate_ab.py --output /tmp/ab-validation
git status --short
git rev-parse HEAD
```

The metadata collection additionally compared report hashes with `git show
<tested_commit>:<path>`, recorded directory trees with `git rev-parse
<tested_commit>:<directory>`, and used the current-guide relative-link algorithm
from `scripts/ab_validate_snapshot.py`. Reruns have their own timestamps/durations;
the retained hashes identify these original artifacts.

## Limits

This is local source validation. No real provider, connector account, remote fleet,
service installation, model API, deployment or new live acceptance was exercised.
The historical **DEPLOYED** and limited **LIVE-VERIFIED** runtime remains
`10b3ee3e438d57b210b1155e2dbaf19aac9b00db`, with its existing host-specific gates.
See [deployment status](../../docs/DEPLOYMENT_STATUS.md).

Documentation/evidence commits following this tested commit are not a new source
validation receipt. Historical counts certify their own exact revisions only.
