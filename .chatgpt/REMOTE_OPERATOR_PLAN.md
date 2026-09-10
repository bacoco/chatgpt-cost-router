# Remote operator goal

Status: `IMPLEMENTED LOCALLY — LIVE GATEWAY BOOTSTRAP NEXT`

Objective: after a one-time gateway installation, ChatGPT can request bounded diagnostics/tests on registered machines and read machine-produced evidence without asking the user to copy/paste terminal commands.

Two transport lanes now share the same server-side FleetRunner policy:

1. **Direct MCP** — ChatGPT -> OpenAI Secure MCP Tunnel -> loopback Fleet Operator MCP -> local/SSH host. This is the preferred long-term path when the ChatGPT workspace supports full custom-MCP write actions.
2. **GitHub relay** — ChatGPT GitHub connector -> `fleet/commands` -> supervised gateway relay -> local/SSH host -> deterministic `fleet/results/<job_id>` result branch. This is the immediate compatibility path for the current Pro context.

Security boundary:
- callers address aliases only; SSH targets/credentials remain local;
- no raw SSH private key is exposed to ChatGPT or GitHub;
- per-host allowed roots and read/write executable allowlists;
- root/admin commands hard blocked;
- destructive command families require explicit authorization;
- SSH uses BatchMode + StrictHostKeyChecking + timeouts/keepalive;
- bounded output, timeout and parallelism;
- GitHub jobs are versioned, expiry-limited, filename-bound and replay-protected by a local ledger;
- relay reads only the dedicated command branch, not PR/issue content;
- results are sanitized and written to deterministic result branches;
- model/API calls are never implicit;
- services run as the logged-in user via LaunchAgent, never root.

Implementation:
- `fleet_operator/core.py`
- `fleet_operator/mcp_server.py`
- `fleet_operator/relay.py`
- `fleet_operator/macos.py`
- `scripts/fleet_operator_server.py`
- `scripts/fleet_operator_relay.py`
- `scripts/fleet_operator_macos.py`
- `docs/FLEET_OPERATOR_PLUGIN.md`
- `docs/FLEET_OPERATOR_RELAY.md`

Next proof: install once on the chosen gateway, then create one `status` job from ChatGPT and verify that ChatGPT itself reads the pushed result without terminal assistance.
