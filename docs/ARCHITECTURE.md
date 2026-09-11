# Architecture — A/B responsibilities and implementation review

Status: documentation-only review; no runtime refactor or deployment.
Reviewed source: `18c36ea51e970659d7a30eed7d9330c38a395cea` on
`bacoco/chatgpt-cost-router/main`. Later documentation commits do not change the
runtime analyzed here. Product scope is defined in the
[A/B decision](TWO_PROJECTS_AND_PAIR_2026-09-11.md).

## Independent products

**A — Chat-first Operations** completes authorized work from normal Chat through
Gmail, GitHub, WordPress/Cowboy and other apps: read, reason, edit, send, publish,
coordinate and verify. It is neither issue-only nor code-only. Direct connector
actions are the primary lane. Work, another coding agent and paid model APIs are
not default dependencies. Serena is an optional tool, not the product.

**B — Fleet Operator** provides machine access, process execution/management,
supervision, monitoring and results. Distribution is optional. Ordinary tasks do
not require an LLM. B must also serve CLI/API/other clients independently of Chat.

A can call B when machine execution is needed. Chat reasoning, connector access,
machine transport, process supervision and optional model delegation are distinct
roles. MCP is an interface choice; it does not itself provide project isolation,
provider budgets or durable job management.

## Current code ownership, not new directories

| Actual source | Logical owner | What exists |
| --- | --- | --- |
| `skills/`, `.chatgpt/`, project-workflow docs | A / shared | Repository-backed workflow instructions, project checkpoints and handoff conventions |
| `cost_router/__main__.py`, `router.py`, `capabilities.py`, `validation.py` | Decision support used by A / shared | Deterministic recommendation and scoped-evidence validation; no app or remote execution in the CLI |
| `policy/routing.json`, `schemas/`, `cost_router/handoff.py` | Shared | Versioned routing and delegation contracts; these are not yet the universal A/B job contract |
| `cost_router/ledger.py` | Shared building block | Local SQLite operation claims/state; not automatically adopted by every adapter |
| `fleet_operator/core.py` | B | Local/SSH execution by host alias, command checks, path/cwd checks, timeouts and output caps |
| `fleet_operator/mcp_server.py` | B interface | Host inventory/status, file read, read/write command fan-out, Git status/pull and local relay-result tools |
| `fleet_operator/relay.py` | B transport | GitHub job polling, local result files and deterministic result branches |
| `fleet_operator/macos.py`, `scripts/fleet_operator*.py` | B packaging | Gateway, relay and intended tunnel installation/entry points |
| `cost_router/workers.py`, `worker_budget.py`, `worker_health.py` | B optional model adapter | Codex dispatch, budget-aware choice, telemetry and auth quarantine |
| `cost_router/remote_worker.py`, `mesh.py`; remote-worker/mesh scripts | B optional model-routing extension | Tailscale-facing Codex endpoints, node heartbeat/TTL and cross-node dispatch |
| `cost_router/macos_launchd.py`, `scripts/macos_mesh_service.py`, `scripts/mesh_service_runner.py` | B supervision | macOS service installation and restart supervision |
| `tests/`, receipts and dated validation documents | A / B / shared evidence | Recorded checks with scoped limitations, not live monitoring |

**Physical separation is incomplete.** The historical `cost_router` package mixes
decision/contracts with B's worker and mesh implementation. The existing MCP
server is a Fleet interface, not a universal host for Gmail/GitHub/Cowboy.
Those apps supply their own integrations outside this repository.

## Implemented execution paths

```text
A: user -> Chat -> authorized app action -> external result verification
                          |
                          | optional machine execution
                          v
B: Fleet MCP or GitHub relay -> FleetRunner -> local process / SSH process

B model extension:
client -> mesh control -> chosen remote-worker endpoint -> Codex CLI
```

The first path is driven by the client and its actual tools, not by a standalone
Python orchestration loop in this repository. Only invoke actions that are
available and authorized in the current context.

The second path has historical relay/SSH evidence. The local MCP server and its
direct ChatGPT attachment are separate verification steps. Do not infer a blanket
plan restriction or guaranteed write capability from either the transport or a
past observation in another surface.

The third path **does invoke another model**. It is an optional B adapter, not a
requirement for A. The implemented worker registry accepts `codex-exec`; Claude,
PAIR and other-provider adapters are not implemented by this architecture review.

## Concrete gaps found in the reviewed implementation

| Observation in current source | Consequence for the A/B split |
| --- | --- |
| `dispatch_mesh` accepts `worker` and `prompt`, not a project/run envelope. | Do not describe the mesh as a project-aware general process API. |
| Relay actions are `status`, `read_file`, `exec_read`, `exec_write`, `git_pull`. | A unified submit/status/progress/logs/cancel/result lifecycle is still a target. |
| Relay's `status` executes `uname`; worker probes read local login/quarantine state. | Host reachability and cheap auth probes do not establish task progress or valid end-to-end service. |
| `worker_health.py` persists auth-failure quarantine. | Preserve this protection; no permanent live-health guarantee follows from one PASS. |
| A relay result is saved locally before push, but the completed ledger is marked only after result publication. | Publish failure or interruption can leave executed work unmarked; recovery/idempotency must be hardened before replay guarantees are claimed. |
| The SQLite operation ledger and Fleet relay ledger are different implementations. | A good shared contract is not proof that the relay enforces its uncertain-outcome semantics. |
| Path/cwd checks are lexical; broad write commands can invoke interpreters. | T37 is targeted hardening, not filesystem/tenant isolation or complete write safety. T38 remains unfinished. |
| Budgets are observed per worker; no unified account/project registry is enforced across all endpoints. | Cross-project/account permissions and quota aggregation still need design and implementation. |

This is a source-level scope/coupling review, not a comprehensive security audit.
No unit tests, host commands or live connector workflows were run to revalidate
these historical runtime claims during the documentation update.

## Proposed shared contract — not implemented everywhere

Requests should bind requester identity, explicit project/task context, operation
profile, inputs, allowed resources, deadline and idempotency key. Add repository
owner/name and immutable base SHA for code-related work. Model delegation adds an
explicit account reference, usage class and budget; never credentials.

Results should bind run identity, lifecycle state, node/workspace/software version,
exit status, bounded diagnostics, artifact references and verification evidence.

A mail task need not invent a Git repository. A machine may serve many projects.
OS identity, connector/GitHub identity and provider account are separate.
Repository instructions cannot grant additional service permissions. Do not share
a mutable global active project between chats. Aggregate provider budgets across
machines/projects by account rather than pretending each worker owns a new quota.

## Migration boundaries

Keep one repository and existing import paths during the strategic pause.
A later approved refactor can separate workflow/connector-facing logic, shared
contracts and B runtime modules behind compatibility facades. Update imports,
entry points and tests together; do not move files merely to make the tree look split.

Retain the GitHub relay as a transitional/fallback B transport, not an A dependency.
Assess PAIR only for the local-inference extension and Serena only where targeted
code operations add value. Neither is installed or adopted by this review.

Historical proofs remain in [VALIDATION_STATUS_2026-09-11](VALIDATION_STATUS_2026-09-11.md).
The [roadmap](ROADMAP.md) separates A, B and shared acceptance categories.
The [engine specification](../SPEC.md) and [routing algorithm](ROUTING_SPEC.md)
retain the implemented deterministic invariants.
