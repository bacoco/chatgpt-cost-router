# Chat-first Operations & Fleet Operator

**Complete useful work from Chat. Run ordinary programs on your own machines. Keep evidence of what actually happened.**

This repository contains two independent products. Its historical name, `chatgpt-cost-router`, is retained: cost routing supports the products but does not define their whole purpose.

| Product | What it is for | What it adds |
| --- | --- | --- |
| **A — Chat-first Operations** | Read, analyze, edit, send, publish and verify through authorized Gmail, GitHub, Cowboy and other connectors. | Durable workflows, project/account permissions, exact approvals and recovery from uncertain results. |
| **B — Fleet Operator** | Run scripts, tests and foreground services on enrolled machines, with or without Chat. | Named process profiles, queueing, supervision, cancellation, logs, progress and verified result files. |

**A is not just an issue generator. B is not a Codex wrapper.** Neither core requires an extra model call. Connector/account permissions and service quotas still apply.

## Why use it?

An email can be sent even when its response is lost. A remote command can be accepted without finishing. A chat can lose the context needed to distinguish those states. This project records workflow and process state so those situations are not mistaken for success or permission to blindly repeat an action.

A can coordinate an authorized email-to-repository-to-publication workflow and verify each change. B can run tests on a configured Mac or Linux machine, expose progress, cancel the process and return the output with an integrity check. A can call B; connector-only work does not require a fleet, and fleet work does not require Chat.

The default preference is to use capabilities already available in Chat and ordinary local processes. Work, Codex, Claude, provider APIs, local inference, Serena and PAIR are optional choices, not hidden execution steps. This does not promise unlimited subscription quotas or free external services.

## Start from Chat

Read [deployment status](docs/DEPLOYMENT_STATUS.md) first: it identifies what is actually installed, verified or blocked. Then use this prompt with the authorized GitHub connector:

```text
Read README.md, .chatgpt/CURRENT.md and docs/DEPLOYMENT_STATUS.md from
bacoco/chatgpt-cost-router, main. My objective is: [describe the actual work].
Use the available native connectors to complete and verify that work, not merely
create an issue. Keep actions within the named project and account.
For machine work, use an enrolled Fleet profile and inspect completion, logs and
results. Follow docs/FLEET_OPERATOR_RELAY.md for the GitHub relay.
Do not switch to Work or invoke another model/API without explicit authorization.
Never repeat an uncertain send, publication or launch without reconciliation.
```

Native connector actions do not automatically become journalled A workflows. To use A's durable engine, attach its private MCP interface or operate its CLI/native-driver loop. The engine returns a tool instruction; the driver must call the real connector and record the real result. Installing a server is not the same as attaching it to a Chat account.

## Try the local example

Python 3.11+, Git and repository access are required:

```bash
git clone https://github.com/bacoco/chatgpt-cost-router.git
cd chatgpt-cost-router
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install .
python scripts/demo_ab.py --output /tmp/ab-first-demo
```

Use a fresh demo directory. A uses simulated connectors; B runs a real local process. The example does not contact your email, website or fleet. Never reuse its simulated capability observations as live authorizations. See the [examples](examples/).

## Find the right guide

| Need | Guide |
| --- | --- |
| What is really deployed, tested or blocked? | [Deployment status](docs/DEPLOYMENT_STATUS.md) |
| How do I install A, B or both? | [Installation](docs/INSTALLATION.md) |
| How do I operate workflows and jobs? | [A/B usage](docs/AB_USAGE.md) |
| How does the native GitHub connector reach machines? | [Fleet relay](docs/FLEET_OPERATOR_RELAY.md) |
| How is the code organized and protected? | [Architecture](docs/ARCHITECTURE.md) |
| What remains? | [Roadmap](docs/ROADMAP.md) |
| Which older documents are historical? | [Documentation index](docs/README.md) |

## Implementation map

`chat_ops/` owns A. `fleet_operator/jobs/` owns B's independent job service. `fleet_operator/` provides the guarded local/SSH gateway and durable relay. `fleet_operator/enrollment/` provides exact-revision staging and controlled activation. Owner-operated `scripts/ab_*` installers create separate user services only when explicitly invoked.

`operation_contracts/` owns project/resource/account grants and private journals. `fleet_operator/workers/` contains optional worker/mesh integrations. `cost_router/` retains deterministic routing and compatibility imports. [SPEC.md](SPEC.md) describes that decision engine, not the whole A/B product.

## Trust and evidence

A write needs authorization and read-back. Lost results remain uncertain; reconciliation reads evidence instead of repeating the write. B distinguishes acceptance, running state and a completed result. Retrieved artifacts must match the completion receipt.

`trusted-local` means trusted owner code in a separate workspace, **not an OS sandbox**. Container profiles require real-engine validation before accepting untrusted workloads. MCP servers bind to loopback and need a separately configured authenticated connection for external access.

Credentials, private host addresses, operator configuration and journals stay outside Git. Publish only sanitized deployment receipts. Historical experiment reports are evidence of those runs, not today's telemetry. **T38 remains paused; deployment does not resume quota-burning experiments.**
