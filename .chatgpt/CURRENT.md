# Current project checkpoint

Task: T35 Fleet Operator remote-control layer after T34 supervision validation
Status: `FLEET_OPERATOR_CODE_READY` — T34 is PASS. The project has now pivoted from asking the user to execute every host command manually to a private Fleet Operator gateway. Core SSH/MCP policy, macOS packaging, Secure MCP Tunnel packaging and a GitHub command-relay compatibility lane are implemented and locally tested. Live gateway installation and one autonomous job remain before the no-copy/paste control path is PASS.

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
- T35A: CODE COMPLETE / LOCAL TESTS PASS for Fleet Operator. Twenty-two isolated tests pass without a model call. The direct MCP server binds to loopback and is intended for OpenAI Secure MCP Tunnel. A separate GitHub relay can execute versioned jobs through the same FleetRunner policy and return deterministic result branches.

## Fleet Operator boundary

The gateway resolves only locally configured host aliases. SSH destinations/credentials stay on the gateway. SSH is batch/strict-host-key mode. Per-host executable/path allowlists, hard-blocked admin commands, destructive-command authorization, timeouts and output caps are enforced server-side. Runtime policy/config lives outside GitHub with mode `0600`.

As of 2026-09-10, OpenAI documents full custom-MCP write/modify actions for Business and Enterprise/Edu; Pro custom MCP is read/fetch only. Therefore direct MCP SSH writes are implemented but are not claimed callable from this Pro chat. The GitHub relay is the immediate compatible execution path because this ChatGPT context already has authenticated GitHub write access.

## Next useful action

Install Fleet Operator once on a gateway Mac that can reach the fleet over SSH/Tailscale, start the supervised GitHub relay, and submit one `status` job from ChatGPT to `fleet/commands`. PASS requires the gateway to execute it without user terminal intervention and push `.fleet/results/<job_id>.json` to `fleet/results/<job_id>`, which ChatGPT then reads itself. After that, terminal copy/paste is no longer required for bounded fleet operations.

Direct-MCP tunnel setup is a separate optional lane until the account has full custom-MCP write access. It can already be installed/tested for read-only inspection.

Fleet Operator spec: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay spec: `docs/FLEET_OPERATOR_RELAY.md`.
Job schema: `schemas/fleet-operator-job.schema.json`.
T34 receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.

Paid OpenAI API/model use for T35A local validation: none.
