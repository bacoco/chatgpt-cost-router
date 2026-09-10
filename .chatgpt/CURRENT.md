# Current project checkpoint

Task: post-T36 operational hardening after autonomous multi-node mesh validation
Status: `MULTI_NODE_MESH_LIVE` — T36 is PASS. Using Fleet Operator without user terminal intervention, ChatGPT brought a second authenticated worker-bearing machine online, verified two simultaneous live nodes, and `--worker auto` selected the higher-priority Mac Studio worker and returned `MULTINODE_OK`. Sparky was also connected and diagnosed autonomously, but its stored ChatGPT refresh token is stale and it has been removed from active routing.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Validated core

- T01-T34: PASS where recorded, except intentionally deferred/blocked experiments documented in the authoritative status.
- T28A/T28B: PASS for two distinct authorized OpenAI account workers isolated by `CODEX_HOME`.
- T30: PASS for live local broker alias dispatch.
- T31A: PASS for deterministic quota/budget-aware selection logic; provider quota ingestion itself remains unproven.
- T32: PASS for private second-device Tailscale dispatch to `openai-B`.
- T33: PASS for heartbeat registration and cross-machine `--worker auto` mesh dispatch.
- T34: PASS for per-user LaunchAgent supervision and forced-crash recovery without manual restart or model call.
- T35A: CODE COMPLETE / LOCAL TESTS PASS for Fleet Operator.
- T35B: PASS for autonomous ChatGPT -> GitHub relay -> gateway -> host -> GitHub result. A ChatGPT-created `status` job executed on the MacBook and another on the remote Mac Studio without user terminal intervention. The Mac Studio path exercised SSH/Tailscale. The Python packaging bug exposed by the first MCP install was fixed by selecting an installed Python >=3.10; 23 Fleet Operator regression tests then passed on the MacBook. The MCP server installed successfully under Python 3.11 and reports `installed=true`, `loaded=true`, with loopback port 8810 open.
- T36: PASS for real multi-node automatic selection. Fleet Operator discovered/auth-checked candidate hosts, rejected Sparky as operationally stale after a real 401 refresh-token failure, brought `macstudio-worker/openai-A` online alongside `macbook-pro-de-loic/openai-B`, and a live `--worker auto` dispatch selected Mac Studio priority 10 and returned `MULTINODE_OK` using `gpt-6-astra`, 4,896 reported tokens, 14.644 s, exit 0, read-only/ephemeral, paid-API environment removed.

## Fleet Operator boundary

The gateway resolves only locally configured host aliases. SSH destinations/credentials stay on the gateway. SSH is batch/strict-host-key mode. Per-host executable/path allowlists, hard-blocked admin commands, destructive-command authorization, timeouts and output caps are enforced server-side. Runtime policy/config lives outside GitHub with mode `0600`.

As of 2026-09-10, OpenAI documents full custom-MCP write/modify actions for Business and Enterprise/Edu; Pro custom MCP is read/fetch only. Therefore direct MCP SSH writes are implemented but are not claimed callable from this Pro chat. The GitHub relay is the immediate compatible execution path because this ChatGPT context already has authenticated GitHub write access.

## Next useful action

Use Fleet Operator itself for subsequent host inspection/tests instead of asking the user for terminal copy/paste. The highest-value engineering work is now hardening worker health and Fleet Operator read/write policy: a worker that only passes `codex login status` can still have an unusable refresh token, and executable-only allowlists need command-aware read validation before the read surface is treated as strongly read-only. Direct Secure MCP Tunnel attachment remains optional and does not block the live relay.

Fleet Operator spec: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay spec: `docs/FLEET_OPERATOR_RELAY.md`.
Job schema: `schemas/fleet-operator-job.schema.json`.
T34 receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.
T35B receipt: `.chatgpt/test-receipts/T35B_FLEET_OPERATOR_LIVE_2026-09-10.md`.
T36 receipt: `.chatgpt/test-receipts/T36_TWO_NODE_MESH_LIVE_2026-09-10.md`.

Paid OpenAI API use for recorded validation: none. T36 used one successful ChatGPT-authenticated Codex call for the final routing proof; earlier Sparky attempts failed at ChatGPT authentication before producing a model result.
