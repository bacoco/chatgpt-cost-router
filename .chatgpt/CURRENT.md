# Current project checkpoint

Task: T35 Fleet Operator remote-control layer after T34 supervision validation
Status: `FLEET_OPERATOR_RELAY_LIVE` — T35B is PASS. ChatGPT can now submit bounded jobs through GitHub and receive machine-produced result branches without terminal copy/paste. The gateway has live access to both the local MacBook alias and the remote Mac Studio alias over SSH/Tailscale. The loopback MCP server is also installed/running; Secure MCP Tunnel / direct custom-app attachment remains a separate product/UI lane.

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

## Fleet Operator boundary

The gateway resolves only locally configured host aliases. SSH destinations/credentials stay on the gateway. SSH is batch/strict-host-key mode. Per-host executable/path allowlists, hard-blocked admin commands, destructive-command authorization, timeouts and output caps are enforced server-side. Runtime policy/config lives outside GitHub with mode `0600`.

As of 2026-09-10, OpenAI documents full custom-MCP write/modify actions for Business and Enterprise/Edu; Pro custom MCP is read/fetch only. Therefore direct MCP SSH writes are implemented but are not claimed callable from this Pro chat. The GitHub relay is the immediate compatible execution path because this ChatGPT context already has authenticated GitHub write access.

## Next useful action

Use Fleet Operator itself for subsequent host inspection/tests instead of asking the user for terminal copy/paste. Add additional machines to the gateway's local fleet config only when their SSH/Tailscale endpoint and allowed root are known. The remaining direct-plugin step is Secure MCP Tunnel plus attaching the custom app in a supported ChatGPT workspace; that does not block the already-live GitHub relay control path.

Fleet Operator spec: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay spec: `docs/FLEET_OPERATOR_RELAY.md`.
Job schema: `schemas/fleet-operator-job.schema.json`.
T34 receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.
T35B receipt: `.chatgpt/test-receipts/T35B_FLEET_OPERATOR_LIVE_2026-09-10.md`.

Paid OpenAI API/model use for T35A/T35B validation: none.
