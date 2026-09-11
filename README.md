# Chat-first Operations & Fleet Operator

Two independent products in the existing `bacoco/chatgpt-cost-router` repository.

| Product | Actual responsibility | Default execution |
| --- | --- | --- |
| **A — Chat-first Operations** | Read, analyze, edit, send, publish, coordinate and verify across authorized Gmail, GitHub, Cowboy and other connectors. | Native Chat tools; no automatic Work switch, extra coding agent or model API. |
| **B — Fleet Operator** | Access configured machines, execute named process profiles, supervise/cancel jobs, monitor progress and recover logs/results/artifacts. | Ordinary processes, independently of Chat; workers, mesh and inference are optional. |

**A is not an issue generator. B is not a Codex wrapper.** The deterministic cost
router remains a decision-support component, not either product's complete scope.

> **Implementation committed on the feature branch, not deployed to the fleet.**
> The code split, A workflows, B lifecycle, gateway, durable recovery and local
> enrollment/release tooling are implemented. The baseline is branch
> `feat/ab-products-20260911` at `cd897ddf3856ffdabef68ba1a71b43dd99efad46`.
> The delivery receipt distinguishes tests, simulations and unexecuted live gates.
> Source, tests and documentation are committed through the GitHub connector.
> Fresh local revalidation: **182 passed, zero failures/errors, one SDK test skipped**.
> **No main merge or deployment. T38 and real machine jobs remain paused.**

Start with [usage](docs/AB_USAGE.md), [architecture](docs/ARCHITECTURE.md),
[validation boundaries](docs/AB_VALIDATION.md) and [current status](.chatgpt/CURRENT.md).

## Implemented boundaries

| Package | Implementation |
| --- | --- |
| `chat_ops/` | Scoped action catalog, per-session capability observations, native tool driver, multi-step references, exact approvals, preflight/read-back, cancellation and read-only reconciliation, CLI and optional MCP interfaces. |
| `fleet_operator/jobs/` | Durable queue, fixed profiles, immutable Git snapshots, owned supervisors, progress/log bounds, deadlines, cancellation, result reconciliation, artifact checksums, node/job metrics. |
| `fleet_operator/enrollment/` | Exact-SHA release staging, manifest verification, explicit idle-node activation/rollback, drift-checked gateway enrollment, user-service definition generation. |
| `fleet_operator/` | Configured local/SSH gateway, bounded public command policy, typed node calls and a non-replaying durable relay/outbox. |
| `fleet_operator/workers/` | Optional legacy workers, account health, remote worker, mesh and macOS wrappers. These are not A/B core requirements. |
| `operation_contracts/` | Operator-owned project/resource/account grants, strict JSON, SQLite transactions, effect tokens, approvals and private receipts. Optional account reservations are separate from provider-reported quotas. |
| `cost_router/` | Deterministic decision engine plus import-identity aliases for old worker/mesh paths. |

### A: complete work through actual available tools

A workflow can read email, update a repository, publish through Cowboy, then send
an authorized report. Action descriptors are not newly granted connector access:
actual tool names, argument schemas, identities and permissions are discovered and
bound by the operator/Chat driver. An unavailable write remains unavailable.

`next` returns one exact invocation and a single-use token. The driver calls the
real connector once and `record` saves its actual return. Every write requires a
bound approval and a successful read-back before completion. A lost response is
**UNCERTAIN**, never permission to repeat a send or publication. `reconcile` can
only read; an explicit recovery read can recover a lost remote identifier.

Capabilities are scoped to principal, project, resource, action, account, surface
and session, with expiry. A new Chat cannot inherit a previous session's entitlement.
No claim is made that a subscription provides unlimited tools or free external services.

### B: ordinary processes, with or without Chat

Node configuration binds an operator principal to projects and named profiles.
Requests provide inputs, project/node/profile IDs and an idempotency key—not a shell,
arbitrary executable, account credential or working directory. A source request
uses a configured repository and exact Git SHA; the user's dirty checkout is not changed.

Local and SSH gateways expose typed submit/start/status/cancel/logs/result/events,
list, health and artifact tools. Enrollment can pin node, runtime and policy identity.
A result is not inferred from submission acceptance or a running supervisor.

`trusted-local` uses separate workspaces and clean environments, **not an OS sandbox**.
Container profiles generate pinned-image, no-network, read-only-root, resource-limited
commands and owned-container cleanup. Actual container-engine behavior still requires
host validation. Long-running services must remain foreground processes in their profile.

## Installation and entry points

Python 3.11 or newer. Install only the core for CLI/native-driver use:

```bash
python -m pip install .
chat-operations --help
fleet-jobs --help
fleet-enroll --help
```

MCP servers are optional; their dependency is pinned separately:

```bash
python -m pip install '.[mcp]'
python -m chat_ops.mcp_server --config /operator/chat.json --transport stdio
python -m fleet_operator.jobs.mcp_server --config /operator/node.json --transport stdio
fleet-gateway --config /operator/gateway.json --transport stdio
```

The core wheel includes canonical JSON schemas and routing policy. There is no
Docker, paid API, provider login or remote deployment step in installation.
Do not place private operator configuration, journals, logs or credentials in Git.

## Reproducible local demonstration

```bash
python scripts/ab_demo.py --directory /tmp/ab-demo-new-directory
python -m unittest discover -s tests -v
python scripts/validate_ab.py --output /tmp/ab-validation
```

The demo refuses an existing directory. Its **A connectors are simulated**, explicitly
labelled; B executes one real local Python process and returns a checksummed artifact.
No real email, GitHub write, WordPress publication, provider/model call or user fleet
job is performed. The output is a demonstration, not live connector certification.

## Explicit operational limits

The native receipt records what its caller observed; it is not an independent
cryptographic attestation. Resource policies and configuration files are operator
trust roots. A single server principal is not a public multi-tenant identity provider.
Use private stdio/loopback transport and separately configured authentication.

The bundled HTTP client uses a bounded legacy MCP initialization exchange and
operator-specified endpoint/account/tool bindings; it is not an OAuth onboarding
client or a claim that every connector exposes a directly reusable endpoint.
The optional official SDK transport test is skipped when the SDK is unavailable.

Legacy worker/prompt mesh interfaces remain private compatibility surfaces, not
new project-aware APIs. Public A/B paths do not automatically delegate to them.
Serena and PAIR remain optional evaluation candidates, not installed integrations.

[Roadmap](docs/ROADMAP.md) separates shipped code from remaining live acceptance gates.
[Decision specification](SPEC.md) continues to describe only the decision engine.
