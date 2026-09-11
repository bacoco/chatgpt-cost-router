# Chat-first Operations & Fleet Operator

Two independent products in the historical `chatgpt-cost-router` repository.

| Product | Purpose | Default execution |
| --- | --- | --- |
| **A — Chat-first Operations** | Complete authorized work from normal Chat across Gmail, GitHub, WordPress/Cowboy and other available connectors. | Chat reasons, invokes its actual tools, acts and verifies; no automatic Work switch or additional coding-agent/model API. |
| **B — Fleet Operator** | Access enrolled machines, run ordinary processes, supervise their lifecycle and retrieve verified results. | Processes and services; coding agents, placement and local inference are optional. |

**A is not limited to issues or specifications. B does not require a second LLM.**

> **Delivery status — 11 September 2026:** implementation available for code review
> on `fix/ab-delivery-reconciled-20260911`. The local automated suite passed
> **168 tests** against the delivered runtime revision; **77 published files**
> were compared by Git blob hash, with no mismatch. This is not a production,
> installed-SDK or owner-fleet validation. No deployment or scheduler change was
> performed by this delivery. See the [delivery report](docs/AB_DELIVERY_RECONCILED_2026-09-11.md)
> and [current checkpoint](.chatgpt/CURRENT.md).

## A — Complete work from Chat

A supports authorized read, search, edit, commit, draft, send, publish and
cross-connector workflows. For example: read permitted mail, update the correct
repository or site, verify it, then send the requested report. Native connector
actions are the primary path; submitting a machine task is optional.

The runtime in `chat_ops/` supplies a catalog, explicit project/resource/account
bindings, durable workflows, exact-input approvals, scoped capability evidence,
read-back verification and recovery without replaying uncertain writes.

Capabilities are scoped to principal, project, resource, action, surface and
conversation session. Tool visibility is not successful invocation. A new chat
must observe its tools again. Configuration does not grant access to a connector
that is absent or denied in the current conversation.

Native mode returns the next exact tool invocation. Chat executes its existing
connector and records the actual output. Those records are **caller-observed**,
not independently authenticated provider receipts. Alternatively, an operator
can configure a direct MCP endpoint for a resource/account. There is no hidden
extra LLM call in either driver.

Gmail, Cowboy and other provider implementations remain external connectors,
not replacements implemented by this repository. Use Cowboy for WordPress;
do not substitute WPVibe. Serena and PAIR are optional, unintegrated candidates,
not prerequisites for completing authorized work.

## B — Execute, supervise and retrieve results

The independent `fleet_operator/jobs/` runtime provides project-bound submission,
start, status, progress, bounded logs, cancellation, deadlines, terminal results,
artifact retrieval, events and reconciliation. Named profiles and host/runtime
bindings are operator-owned; requests cannot supply arbitrary shell commands,
a new principal or unapproved working directories.

Each run gets a separate workspace. Repository jobs use an immutable source SHA
without switching or cleaning the user's existing checkout. A durable claim
precedes execution. A lost supervisor heartbeat becomes `UNCERTAIN`, not permission
to repeat the task. An uncertain result is reconciled from the exact receipt.

Artifact retrieval verifies the receipt, run identity, manifest, file size and
whole-file SHA-256. File paths are opened without following symlinks; hard links
and changed files are rejected. Chunks are at most 64 KiB; artifacts at most
16 MiB. Both `data_base64` and the compatibility field `data` contain the same
base64 chunk; `chunk_sha256` verifies that chunk. Full artifact bytes use the
private node/CLI/MCP path, not the GitHub relay.

The gateway resolves enrolled aliases and verifies configured node/revision
identities. It uses bounded process transport and a restricted command policy.
**Legacy raw write and Git-pull endpoints are now inspection-only or blocked:**
mutations require an operator-enrolled process profile. Existing services must
not be upgraded blindly under assumptions from the old broad write lane.

The relay persists execution intent and results separately from publication.
A failed publication retries delivery, including after the source job disappears,
without rerunning the machine operation. `ACCEPTED` means queued/running, not done.

Metrics are observations, not guesses. Linux direct-process CPU/RSS readings are
not aggregate container/GPU metrics; unavailable observations remain unknown.

## Shared boundaries and safety

`operation_contracts/` supplies strict bounded JSON, project grants, a durable
journal and operator budgets. Machines, projects, GitHub identities and provider
accounts are separate. Provider quotas are not inferred from the number of workers;
operator budget observations are not automatic provider quota telemetry.

**Private operator-controlled use only.** `trusted-local` is not an OS sandbox
for hostile workloads. Container controls and owned-container cleanup exist in
code but were not qualified against a real engine by this delivery. The configured
principal and session identifiers are not a public multi-tenant authentication
system. Keep credentials out of requests, logs and GitHub receipts.

No claim is made that Chat subscriptions, connectors or machines are unlimited
or universally free. The economic priority is to avoid unnecessary additional
model calls, not to conceal them behind another tool.

## Entry points and development checks

For native A work, use normal Chat with the task's actual connectors. No Fleet
or GPU installation is required. The [Chat-first skill](skills/chat-first-operations/SKILL.md)
and [project bootstrap prompt](docs/PROJECT_BOOTSTRAP_PROMPT.md) describe that lane.

For developers, from a checkout with the documented dependencies available:

```bash
python -m chat_ops --help
python -m fleet_operator --help
python -m unittest discover -s tests -v
python scripts/ab_demo.py --directory /tmp/ab-demo-new-directory
```

The demo requires a **new directory**. Its Gmail/GitHub/Cowboy actions are explicitly
simulated; B really runs a local process producing `42`. It sends no real mail and
publishes no real site. The integration tests additionally exercise A driving B
and retrieving the verified file.

Optional MCP entry points are `chat_ops.mcp_server`,
`fleet_operator.jobs.mcp_server` and `fleet_operator.mcp_server`. They require the
optional SDK. HTTP remains loopback/private. An HTTP test fixture is not proof
that the official SDK or Chat custom-app attachment works on an installed host.

Enrollment, immutable runtime activation and packaging code is present under
`fleet_operator/enrollment/` and the repository packaging files. Those operations
were preserved, **not executed or certified by this reconciliation**. Do not
interpret installation recipes as authorization to restart paused services.

## Layout and evidence

| Area | Responsibility |
| --- | --- |
| `chat_ops/` | A workflows, native driver, optional MCP transport and interface |
| `fleet_operator/jobs/` | B ordinary-process lifecycle, monitoring and artifacts |
| `fleet_operator/` | Gateway, bounded transport, relay and host access |
| `fleet_operator/workers/` | Retained optional worker/mesh implementations |
| `cost_router/` | Decision support and backward-compatible worker import aliases |
| `operation_contracts/` | Shared project contracts, journal, private records and budgets |

Historical test receipts and architecture reviews remain available; they are dated
snapshots, not current fleet telemetry. Start with the [reconciled delivery report](docs/AB_DELIVERY_RECONCILED_2026-09-11.md)
for this version and the [historical validation status](docs/VALIDATION_STATUS_2026-09-11.md)
for earlier experiments. T38, new installations and the stopped quota-burn
experiment have not been resumed by this delivery.
