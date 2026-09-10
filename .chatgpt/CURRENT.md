# Current project checkpoint

Task: T34 operational mesh after T33 live automatic cross-node routing
Status: `MESH_LIVE_VALIDATED` — T33 is PASS. A MacBook worker node heartbeat-registered into a Mac Studio control plane; the control plane discovered `macbook-pro-de-loic/openai-B` and `--worker auto` dynamically dispatched through the mesh to that remote worker with a verified result.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Validated core

- T01-T30: PASS where recorded, except intentionally deferred/blocked experiments documented in the authoritative status.
- T28A/T28B: PASS for two distinct authorized OpenAI account workers isolated by `CODEX_HOME`.
- T30: PASS for live local broker alias dispatch.
- T31A: PASS for deterministic quota/budget-aware selection logic; provider quota ingestion itself remains unproven.
- T32: PASS for private remote dispatch from a second Tailscale device to `openai-B` on another Mac: `REMOTE_OK`, `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, paid-API environment removed.
- T33: PASS. The MacBook heartbeat-registered as a live remote node; the Mac Studio control plane discovered namespaced `macbook-pro-de-loic/openai-B`; `--worker auto` dispatched through the dynamically resolved node and returned `MESH_OK`, `gpt-6-astra`, 4,612 reported tokens, 5.888 s, exit 0, read-only/ephemeral, paid-API environment removed.

## Cost / quota boundary

T13 remains `PARTIAL_STOPPED`. Per-call Codex token counts are telemetry, not provider 5-hour/weekly quota. T31/T33 can rank trusted allowance observations but keep unknown values unknown.

## Remaining gaps

- Automatic/reliable ingestion of live per-account 5-hour and weekly allowance.
- Separately shared external-user Tailscale identity/ACL smoke when such a user is available.
- Always-on service supervision/launch-at-boot for control plane and worker nodes.
- Useful concurrency when a real workload benefits from it.
- Claude/other-provider adapters and provider-neutral handoff.
- Canonical Gmail Developer MCP only if still required.

## Next useful action

Make the validated mesh operational rather than experimental: add supervised launch-at-login/boot packaging, restart/health behavior, and a second live worker-bearing node when available. Keep external-person Tailscale sharing as a separate identity/ACL smoke because the current remote and mesh proofs used the owner's Tailscale identity.

T32 receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.
T33 specification: `docs/T33_MESH_NODE_REGISTRATION.md`.
T33 receipt: `.chatgpt/test-receipts/T33_MESH_LIVE_2026-09-10.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
