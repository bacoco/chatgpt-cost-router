# Install and deploy A/B

Read [deployment status](DEPLOYMENT_STATUS.md) before changing an existing installation. Installing code, configuring policy, starting services and attaching a Chat account are separate operations.

## Local installation and first run

Use Python 3.11+ in a private virtual environment, from the repository root:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install .
chat-operations --help
fleet-jobs --help
fleet-enroll --help
python scripts/ab_demo.py --directory /tmp/ab-new-demo
```

A's demo connectors are simulated; B actually runs a local process. Use a fresh directory. MCP is optional: install `python -m pip install '.[mcp]'` to run private MCP servers. The core does not require Codex, Claude, Docker or an LLM API account. Installation can download packages; `pyproject.toml` is the dependency authority.

For source validation:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_ab.py --output /tmp/ab-validation
```

The source bundle must include tracked `skills/` metadata as well as code and tests. Do not suppress missing-file failures to declare a release successful.

## Real policy and access

Keep projects, `chat.json`, `node.json`, gateway configuration and journals outside Git with private permissions. A project names members, resources, accounts, actions, nodes and profiles. A node profile fixes its executable, arguments, timeout, output bounds and artifacts. Requests supply structured inputs, not arbitrary shell commands or credentials. Read [usage](AB_USAGE.md) and the [examples](../examples/).

```bash
python -m chat_ops.mcp_server --config /operator/chat.json --transport stdio
python -m fleet_operator.jobs.mcp_server --config /operator/node.json --transport stdio
fleet-gateway --config /operator/gateway.json --transport streamable-http --port 8813
```

Separately configure an authenticated connection/tunnel and discover actual tools in the current Chat account/session. Never expose the raw loopback server publicly as an authentication shortcut. The native GitHub relay is an alternative for fleet access; it does not automatically attach A's MCP app to Chat.

## Owner-operated fleet deployment

The installer accepts only aliases already present in private gateway configuration, keeps SSH host-key checks, does not use root or copy credentials, and does not switch the owner's checkout. It transfers an exact revision and checks the archive hash.

```bash
python scripts/ab_fleet_deploy.py \
  --repo /operator/existing-repository \
  --revision FULL_40_CHARACTER_COMMIT \
  --gateway-config /operator/legacy-gateway.json \
  --hosts macbook,macstudio
```

This is a real installation beneath `~/.local/share/chatgpt-cost-router/ab/`. It installs the package, tests completion, verified artifact retrieval and cancellation, then creates new user services. The local gateway also installs A's MCP service and runs the full suite. Inspect each node result: a rollout command can finish successfully while reporting blocked nodes.

Initial profiles are `smoke` and `validate-release`. Enroll explicitly approved profiles for application-specific workloads. The current owner gateway activation helper expects its local alias to be `macbook`; it is not a universal zero-configuration installer.

After verified node receipts exist:

```bash
python scripts/ab_gateway_activate.py \
  --rollout /operator/ab/rollout.json \
  --legacy-config /operator/legacy-gateway.json \
  --repo /operator/existing-repository
```

This creates separate gateway/relay policy, binds node identities/revisions, installs new services and verifies local MCP discovery and node health. `fleet/ab-commands` must exist. It differs from the historical relay queue; do not submit an operation to both.

## Service ownership, upgrade and recovery

New labels are `pro.chatgpt-cost-router.ab-node`, `.ab-chat`, `.ab-gateway` and `.ab-relay`, depending on role. macOS uses LaunchAgents in the operator's login session; Linux uses user systemd. Old mesh, worker, gateway and relay services are not replaced.

The installer refuses differing existing configuration/service definitions. Before upgrading, drain jobs and reconcile uncertain outcomes, retain the old revision/configuration and explicitly stop only the affected A/B service. Do not kill unrelated processes. `fleet-enroll stage/verify/activate` provides a separate checked idle-node activation path; selecting an older staged SHA is its rollback operation. Activation alone does not reload services.

A startup acknowledgement is not service health. Inspect state, private logs, MCP health and a real completed job. Startup does not prove persistence across logout or reboot. Private receipts/logs live under `ab/`; publish only sanitized summaries. The targeted `ab_complete_assets.py` helper repairs the two omitted skill documents of the initial deployment from its exact Git revision, without changing runtime code.
