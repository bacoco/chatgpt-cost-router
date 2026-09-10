# Validation status — 10 September 2026

This is the **authoritative current status snapshot**. Historical experiment logs preserve earlier states; when they conflict, use this file plus durable receipts and current GitHub state.

## Status vocabulary

- `PASS`: requested behavior actually executed and verified with observable evidence.
- `PARTIAL_STOPPED`: useful evidence preserved, but further measurement intentionally stopped.
- `BLOCKED_MISSING_CONNECTOR`: required connector unavailable in the tested context.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built/tested because current evidence does not justify the cost.
- `NOT_YET_FORMALLY_TESTED`: distinct test remains unexecuted.

## Current validated state

```text
T01-T09     ChatGPT/GitHub cloud capabilities                 PASS where applicable
T10         Codex CLI persistent local Mac worker             PASS — A/B/C1/C2
T10-VM      distinct Ubuntu/cloud persistent VM               NOT_YET_FORMALLY_TESTED — optional
T11/T12     original persistent Worker MCP / scheduler lane   DEFERRED_NOT_JUSTIFIED
T13         quota/cost experiment                             PARTIAL_STOPPED
T14         Gmail Developer MCP in ChatGPT/Scheduled Tasks    BLOCKED_MISSING_CONNECTOR
T14-alt     Codex Mac Chat + built-in Gmail                   PASS
T15/T16/16A scheduler-chat continuation / repo recovery       PASS
T17/T18/T19 Actions control gate / repo scheduler workspace   PASS
T20/T23/T24 ChatGPT Cloud -> Codex -> ChatGPT round trip      PASS
T21/T22     workflow skills / project bootstrap               PASS
T25         Codex Mac Work capability characterization        PASS
T26         Codex Mac Work -> pushed GitHub return            PASS — independently reverified
T27         headless callable Codex CLI via codex exec        PASS
T28A        CODEX_HOME auth/state isolation                   PASS
T28B        two distinct authorized account workers           PASS
T29         standalone parallel smoke                         DEFERRED_NOT_JUSTIFIED
T30         two-worker local broker                           PASS — live alias dispatch verified
T31A        quota/budget-aware selection logic                PASS — deterministic local tests
T32         private remote worker over Tailscale Serve        PASS — live second-device dispatch
T33         automatic node registry / cross-node mesh routing PASS — live two-machine auto dispatch
T34         macOS LaunchAgent supervision/recovery            PASS — live forced-crash recovery
T35A        Fleet Operator SSH/MCP + GitHub relay code         PASS — 22 isolated tests; live gateway pending

GitHub Actions control plane                                  PASS
GitHub hosted runner allocation                               BLOCKED_EXTERNAL_CAPACITY during observed test
Create repository via tested GitHub Developer MCP             BLOCKED — observed 403
Paid OpenAI API                                               NOT USED
```

## Recent worker evidence

T30 proved a controller can address a specific isolated ChatGPT-authenticated Codex worker by alias without manual account swapping. T31A added deterministic budget-aware selection without a model call.

T32 then proved the private remote primitive end to end. A second Tailscale device resolved and pinged the worker Mac, reached the loopback-only broker through Tailscale Serve, saw only `openai-B`, and remotely dispatched it. The result was `REMOTE_OK`, provider `openai`, model `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, with paid-API environment removed. The live caller used the owner's Tailscale identity; a separate external-person identity remains untested.

## T33 — automatic node registration / live cross-node mesh

T33 adds a private control plane and node heartbeat agent. A node advertises only its `.ts.net` Serve endpoint, location, worker aliases, ready/auth state, cost class, priority and optional non-secret budget observations. It does not advertise `CODEX_HOME`, local paths, credentials, token material or email addresses. Runtime owner binding is stored as a SHA-256 value, not the login itself.

Seven isolated T33 tests pass without a model call: identity/endpoint validation; durable registration + TTL expiry; node-id takeover rejection; namespacing/ambiguity; headroom-aware selection; safe cross-node forwarding; and local advertisement redaction. Python compilation and Bash syntax checks also pass.

The live proof then succeeded across two machines. The MacBook heartbeat agent registered node `macbook-pro-de-loic` with worker `openai-B` into the Mac Studio control plane. The control plane reported the node with a fresh heartbeat and exposed `macbook-pro-de-loic/openai-B`. A `run --worker auto` request dynamically selected that mesh worker and returned `MESH_OK` through the remote T32 endpoint. Execution telemetry: provider `openai`, model `gpt-6-astra`, 4,612 reported tokens, 5.888 s, exit 0, read-only/ephemeral, paid-API environment removed.

Therefore T33 is PASS for automatic node registration/discovery and cross-machine automatic dispatch. This single-node live smoke does not yet establish useful load balancing among two simultaneously available worker nodes.

Specification: `docs/T33_MESH_NODE_REGISTRATION.md`.
Receipt: `.chatgpt/test-receipts/T33_MESH_LIVE_2026-09-10.md`.

## T34 — macOS service supervision / live recovery

T34 adds per-user macOS LaunchAgents for three roles: mesh control plane, T32 remote-worker facade, and T33 mesh-node heartbeat agent. Runtime values such as Tailscale allowlists, control-plane URL and worker aliases are written only to local `~/.config/chatgpt-cost-router/*.json` files with mode `0600`; they are not committed and are not embedded in the plist. The plists contain only the absolute Python runner path, local config-file path, RunAtLoad/KeepAlive policy and log paths.

The service runner resolves/records absolute Python, Tailscale and Codex binaries at install time, uses absolute `examples/workers.json` paths so launchd working-directory differences cannot break discovery, waits for Tailscale before starting, and waits for the local T32 port before starting mesh-node registration.

Eight isolated tests pass without a model call, including private config permissions, plist structure/redaction, dry installs for control and worker-node roles, invalid control URL rejection, versioned config validation, and absolute registry/binary-path behavior under launchd.

The live installation/recovery proof then succeeded. The Mac Studio `mesh-control` LaunchAgent reported installed/loaded. The MacBook `remote-worker` and `mesh-node` LaunchAgents also reported installed/loaded, with the T32 endpoint remaining tailnet-only. An initial integration smoke exposed a real `--codex-bin` CLI mismatch that caused the node agent to crash-loop; commits `9c4ac6f686513d45af82abd4387f1e23e7ba6cfb` and `13af9c0e158b5899c16a232439f97e3ecf2a80b6` corrected and regression-tested it.

After the fix, both MacBook services were deliberately killed with `SIGKILL`. `remote-worker` restarted from PID `38936` to `39984`; `mesh-node` restarted from `39681` to `39985`. `launchctl` reported both `state = running`, the management CLI reported both `loaded=true`, and the Mac Studio subsequently rediscovered `macbook-pro-de-loic/openai-B` as `ready=true` with a fresh heartbeat (`age_seconds=15.979`). No manual service restart or model call was used for this recovery proof.

Therefore T34 is PASS for per-user launchd supervision and recovery from unexpected process exit, including automatic re-registration into the mesh. A full logout/login or machine reboot lifecycle remains a distinct untested check.

Specification: `docs/T34_MACOS_SERVICE_SUPERVISION.md`.
Receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.

## T35A — Fleet Operator code / self-service control path

The project now contains a private Fleet Operator layer intended to eliminate routine user terminal copy/paste. The gateway maps caller-visible aliases to local-only host configuration; SSH targets and credentials are not returned to clients. It supports local and SSH transports, per-host root/command allowlists, strict host-key checking, batch SSH, bounded time/output/fan-out, hard-blocked root/admin commands, and a separate explicit gate for destructive commands.

A loopback-only MCP 2.x Streamable HTTP server exposes truthful read-only and write-capable tools and is packaged for OpenAI Secure MCP Tunnel. Runtime API key material is referenced from a local mode-0600 file rather than embedded in the LaunchAgent or repository.

Because the current ChatGPT Pro product boundary does not provide full custom-MCP write actions, T35A also implements a GitHub command-relay compatibility lane. A supervised gateway can poll versioned jobs only from `fleet/commands`, validate action/expiry/filename, reject replay with a local ledger, execute through the same FleetRunner policy, persist a local result first, and push a sanitized deterministic result branch `fleet/results/<job_id>`. This does not execute PR/issue text or arbitrary branches and does not invoke a model/API.

Twenty-two isolated Fleet Operator tests pass and all new Python files compile. These tests do **not** prove a real SSH connection, Secure MCP Tunnel connection, GitHub result push, or ChatGPT invocation. Live gateway bootstrap plus one ChatGPT-created/ChatGPT-read relay job is still required before the no-copy/paste lane is PASS.

Specification: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay: `docs/FLEET_OPERATOR_RELAY.md`.
Receipt: `.chatgpt/test-receipts/T35A_FLEET_OPERATOR_CODE_2026-09-10.md`.

## Remaining gaps

1. Live Fleet Operator gateway bootstrap plus one autonomous GitHub-relay job/result round trip.
2. Direct ChatGPT MCP write actions remain product-plan/workspace limited; current Pro custom MCP is read/fetch only.
3. Automatic/reliable live 5-hour and weekly allowance ingestion per account.
4. Separately shared external-user Tailscale identity/ACL smoke when available.
5. A second simultaneously live worker-bearing node for real multi-node selection/load distribution.
6. Full logout/login or machine reboot lifecycle recovery for LaunchAgents, if operationally worth testing.
7. Useful broker-managed concurrency when a real workload benefits from it.
8. Claude/other-provider worker adapters plus provider-neutral handoff.
9. Canonical Gmail Developer MCP only if operationally required.
10. Repository creation through the tested GitHub Developer MCP remains blocked by the observed 403.

No paid OpenAI API/model call was used for T35A local validation.
