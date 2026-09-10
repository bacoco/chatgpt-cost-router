# Current project checkpoint

Task: T33 automatic node registration / cross-node mesh after T32 live remote transport
Status: `MESH_CODE_READY` — local two-account workers, alias/budget broker and private second-device Tailscale dispatch are validated. T33 now adds heartbeat registration, TTL discovery and cross-node routing. Seven isolated T33 tests pass without a model call; one live two-node registration/dispatch remains before T33 is PASS.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Validated core

- T01-T30: PASS where recorded, except intentionally deferred/blocked experiments documented in the authoritative status.
- T28A/T28B: PASS for two distinct authorized OpenAI account workers isolated by `CODEX_HOME`.
- T30: PASS for live local broker alias dispatch.
- T31A: PASS for deterministic quota/budget-aware selection logic; provider quota ingestion itself remains unproven.
- T32: PASS for private remote dispatch from a second Tailscale device to `openai-B` on another Mac: `REMOTE_OK`, `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, paid-API environment removed.
- T33A: CODE COMPLETE / LOCAL TESTS PASS. Worker hosts can self-discover their Tailscale DNS name, advertise redacted worker state, heartbeat into a loopback-only/Tailscale control plane, expire by TTL, and be selected/forwarded across nodes.

## Cost / quota boundary

T13 remains `PARTIAL_STOPPED`. Per-call Codex token counts are telemetry, not provider 5-hour/weekly quota. T31/T33 can rank trusted allowance observations but keep unknown values unknown.

## Remaining gaps

- Live T33 registration plus one cross-node mesh dispatch.
- Automatic/reliable ingestion of live per-account 5-hour and weekly allowance.
- Separately shared external-user Tailscale identity/ACL smoke when such a user is available.
- Always-on service supervision/launch-at-boot for control plane and worker nodes.
- Useful concurrency when a real workload benefits from it.
- Claude/other-provider adapters and provider-neutral handoff.
- Canonical Gmail Developer MCP only if still required.

## Next safe action

Run the T33 control plane on the Mac Studio, register the already-running MacBook T32 worker node with `mesh_node_agent.py --once` (then optionally start the heartbeat daemon), verify that the control plane discovers `node/openai-B`, and send exactly one bounded `run` through the mesh. No model call is needed for registration, discovery or selection.

T32 receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.
T33 specification: `docs/T33_MESH_NODE_REGISTRATION.md`.
Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.

Paid OpenAI API used for recorded validations: no.
