# A/B reconciled delivery — 11 September 2026

**Code delivered for review; local suite PASS; production deployment not performed.**

Repository: `bacoco/chatgpt-cost-router`.
Branch: `fix/ab-delivery-reconciled-20260911`.
Immutable code revision: `1c239d502bcbae0c1bc988e9fd3c70c0b436520e`.
Documentation/evidence commits may follow without changing that code revision.

## What is delivered

A retains complete native Chat operations across authorized connectors, scoped
resources/accounts/sessions, explicit write approvals, read-back checks and
read-only recovery after uncertain writes. The shared journal fences competing
invocations. B supplies independent ordinary-process execution and supervision,
bounded logs, progress, deadlines, cancellation and receipt-verified file delivery.

This reconciliation combines the artifact receipt/path/integrity checks with the
concurrent supervisor claim, resource metrics, owned-container cleanup, runtime
identity envelope, bounded gateway transport and durable relay outbox. It retains
the physical worker moves and compatibility aliases from the pinned parent.

Artifact output supports both `data_base64` and `data`, plus `chunk_sha256`.
The 64 KiB chunk limit is enforced consistently. Artifact bytes are not a GitHub
relay operation; retrieval uses the private node, CLI or MCP transport.
Raw gateway write/Git-pull behavior is intentionally restricted: general changes
must use operator-owned process profiles. This is a migration consideration,
not a transparent replacement for historical broad write commands.

## Executed validation

Command: `python -m unittest discover -s tests -v`.
Environment: Linux, Python 3.13.5, local execution container.
Final run: **168 tests; 0 failures; 0 errors; 0 skipped; 30.576 seconds**.

The final run took place after comparing 77 local files with GitHub Git-blob
hashes. That manifest includes all test-directory files, all A modules, the B job
runtime and gateway/relay modules, shared changes and moved worker implementations.
All 77 matched. The manifest is a declared scope, not a full repository tree hash.
The checkout was reconstructed from the verified baseline archive and exact
GitHub revisions; it was not a network clone.

| Check | Evidence scope |
| --- | --- |
| A drives B and retrieves `42` | Real local child, local A-to-B adapter, actual verified artifact bytes |
| Independent B CLI | Real subprocess submission, polling and retrieval of `CLI_OK` |
| Multiple connector workflow | Simulated Gmail/GitHub/Cowboy actions with approvals and verification |
| HTTP JSON/SSE transport | Real loopback HTTP fixtures, including discovery, correlation and error cases |
| No duplicate effects | Failure injection, lost replies, single-use dispatch and relay retry tests |
| Isolation and integrity checks | Foreign projects/sessions, altered receipts/files and unsafe paths rejected |
| Compatibility | Existing deterministic tests and retained worker import aliases |

The machine-readable receipt includes the exact test-log hash, a losslessly
compressed copy of the log, and the per-file read-back manifest:
[AB_RECONCILED_2026-09-11.json](../.chatgpt/test-receipts/AB_RECONCILED_2026-09-11.json).

Decode the log with Python's standard `base64` and `gzip` modules and compare its
SHA-256 with `test_log_sha256`. No credentials or owner-machine state are required.

## Concurrent-change incident and resolution

The initial `cd897dd` reconstruction passed 124 tests; the first continuation
copy passed 142. Those counts did **not** certify the moving shared branch.
Another writer added contracts, A recovery, B lifecycle/gateway/outbox, packaging
and worker moves while this continuation was pushing. Some overlapping B files
were temporarily overwritten by our full-file writes.

The collision was detected through read-back hashes. The shared branch was no
longer used for writes. An isolated branch was created at
`e3fc9d1fe6901637834a3f1be78ac058a646b34d`; overlapping safeguards were explicitly
reconciled and the combined runtime suite rerun. Commits `9c8d0c1` and `1c239d5`
persist that reconciliation. Later changes on the other branch are outside this
fixed snapshot and require a separate comparison before integration.

## Not validated, deployed or implied

The optional official MCP SDK was not installed in this execution environment.
An offline installation attempt found no locally available distribution. This
says nothing about remote package availability. Mock registration and HTTP
fixtures are not official-SDK/server or actual Chat attachment validation.

No new owner-host SSH/process task, installed container-engine test, actual
Gmail/Cowboy cross-connector workflow, enrollment, immutable release activation,
package installation, service restart or scheduler change was executed here.
Those deployment/acceptance gates remain open; their code is not claimed certified.
No extra coding-agent/model API calls were used by this continuation.

`trusted-local` is not a sandbox for hostile code. Private configured principals
and caller-observed native evidence are not a public multi-tenant authentication
or independent provider attestation system. CPU/RSS observations are direct-process
measurements where available, not aggregate GPU/container metrics.

Historical receipts remain unchanged. Review and integration are separate from
production rollout. Do not resume T38, install optional components or restart the
stopped quota experiment based only on this report.
