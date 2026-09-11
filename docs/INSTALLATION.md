# Install and deploy A/B

Read [deployment status](DEPLOYMENT_STATUS.md) before changing an existing installation. Installing code, configuring private policy, starting services and attaching a Chat account are separate operations.

## Local installation

Use Python 3.11+ and a private virtual environment:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install .
chat-operations --help
fleet-jobs --help
fleet-enroll --help
```

MCP is optional and pinned separately:

```bash
python -m pip install '.[mcp]'
```

The ordinary A/B core does not require Codex, Claude, Docker or an LLM API account. Installation can download Python packages; `pyproject.toml` is the dependency authority.

## Working example and tests

```bash
python scripts/ab_demo.py --directory /tmp/ab-new-demo
python -m pip install -r requirements-dev.txt
python scripts/validate_ab.py --output /tmp/ab-validation
```

The demo's A connectors are simulated; B actually runs a local process. Do not reuse simulated observations as real permissions. An existing demo directory is refused. Full source validation requires the tracked `skills/` metadata as well as code and tests.

## Real policy and access

Keep project registries, `chat.json`, `node.json`, gateway configuration and journals outside Git with private permissions. A project names members, resources, accounts, actions, nodes and profiles. A node profile fixes its executable, arguments, timeout, output bounds and artifacts. Requests supply structured inputs, not shell commands or credentials. See [usage](AB_USAGE.md).

```bash
python -m chat_ops.mcp_server --config /operator/chat.json --transport stdio
python -m fleet_operator.jobs.mcp_server --config /operator/node.json --transport stdio
fleet-gateway --config /operator/gateway.json --transport streamable-http --port 8813
```

These are private server examples, not external authentication setup. Separately configure a supported authenticated connection/tunnel and discover actual tools in the current Chat account/session. Never expose the raw loopback server publicly as an authentication shortcut.

## Owner-operated fleet deployment

The installer only accepts aliases already present in the private gateway configuration. It retains SSH host-key checks, does not use root, does not copy credentials and does not switch the owner's working checkout. It transfers an exact Git revision with an archive integrity check.

```bash
python scripts/ab_fleet_deploy.py \
  --repo /operator/existing-repository \
  --revision FULL_40_CHARACTER_COMMIT \
  --gateway-config /operator/legacy-gateway.json \
  --hosts macbook,macstudio
```

This performs a real installation beneath `~/.local/share/chatgpt-cost-router/ab/`. It installs the package, tests process completion, verified artifact retrieval and cancellation, then creates new user services. The local gateway also installs A's MCP service and runs the full test suite. Inspect each node result: a successfully executed rollout command can still contain blocked nodes.

Default profiles are `smoke` and `validate-release`, not arbitrary command execution. Enroll explicitly approved profiles for application-specific workloads.

After verified node receipts exist:

```bash
python scripts/ab_gateway_activate.py \
  --rollout /operator/ab/rollout.json \
  --legacy-config /operator/legacy-gateway.json \
  --repo /operator/existing-repository
```

This creates separate gateway/relay policy, pins node runtime/policy identities, installs new services and tests local MCP discovery and node health. The branch `fleet/ab-commands` must exist. It differs from the historical relay queue; do not submit an operation to both.

## Service ownership and recovery

New labels are `pro.chatgpt-cost-router.ab-node`, `.ab-chat`, `.ab-gateway` and `.ab-relay`, depending on host role. macOS uses LaunchAgents in the operator's login session; Linux uses user systemd. Old mesh, worker, gateway and relay services are not replaced by this installer.

The installer refuses differing existing configuration/service definitions. Before an upgrade, drain jobs and reconcile uncertain outcomes; retain the old revision/configuration and explicitly stop only the affected A/B service. Do not kill unrelated processes. `fleet-enroll stage/verify/activate` provides a separate checked idle-node activation path; selecting an older staged SHA is its rollback operation.

A startup acknowledgement is not proof of a healthy service. Inspect its state, private logs, MCP health and a real completed job. Startup does not prove persistence across logout or reboot. Deployment receipts/logs live in the private `ab/` directory; publish only sanitized summaries.
