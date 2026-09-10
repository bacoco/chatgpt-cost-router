# T34 — macOS LaunchAgent supervision for the private worker mesh

Status: `CODE COMPLETE — LOCAL TESTS PASS; LIVE INSTALL/RESTART SMOKE NEXT`

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

Six isolated tests cover private config permissions, LaunchAgent keepalive/run-at-load structure, no personal allowlist data in plists, control dry-install, worker-node two-agent dry-install, bad control URL rejection and versioned runner config. Python compilation and plist generation pass without model calls.

## Live proof required

Install on the current Mac Studio control plane and MacBook worker node, confirm all three LaunchAgents are loaded, kill one supervised process, verify launchd restarts it, then confirm `nodes`/`workers` recover without manual server restart. A model call is unnecessary for T34 unless a final end-to-end dispatch is desired after restart.
