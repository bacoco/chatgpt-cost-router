# T32 — private remote worker over Tailscale Serve

Status: `PASS — LIVE SECOND-DEVICE TAILNET DISPATCH VERIFIED`

## Goal

Let an authorized remote person/controller submit bounded work to a Codex worker physically running on the owner's Mac, without exposing SSH, a shell, raw Codex, credentials, or a public Internet listener.

## Architecture

```text
remote user/device
  -> Tailscale identity + ACL/share
  -> Tailscale Serve HTTPS
  -> 127.0.0.1:8787 only
  -> remote worker facade
  -> local broker
  -> allowed worker alias / CODEX_HOME
  -> codex exec --ephemeral --sandbox read-only
```

GitHub remains the durable project-state/handoff bus when a task needs repository state. This HTTP layer is only private dispatch/telemetry transport.

## Implemented safety boundary

- backend refuses non-loopback bind addresses;
- `Tailscale-User-Login` is mandatory and must match a local allowlist;
- allowed worker aliases are a separate local allowlist;
- remote clients cannot supply a filesystem workspace path;
- each call gets a temporary private task directory that is deleted after completion;
- request JSON accepts only `worker` and `prompt` and is size-limited;
- Codex remains `--ephemeral --sandbox read-only` and remote calls add `--ignore-user-config` so the host user's Codex config/MCP/plugin configuration is not loaded;
- paid API-key environment variables are stripped by the broker;
- responses omit `CODEX_HOME`, local task paths and Codex stderr/session ids;
- no credentials, user emails or allowlists are committed to GitHub.

## Local environment

Required only on the worker Mac at runtime:

```bash
export COST_ROUTER_ALLOWED_TAILSCALE_USERS='remote-user-tailnet-login'
export COST_ROUTER_REMOTE_WORKERS='openai-B'
export COST_ROUTER_REMOTE_WORKSPACE_ROOT="$HOME/codex-remote-worker-tasks"
python3 scripts/remote_worker_server.py --port 8787
```

The repository also contains a launcher that starts the localhost backend and configures a dedicated Tailscale Serve HTTPS port `8443` in the background:

```bash
export COST_ROUTER_ALLOWED_TAILSCALE_USERS='remote-user-tailnet-login'
export COST_ROUTER_REMOTE_WORKERS='openai-B'
bash scripts/start_remote_worker.sh
```

Equivalent manual Serve configuration:

```bash
tailscale serve --bg --https=8443 8787
```

Tailscale Serve should report a private `https://<device>.<tailnet>.ts.net` URL. Do **not** use Tailscale Funnel for this worker.

## API

Authenticated through Tailscale Serve identity headers:

- `GET /v1/health`
- `GET /v1/workers`
- `POST /v1/run` with `{"worker":"openai-B","prompt":"..."}`

A tiny client is included for the remote Mac/PC:

```bash
python3 scripts/remote_worker_client.py --url https://<device>.<tailnet>.ts.net:8443 health
python3 scripts/remote_worker_client.py --url https://<device>.<tailnet>.ts.net:8443 workers
python3 scripts/remote_worker_client.py --url https://<device>.<tailnet>.ts.net:8443 run --worker openai-B --prompt 'Return exactly REMOTE_OK'
```

Stop the dedicated listener with `bash scripts/stop_remote_worker.sh`.

## Verification

Six isolated unit tests cover identity allowlisting, request validation, worker allowlisting, path redaction, temporary-workspace cleanup, and a fake Codex dispatch. They make no model call and consume no Codex allowance.

## Live verification — 2026-09-10

PASS from a second Tailscale device. A Mac Studio on the same tailnet resolved the worker Mac through MagicDNS, `tailscale ping` reached it at its Tailscale address, and the remote client reached the HTTPS Serve endpoint. `GET /v1/health` returned `ok=true` with `transport=tailscale-serve`; `GET /v1/workers` exposed only the allowlisted `openai-B` worker as ChatGPT-authenticated and ready.

One real remote dispatch then called `openai-B` through the remote facade. The response returned `REMOTE_OK`, provider `openai`, model `gpt-6-astra`, `4,610` reported tokens, `6.753 s`, and exit code `0`. It also confirmed `read-only`, `ephemeral`, and paid-API environment removal. No raw `CODEX_HOME`, local workspace path, Codex stderr, or session id was returned.

This closes T32 for **second-device private remote transport and execution**. The live caller used the owner's existing Tailscale identity, so a separately shared external person's identity/ACL path (for example a partner using a different Tailscale login) remains a distinct operational smoke, not a prerequisite for the transport primitive itself.

Durable receipt: `.chatgpt/test-receipts/T32_REMOTE_WORKER_LIVE_2026-09-10.md`.
