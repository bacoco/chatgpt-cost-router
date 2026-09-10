# Current project checkpoint

Task: T35 multi-node selection / next operational expansion after T34 supervision validation
Status: `SUPERVISED_MESH_VALIDATED` — T34 is PASS. The Mac Studio control plane and MacBook worker/node run as per-user LaunchAgents; forced `SIGKILL` of both MacBook services produced new PIDs automatically and the worker reappeared in the mesh with a fresh heartbeat, without a manual restart or model call.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Validated core

- T01-T30: PASS where recorded, except intentionally deferred/blocked experiments documented in the authoritative status.
- T28A/T28B: PASS for two distinct authorized OpenAI account workers isolated by `CODEX_HOME`.
- T30: PASS for live local broker alias dispatch.
- T31A: PASS for deterministic quota/budget-aware selection logic; provider quota ingestion itself remains unproven.
- T32: PASS for private remote dispatch from a second Tailscale device to `openai-B` on another Mac: `REMOTE_OK`, `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, paid-API environment removed.
- T33: PASS. The MacBook heartbeat-registered as a live remote node; the Mac Studio control plane discovered namespaced `macbook-pro-de-loic/openai-B`; `--worker auto` dispatched through the dynamically resolved node and returned `MESH_OK`, `gpt-6-astra`, 4,612 reported tokens, 5.888 s, exit 0, read-only/ephemeral, paid-API environment removed.
- T34: PASS. Per-user LaunchAgents supervise mesh-control, remote-worker and mesh-node. After a forced `SIGKILL`, remote-worker PID changed `38936 -> 39984` and mesh-node `39681 -> 39985`; both returned `running/loaded`, and the Mac Studio rediscovered `macbook-pro-de-loic/openai-B` as `ready=true` with a fresh heartbeat. No model call was used for this recovery proof.

## Cost / quota boundary

T13 remains `PARTIAL_STOPPED`. Per-call Codex token counts are telemetry, not provider 5-hour/weekly quota. T31/T33 can rank trusted allowance observations but keep unknown values unknown.

## Remaining gaps

- Automatic/reliable ingestion of live per-account 5-hour and weekly allowance.
- Separately shared external-user Tailscale identity/ACL smoke when such a user is available.
- Useful concurrency when a real workload benefits from it.
- Claude/other-provider adapters and provider-neutral handoff.
- Canonical Gmail Developer MCP only if still required.

## Next useful action

The mesh is now supervised and self-recovers from process crashes. The next useful proof is a **second simultaneously live worker-bearing node** so `--worker auto` must choose among at least two machines using the T31/T33 ranking rules. A full logout/login or machine reboot recovery test is a separate lifecycle check and should not be claimed from T34.

T32 receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.
T33 specification: `docs/T33_MESH_NODE_REGISTRATION.md`.
T33 receipt: `.chatgpt/test-receipts/T33_MESH_LIVE_2026-09-10.md`.
T34 specification: `docs/T34_MACOS_SERVICE_SUPERVISION.md`.
T34 receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
