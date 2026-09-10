# T34 — live macOS LaunchAgent recovery receipt — 2026-09-10

Status: `PASS`

## Scope

Validate that the already-proven T32/T33 private mesh can run under per-user macOS LaunchAgents and recover from unexpected process death without a manual service restart or a model call.

## Precondition / integration fix

The first live smoke exposed a real launchd-path integration bug: `mesh_service_runner.py` passed `--codex-bin` to `mesh_node_agent.py` before that CLI accepted the option. The node agent therefore crash-looped and disappeared after the T33 TTL.

- fix commit: `9c4ac6f686513d45af82abd4387f1e23e7ba6cfb`
- regression-test commit: `13af9c0e158b5899c16a232439f97e3ecf2a80b6`

After the fix, the node again registered as `macbook-pro-de-loic/openai-B`, `ready=true`.

## Live supervision evidence

Mac Studio control plane:

- `control`: `installed=true`, `loaded=true`
- Tailscale Serve control endpoint: private/tailnet-only on HTTPS port `8444`

MacBook worker host:

- `remote-worker`: `installed=true`, `loaded=true`
- `mesh-node`: `installed=true`, `loaded=true`
- T32 worker endpoint: private/tailnet-only on HTTPS port `8443`

Both worker-host services were deliberately sent `SIGKILL`.

Observed process replacement:

- `remote-worker`: PID `38936 -> 39984`
- `mesh-node`: PID `39681 -> 39985`

After restart:

- both LaunchAgents reported `state = running`
- management status still reported both services `loaded=true`
- no manual start/restart command was needed after the kills

## Mesh recovery evidence

The Mac Studio control plane subsequently returned:

- live node `macbook-pro-de-loic`
- mesh worker `macbook-pro-de-loic/openai-B`
- `auth=chatgpt`
- `ready=true`
- heartbeat age `15.979` seconds in the observed check

This demonstrates crash -> launchd restart -> heartbeat -> mesh rediscovery.

## Boundary

This proves recovery from unexpected process exit inside the logged-in macOS user session. It does not independently prove a complete logout/login cycle or machine reboot, although the installed LaunchAgents are configured with `RunAtLoad`.

No Codex/model call was required for T34. No paid OpenAI API was used.
