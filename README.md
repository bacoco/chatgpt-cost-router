# Chat-first Operations & Fleet Operator

**Complete useful work from Chat. Run ordinary programs on your own machines. Keep evidence of what actually happened.**

This repository contains two independent products. Its historical name, `chatgpt-cost-router`, is retained; cost routing is a supporting component, not the whole application.

| Product | What it is for | What it adds |
| --- | --- | --- |
| **A — Chat-first Operations** | Read, analyze, edit, send, publish and verify through authorized Gmail, GitHub, Cowboy and other connectors. | Durable workflows, project/account permissions, exact approvals and recovery from uncertain external results. |
| **B — Fleet Operator** | Run scripts, tests and foreground services on enrolled machines, with or without Chat. | Named process profiles, queueing, supervision, cancellation, logs, progress and verified result files. |

**A is not just an issue generator. B is not a Codex wrapper.** Neither core requires an extra model call. Actual connector and account permissions still apply.

## Why use it?

An email can be sent even when its response is lost. A remote command can be accepted without finishing. A chat can lose the context needed to distinguish those states. This project records workflow and process state so those situations are not mistaken for success or permission to blindly repeat an action.

For example, A can coordinate an authorized email-to-repository-to-publication workflow and verify each change. B can run tests on a configured Mac or Linux machine, expose progress, cancel the process and return the output with an integrity check. A can call B, but connector-only work does not require a fleet and fleet work does not require Chat.

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
Never repeat an uncertain send, publication or process launch without reconciliation.
```

Native connectors do not automatically become journalled A workflows. To use A's durable engine, attach its private MCP interface or operate its CLI/native-driver loop. The engine returns a tool instruction; the driver must call the real connector and record the real result. Installing a server is not the same as attaching it to a Chat account.

## Try the local example

Python 3.11+ and Git are required. Repository access is required to clone it.

```bash
git clone https://github.com/bacoco/chatgpt-cost-router.git
cd chatgpt-cost-router
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install .
python scripts/ab_demo.py --directory /tmp/ab-first-demo
```

Use a new demo directory. A is explicitly `SIMULATED_CONNECTORS`; B is a `REAL_LOCAL_PROCESS`. Both should reach `SUCCEEDED`. The example does not contact your email, website or fleet. Never reuse its simulated capability observations as live authorizations.

## Find the right guide

| Need | Guide |
| --- | --- |
| What is really deployed, tested or blocked? | [Deployment status](docs/DEPLOYMENT_STATUS.md) |
| How do I install A, B or both? | [Installation](docs/INSTALLATION.md) |
| How do I operate workflows and jobs? | [A/B usage](docs/AB_USAGE.md) |
| How does a Chat GitHub connector reach the machines? | [Fleet relay](docs/FLEET_OPERATOR_RELAY.md) |
| How is the code organized and protected? | [Architecture](docs/ARCHITECTURE.md) |
| What remains to do? | [Roadmap](docs/ROADMAP.md) |
| Which older documents are historical? | [Documentation index](docs/README.md) |

## Implementation map

`chat_ops/` owns A. `fleet_operator/jobs/` owns B's independent job service. `fleet_operator/` provides the guarded local/SSH gateway and durable relay. `fleet_operator/enrollment/` provides exact-revision staging and controlled activation. The owner-operated `scripts/ab_*` tools install separate user services only when explicitly invoked.

`operation_contracts/` owns project/resource/account grants and private journals. `fleet_operator/workers/` contains optional historical worker and mesh integrations. `cost_router/` retains deterministic routing and compatibility imports. [SPEC.md](SPEC.md) describes that decision engine, not the whole A/B product.

## Trust and evidence

A write needs authorization and read-back. Lost results remain uncertain; reconciliation reads evidence instead of repeating the write. B distinguishes queue acceptance, running state and a completed result. Retrieved artifacts must match the completion receipt.

`trusted-local` means trusted owner code in a separate workspace, **not an operating-system sandbox**. Container profiles require separate real-engine validation before accepting untrusted workloads. MCP servers bind to loopback and need a separately configured authenticated connection for external access.

Private host addresses, credentials, operator configuration and journals stay outside Git. Publish only sanitized deployment receipts. Historical experiment reports are evidence of those runs, not today's telemetry. **T38 remains paused; deployment does not resume quota-burning experiments.**
