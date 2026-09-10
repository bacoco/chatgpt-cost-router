# T33 — automatic worker-node registration and cross-node mesh routing

Status: `PASS — LIVE TWO-MACHINE REGISTRATION + AUTO DISPATCH VERIFIED`

## Goal

Remove hard-coded worker placement from the controller. A worker host periodically advertises its private Tailscale Serve endpoint plus non-secret worker availability/cost/budget metadata. The control plane keeps only fresh heartbeats and routes to a live worker without knowing its `CODEX_HOME` or local filesystem.

## Architecture

```text
worker node(s)                         control plane
-------------                         -------------
local Codex workers                    loopback mesh service
remote-worker Serve endpoint  --->     Tailscale Serve HTTPS
mesh_node_agent heartbeat      --->     TTL node registry
                                           |
remote user/controller  ------------> nodes / workers / run
                                           |
                                           +--> selected node /v1/run
```

## Implemented

- `cost_router/mesh.py`: validated `.ts.net` node endpoints, private durable node registry, TTL expiry, namespaced workers, cross-node selection and dispatch.
- `scripts/mesh_control_server.py`: loopback-only control plane behind Tailscale Serve.
- `scripts/mesh_node_agent.py`: node self-discovery from `tailscale status --json`, local worker probing and 30-second heartbeat registration; `--once` is available for bounded tests.
- `scripts/mesh_client.py`: `health`, `nodes`, `workers`, and `run` client.
- start/stop helpers for the control plane and heartbeat agent.

## Safety boundary

- control plane binds only to loopback and must sit behind Tailscale Serve;
- Tailscale user identity is allowlisted;
- node endpoint must be HTTPS and end in `.ts.net`;
- node advertisements contain no `CODEX_HOME`, token, email, API key or local path;
- the runtime registry stores only a SHA-256 owner binding, not the Tailscale login itself;
- stale nodes disappear from routing after the TTL (default 120 s);
- explicit duplicate worker aliases across nodes fail closed unless addressed as `node/worker`;
- `paid-api` worker advertisements are rejected;
- the control plane forwards only the selected local worker alias and prompt to the already-validated T32 endpoint;
- remote worker execution therefore retains T32's read-only, ephemeral, user-config-isolated, paid-API-env-stripped boundary.

## Selection

`auto` considers only fresh, ready ChatGPT-authenticated workers. It ranks included/free classes before paid classes, then prefers known allowance headroom over unknown headroom and larger minimum 5-hour/weekly headroom before static priority. Quota fields remain observations; the mesh does not invent provider quota.

## Local verification

Seven isolated T33 tests pass without a model call:

1. Tailscale identity and endpoint validation;
2. durable registration plus TTL expiry;
3. node-id owner takeover rejection;
4. worker namespacing and ambiguous-alias fail-closed behavior;
5. headroom-aware automatic selection;
6. cross-node forwarding of only `worker` + `prompt`;
7. local advertisement redaction of `CODEX_HOME`/paths.

Python compilation and Bash syntax checks for the new server/agent/client/start/stop files pass.

## Live proof — 2026-09-10

PASS. A Mac Studio ran the mesh control plane behind Tailscale Serve on dedicated HTTPS port `8444`. The MacBook worker host started the heartbeat agent and registered itself as node `macbook-pro-de-loic`, advertising only the already-approved `openai-B` worker through its T32 Serve endpoint. The registration reported `ready=true`, `auth=chatgpt`, `cost_class=included`, and unknown 5-hour/weekly quota observations rather than inventing values.

From the control-plane machine, `nodes` returned that live node with a fresh heartbeat age of about 2.5 seconds and `workers` exposed the namespaced worker `macbook-pro-de-loic/openai-B`. A subsequent mesh `run --worker auto` dynamically resolved that worker and returned:

```text
MESH_OK
worker_alias=openai-B
paid_api_used=NO
```

Observed execution telemetry: provider `openai`, model `gpt-6-astra`, `4,612` reported tokens, `5.888 s`, exit code `0`, `read-only`, `ephemeral`, paid-API environment removed.

This closes T33 for automatic node registration/discovery plus cross-machine automatic dispatch. It does not prove useful multi-node load balancing yet because only one live worker node was registered in this smoke. A second live worker-bearing node is the next proof if actual multi-node selection is required.
