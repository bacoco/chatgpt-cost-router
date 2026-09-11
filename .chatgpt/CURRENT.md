# Current project checkpoint

Repository: `bacoco/chatgpt-cost-router`.
Delivery branch: `fix/ab-delivery-reconciled-20260911`.
Status: `LOCAL_SUITE_VERIFIED_REVIEW_PENDING`.
Code revision: `1c239d502bcbae0c1bc988e9fd3c70c0b436520e`.

A completes authorized native Chat connector work; B independently supervises
ordinary machine processes. A is not limited to issues, and B does not require
a second model. The implementation supersedes the earlier documentation-only
pause checkpoint; it does not authorize deployment or broad remote writes.

## Evidence from this continuation

The local published-runtime suite passed 168 tests, with no failures, errors or
skips. The 77-file read-back manifest matches the tested bytes. Real local process,
standalone CLI artifact retrieval, simulated multi-connector workflows and real
loopback JSON/SSE fixtures are covered. Official MCP SDK compatibility and actual
owner-host deployment are not established by these tests.

Read `docs/AB_DELIVERY_RECONCILED_2026-09-11.md` and
`.chatgpt/test-receipts/AB_RECONCILED_2026-09-11.json` before continuing.

## Concurrency rule for continuation

The former shared feature branch had another writer during delivery. This branch
forked at `e3fc9d1fe6901637834a3f1be78ac058a646b34d` and reconciles overlapping
B changes while retaining that snapshot's shared/A/worker changes. Do not blindly
copy older files back or assume later shared-branch commits are included. Work
from an immutable revision and compare any later changes explicitly.

## Remaining qualification gates

Install/test the optional official MCP SDK and actual private app attachment;
validate an authorized real connector workflow and an enrolled non-LLM owner-node
task; qualify supported OS/container cleanup, enrollment and release activation.
Do not infer these PASS states from local tests. `trusted-local` is not a hostile
workload sandbox. Historical receipts are retained unchanged. No services,
schedulers, owner-machine installations or quota-burn experiments were restarted.
