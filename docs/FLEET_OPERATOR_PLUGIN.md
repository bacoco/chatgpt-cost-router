# Fleet Operator — private SSH app for ChatGPT

Status: `CODE COMPLETE / LOCAL POLICY TESTS PASS — HOST INSTALL + TUNNEL + LIVE CHATGPT CALL PENDING`

## Goal

After one gateway installation, ChatGPT addresses machines by alias and can inspect or operate them without asking the user to copy/paste terminal commands. SSH destinations and authentication stay on the gateway; ChatGPT never receives an SSH private key.

```text
ChatGPT
  |
  | custom MCP app
  v
OpenAI Secure MCP Tunnel        (outbound-only from gateway)
  |
  v
127.0.0.1:8810/mcp
Fleet Operator MCP
  |
  +--> gateway host locally
  +--> SSH/Tailscale --> Mac / Linux / DGX / VM aliases
```

The MCP implementation uses the current MCP Python SDK Streamable HTTP transport and binds only to loopback. OpenAI Secure MCP Tunnel is the intended production ingress; do not expose port 8810 through Funnel or a public listener.

## Tools

Read-only tools:

- `fleet_list_hosts`
- `fleet_host_status`
- `fleet_read_file`
- `fleet_exec_read`
- `fleet_exec_many_read`
- `fleet_git_status`
- `fleet_relay_result`

Write-capable tools:

- `fleet_exec_write`
- `fleet_exec_many_write`
- `fleet_git_pull`

The MCP ToolAnnotations describe the real behavior. Write tools are not mislabeled as read-only.

## Server-side safety boundary

- caller supplies a host alias, never an SSH target;
- aliases resolve only from local `~/.config/chatgpt-cost-router/fleet-operator.json`;
- local config is mode `0600` and is not committed;
- SSH uses `BatchMode=yes`, strict host-key checking, connection timeout and keepalive;
- commands are argv arrays and are shell-quoted by the gateway;
- each host has explicit read/write executable allowlists;
- `sudo`, `su`, reboot/shutdown, raw disk tools and similar admin commands are hard blocked;
- `rm`, `kill`/`pkill`, destructive `git` and destructive `launchctl` require `allow_destructive=true`;
- filesystem reads/cwd are limited to locally configured roots;
- stdout/stderr are bounded and timeout is enforced;
- fan-out is bounded to 32 concurrent hosts;
- SSH targets, credentials and key material never appear in inventory results.

## macOS gateway packaging

`requirements-fleet-operator.txt` pins the MCP SDK. The installer creates a private virtualenv and a per-user LaunchAgent. It never runs as root.

```bash
python3 scripts/fleet_operator_macos.py bootstrap \
  --local-host gateway /absolute/allowed/root \
  --ssh-host worker-1 user@worker-1.example.ts.net /absolute/allowed/root
```

This creates the local fleet policy, starts the MCP server, and starts the GitHub relay described below. The relay is deliberately useful even before the ChatGPT MCP app is connected.

## Secure MCP Tunnel

On macOS the supported OpenAI tunnel client installation is:

```bash
brew install openai/tools/tunnel-client
```

Create a tunnel and a restricted runtime API key in OpenAI Platform. Put only the runtime key in a local mode-0600 file, then install the supervised tunnel:

```bash
python3 scripts/fleet_operator_macos.py install-tunnel \
  --tunnel-id tunnel_<32-hex> \
  --runtime-key-file ~/.config/chatgpt-cost-router/secrets/fleet-tunnel.key
```

The generated tunnel config refers to the key with `file:...`; neither the key nor its value is placed in the LaunchAgent plist. The tunnel forwards the `main` MCP channel to `http://127.0.0.1:8810/mcp` and keeps its health/UI loopback-only.

In ChatGPT, create/connect the custom app using **Connection: Tunnel** and select/paste the same tunnel ID.

## Important plan boundary

As of 2026-09-10, OpenAI documents full custom-MCP write/modify actions for ChatGPT Business and Enterprise/Edu. ChatGPT Pro can build Apps SDK apps and connect custom MCPs with read/fetch permissions, but full MCP write actions are not enabled. Therefore the direct SSH-write tools are implemented correctly but must not be claimed as callable from this Pro chat until product access changes or the account is in an eligible workspace.

The next section provides a compatibility lane that works with a ChatGPT context that already has GitHub write access.

## GitHub command relay for current ChatGPT contexts

`fleet_operator.relay` polls a dedicated `fleet/commands` branch. ChatGPT can write a bounded job with its existing GitHub connector; the supervised gateway executes the job through the same FleetRunner policy and pushes the sanitized result to deterministic branch `fleet/results/<job_id>`. This is not an arbitrary shell daemon: the job schema is versioned and action-limited, expires within 24 hours, and a local ledger rejects replay.

See `docs/FLEET_OPERATOR_RELAY.md` and `schemas/fleet-operator-job.schema.json`.

## Verification state

Local verification currently covers policy/config/SSH construction, root-command blocking, destructive authorization, root confinement, output/timeout bounds, parallel ordering, local transport, LaunchAgent/tunnel config redaction, job schema/expiry, relay replay protection and one local fake-bus execution. No live SSH/MCP/Tunnel call is claimed by these tests.
