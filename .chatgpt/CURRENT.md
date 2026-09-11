# Current project checkpoint

Task: post-T37 operational hardening after autonomous multi-node mesh validation
Status: `HARDENED_FLEET_AND_WORKER_HEALTH_LIVE` — T37 is PASS. Fleet Operator read execution now enforces command-aware read-only semantics, and real Codex authentication failures durably quarantine a worker so a stale `codex login status` cannot keep poisoning mesh readiness.

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
- T35B: PASS for autonomous ChatGPT -> GitHub relay -> gateway -> host -> GitHub result, including remote SSH/Tailscale execution and a live loopback MCP server.
- T36: PASS for real multi-node automatic selection. `macbook-pro-de-loic/openai-B` and `macstudio-worker/openai-A` were simultaneously ready, and live `--worker auto` selected the priority-10 Mac Studio worker and returned `MULTINODE_OK` using `gpt-6-astra`, 4,896 reported tokens, exit 0, read-only/ephemeral, paid-API environment removed.
- T37: PASS for live safety hardening. The full repository suite passed 100 tests. After reloading Fleet Operator, `exec_read` rejected an attempted `python3 -c` file write before execution while allowing `git status`. A real Sparky Codex authentication failure then persisted `openai-A` as `quarantined/auth_failure`; the next mesh heartbeat advertised `ready=false`, `auth=unavailable`, while the valid MacBook and Mac Studio workers remained `ready=true`.

## Fleet Operator boundary

The gateway resolves only locally configured host aliases. SSH destinations/credentials stay on the gateway. SSH is batch/strict-host-key mode. Runtime policy/config lives outside GitHub with mode `0600`. Read mode is command-aware after T37; the write lane remains broader and is the next safety-hardening target.

The GitHub relay remains the immediately usable execution path from this ChatGPT context. Direct Secure MCP Tunnel/custom-app attachment is separate and does not block autonomous fleet operation.

## Next useful action

Harden Fleet Operator write execution so shells/interpreters cannot bypass executable-level admin/destructive policy. After that, the largest routing gap remains trustworthy automatic 5-hour/weekly allowance ingestion.

Fleet Operator spec: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay spec: `docs/FLEET_OPERATOR_RELAY.md`.
T36 receipt: `.chatgpt/test-receipts/T36_TWO_NODE_MESH_LIVE_2026-09-10.md`.
T37 receipt: `.chatgpt/test-receipts/T37_FLEET_READ_AND_WORKER_QUARANTINE_LIVE_2026-09-11.md`.

Paid OpenAI API use for recorded validation: none. T37 required no successful model call.
