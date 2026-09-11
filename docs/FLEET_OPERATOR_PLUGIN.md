# Fleet Operator — private SSH app for ChatGPT

Status: `RELAY LIVE / MCP SERVER LIVE — SECURE MCP TUNNEL + DIRECT CHATGPT APP ATTACHMENT PENDING`

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
- read mode is command-aware: interpreters/build tools are rejected and multi-purpose CLIs are constrained to known read-only subcommands/actions;
- direct root/admin commands are hard blocked;
- direct destructive commands require `allow_destructive=true`;
- filesystem reads/cwd are limited to locally configured roots;
- stdout/stderr are bounded and timeout is enforced;
- fan-out is bounded to 32 concurrent hosts;
- SSH targets, credentials and key material never appear in inventory results.

T37 validates the bounded read lane in live use. The write lane is not yet claimed strongly command-safe because shell/interpreter execution can bypass executable-level classification; separating that high-risk capability is the next hardening target.

## macOS gateway packaging

`requirements-fleet-operator.txt` pins the MCP SDK. The current SDK requires Python 3.10+. The installer discovers a compatible installed interpreter (including Homebrew Python), creates a private virtualenv and a per-user LaunchAgent, and never runs as root.

## Secure MCP Tunnel

The MCP server is prepared for an outbound OpenAI Secure MCP Tunnel and remains loopback-only. Direct custom-app attachment is separate from the already-working GitHub relay path.

## GitHub command relay for current ChatGPT contexts

`fleet_operator.relay` polls a dedicated `fleet/commands` branch. ChatGPT can write a bounded job with its existing GitHub connector; the supervised gateway executes it through FleetRunner and pushes a sanitized deterministic result branch `fleet/results/<job_id>`. Jobs are versioned, expire within 24 hours and are replay-protected locally.

See `docs/FLEET_OPERATOR_RELAY.md` and `schemas/fleet-operator-job.schema.json`.

## Verification state

Live evidence proves autonomous GitHub-relay execution on the gateway MacBook and remote machines over SSH/Tailscale. T37 adds command-aware read semantics and durable worker-auth quarantine; the full repository suite passed 100 tests. In live verification, `exec_read` blocked interpreter-based mutation while preserving safe `git status`, and a real Codex authentication failure quarantined a worker so the mesh advertised it `ready=false`. Secure MCP Tunnel and a direct ChatGPT MCP invocation remain untested.
