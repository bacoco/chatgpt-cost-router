# T34 — macOS LaunchAgent supervision for the private worker mesh

Status: `PASS — LIVE INSTALL + FORCED-CRASH RECOVERY VERIFIED`

## Goal

Turn the T32/T33 proof-of-concept into a user-session service that comes back automatically after login or an unexpected process exit, without root privileges and without putting account identities, credentials or `CODEX_HOME` values in GitHub.

## Design

Use per-user macOS **LaunchAgents**, not LaunchDaemons. Codex authentication belongs to the logged-in user's home and worker-specific `CODEX_HOME`; running the mesh as root would be the wrong ownership/security model.

Three supervised roles exist:

- `mesh-control` — Mac Studio control plane, loopback `8790`, private Tailscale Serve `8444`;
- `remote-worker` — T32 facade on a worker host, loopback `8787`, private Tailscale Serve `8443`;
- `mesh-node` — T33 heartbeat/registration agent on a worker host.

`RunAtLoad=true` and `KeepAlive={SuccessfulExit=false}` restart a role when it exits unexpectedly. The runner waits for Tailscale before starting and the mesh-node waits for the local T32 port before registering.

## Local-only configuration

Installer-generated runtime JSON lives under `~/.config/chatgpt-cost-router/` with mode `0600`. It may contain the local Tailscale allowlist, control-plane URL and selected worker aliases. These values are not committed to GitHub and are not placed directly in the LaunchAgent plist.

Plists live in `~/Library/LaunchAgents/` and only point to the repository runner + local config file. No root/Sudo is required.

## Commands

Control-plane Mac:

```bash
python3 scripts/macos_mesh_service.py install-control \
  --allowed-users "$COST_ROUTER_MESH_ALLOWED_USERS"
```

Worker-node Mac:

```bash
python3 scripts/macos_mesh_service.py install-worker-node \
  --control-url "$COST_ROUTER_MESH_CONTROL_URL" \
  --allowed-users "$COST_ROUTER_ALLOWED_TAILSCALE_USERS" \
  --workers "$COST_ROUTER_REMOTE_WORKERS"
```

Status:

```bash
python3 scripts/macos_mesh_service.py status
```

Uninstall:

```bash
python3 scripts/macos_mesh_service.py uninstall control
python3 scripts/macos_mesh_service.py uninstall worker-node
```

## Safety boundaries

- per-user LaunchAgents only;
- no root daemon;
- no public Funnel;
- existing T32/T33 loopback-only services remain unchanged;
- runtime config files are `0600` and Git-untracked because they are created in the user's home;
- LaunchAgent plists contain no Tailscale login, worker alias or authentication material;
- absolute Python/Tailscale/Codex executable paths are resolved during installation so LaunchAgent PATH differences do not silently select another binary.

## Local verification

Eight isolated tests cover private config permissions, LaunchAgent keepalive/run-at-load structure, no personal allowlist data in plists, control dry-install, worker-node two-agent dry-install, bad control URL rejection, versioned runner config, and absolute registry/binary-path behavior under launchd. Python compilation and plist generation pass without model calls.

## Live proof

T34 was verified on the live two-Mac mesh without a model call.

- Mac Studio: `mesh-control` was installed as a per-user LaunchAgent and reported `installed=true`, `loaded=true`; Tailscale Serve remained private on port `8444`.
- MacBook: `remote-worker` and `mesh-node` were installed as per-user LaunchAgents and both reported `installed=true`, `loaded=true`; the T32 endpoint remained tailnet-only on port `8443`.
- A launchd integration bug was exposed during the first smoke: the runner passed `--codex-bin` to `mesh_node_agent.py` before that CLI accepted the option. The agent crash-looped and expired from the mesh by TTL. Commit `9c4ac6f686513d45af82abd4387f1e23e7ba6cfb` added the argument and commit `13af9c0e158b5899c16a232439f97e3ecf2a80b6` added the regression test.
- After the fix, both supervised MacBook processes were deliberately killed with `SIGKILL`. `remote-worker` changed PID `38936 -> 39984`; `mesh-node` changed PID `39681 -> 39985`. `launchctl` then reported both services `state = running`, and the management CLI still reported both `loaded=true`.
- Without a manual service restart, the Mac Studio subsequently rediscovered `macbook-pro-de-loic/openai-B` with `ready=true` and a fresh heartbeat (`age_seconds=15.979` in the observed check).

This proves unexpected-process recovery through per-user `launchd`, followed by automatic heartbeat recovery into the T33 mesh. It does **not** yet prove a full logout/login or machine reboot cycle; `RunAtLoad` is configured, but that distinct lifecycle test has not been executed.

Receipt: `.chatgpt/test-receipts/T34_LAUNCHD_RECOVERY_LIVE_2026-09-10.md`.
