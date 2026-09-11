# Main integration and target-host rollout — 11 September 2026

This update follows the owner's explicit instruction to integrate and perform a bounded rollout, not another documentation-only pause. Existing services and schedulers must not be replaced.

## Executed in this continuation

- A fresh GitHub-relay `status` request reached `macbook` and returned `PASS`, exit 0. Receipt: `.fleet/results/job-ab-readiness-20260911-1629.json` on its matching result branch. This proves host access, not the new job/MCP runtime.
- Read the parallel rollout receipts: the A service failed with `Settings` lacking `host`; a Mac Studio non-LLM job was `UNCERTAIN/PermissionError`. These are not counted as successful deployments.
- Reproduced the revoked-queued-project defect reported in PR #13 and the MCP v2 Settings startup defect, then corrected both. Queue failures remain principal-scoped and cannot change a concurrently started task. SDK HTTP binding remains loopback only.
- Reconstructed the reviewed runtime from the existing baseline archive, verified its 77-file receipt manifest, and verified six compatibility alias files against GitHub blobs. Applied only the queue/startup corrections and their regression tests.
- `python -m unittest discover -s tests -v`: 173 tests, 0 failures, 0 errors, 0 skipped; Linux, Python 3.13.5; 30.338 seconds. The SDK compatibility regression uses a strict Settings fixture, not an installed SDK/server certificate. The queue regression really runs a local non-LLM process after rejecting a revoked project.

## Reconciliation and limits

PR #13 is the reviewed runtime snapshot. Later changes on PR #12 remain preserved on `feat/ab-products-20260911`; they are not silently overwritten or certified by this suite. The merge decision concerns this qualified baseline plus the small fixes above, not every later parallel addition.

The official MCP v2 migration guide moves HTTP options from Settings to `run()`: https://py.sdk.modelcontextprotocol.io/migration/#transport-specific-parameters-moved-from-mcpserver-constructor-to-runapp-methods . The compatibility adapter checks actual transport fields rather than `hasattr(server, 'settings')`.

A remote source-export request through an interpreter was blocked by the tool's security check and was not retried by another route. Existing local archive bytes were used instead. A fresh complete installed-SDK/owner-process/file-retrieval acceptance is still required before claiming rollout success. No extra model call, quota experiment, scheduler change or replacement of existing services is authorized by this report.
