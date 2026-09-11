# Chat-first Operations & Fleet Operator

This repository, historically named **ChatGPT Cost & Capability Router**, serves
**two independent needs**. They can cooperate, but neither requires the other.

| Product | Purpose | Default execution |
| --- | --- | --- |
| **A — Chat-first Operations** | Complete authorized work from normal Chat across Gmail, GitHub, WordPress/Cowboy and all other available apps/connectors. | Chat reasons, invokes tools, acts and verifies; no Work switch or additional coding-agent/model-API call by default. |
| **B — Fleet Operator** | Access machines, launch processes, manage their lifecycle, monitor progress/resources and retrieve results. | Ordinary processes and services; placement, coding agents and local inference are optional capabilities. |

**A is not limited to creating issues, preparing specifications or handing work to
another agent. B is not limited to running Codex or distributing GPU inference.**

> **Current state: documentation-aligned strategic pause.** The A/B responsibilities
> are defined; the physical code split and full product implementation are not
> complete. T38 and new deployments remain paused. Historical validation is recorded
> through T37; this README update is not a new live test or deployment authorization.
> Start with [CURRENT](.chatgpt/CURRENT.md), the
> [A/B decision](docs/TWO_PROJECTS_AND_PAIR_2026-09-11.md) and the
> [implementation map](docs/ARCHITECTURE.md).

## A — Complete work from Chat and its tools

The economic priority is to use the capability already included in Chat and avoid
unnecessary additional Work/Codex/Claude/model-API usage. This is a routing objective,
not a promise of unlimited usage or zero cost for every connector and machine.

| Connected system | Intended authorized operations |
| --- | --- |
| Gmail | Search/read messages, prepare and verify drafts, send requested mail and verify the result. |
| GitHub | Read/analyze repositories, edit files, commit, manage branches/issues/PRs, perform authorized merges and verify exact state. |
| WordPress through Cowboy | Read, edit and publish content, then verify the resulting site. Do not substitute WPVibe. |
| Other apps/connectors | Use their actual document, calendar, contact, search, publishing and other capabilities. |
| Cross-app workflows | Carry the correct task/project context across systems, execute authorized steps and verify each external effect. |

For example: read permitted emails, analyze their information, update a repository
or website, and send a verified report. Direct connector actions are the primary
lane; a machine task is optional. An issue is only one possible output.

Capabilities must be checked per **action, account/resource, surface and session**.
ChatGPT.com Chat, Codex Mac Chat, Work, CLI and Scheduled Tasks are distinct contexts.
Visible tools are not automatically invocable or verified. Reuse historical receipts
without turning a success or denial on one surface into a universal product claim.
See the [surface map](docs/SURFACE_CAPABILITY_MAP.md) and
[capability contract](docs/CAPABILITIES.md).

The repository supplies workflow skills, scoped evidence, handoffs and a
deterministic decision engine. Gmail, Cowboy and other app implementations are
external integrations, not newly implemented adapters in this repository.
Serena is an **optional** code-context/editing tool to evaluate, not A's foundation.

## B — Machine access, execution and monitoring

B owns machine enrollment/access, authorization, execution, supervision, monitoring
and results. A can use it as a tool; a CLI, API or another authorized client must
also be able to use it without Chat. No second LLM is required for an ordinary task.

```text
A: Chat + authorized apps --------> Gmail / GitHub / Cowboy / other systems
          |
          | optional scoped machine task
          v
B: Fleet Operator <--------------- CLI / API / other authorized clients
          |
          +--> tests, builds, scripts and supervised services
          +--> optional Codex / Claude adapters
          +--> optional local inference, with PAIR as a candidate
```

The diagram is the product boundary, not a claim that every adapter is implemented.
The existing Fleet gateway provides local/SSH command execution, an MCP server,
a GitHub relay, bounded outputs and macOS packaging. Separate worker modules add
Codex dispatch, Tailscale endpoints, heartbeat discovery and auth quarantine.

**B is still a prototype, not a complete multi-tenant job platform.** Host reachable,
supervisor loaded, process running, progress observed, job complete and result
verified are distinct states. General durable job lifecycle/cancellation,
project isolation and resource monitoring still need consolidation.

T37 added command-aware read checks and worker-auth quarantine; it did not prove
a complete OS sandbox. Broad write execution and relay recovery after uncertain
effects remain open risks. Do not expose the gateway publicly or to untrusted users.
The direct ChatGPT MCP attachment is not yet a recorded live PASS; GitHub relay
proof is a separate transport result. Client/workspace permissions must be verified,
not inferred from a blanket Pro read-only claim.

PAIR is a candidate for **local inference routing**, not a replacement for general
process management or subscription-account routing. Neither PAIR nor Serena has
been integrated by this review. See the [comparison](docs/TWO_PROJECTS_AND_PAIR_2026-09-11.md).

## Multiple projects, machines and accounts

Do not equate a machine with a project, GitHub identity or model-provider account.
A request must carry explicit project/task context; repository and immutable SHA
apply when code is involved, not to every email. Concurrent chats must not share a
mutable global "active project". Permissions come from the authorized service,
not from instructions that a repository grants itself.

The proposed A/B contract includes requester, context, operation, inputs, allowed
resources, deadline/idempotency key and optional account/budget reference. Results
include run identity, status, diagnostics and evidence. **This unified contract is
a design target**, not an already-enforced field set in every runtime adapter.

Keep credentials out of requests and repository receipts. Aggregate provider usage
per account across machines/projects; do not count each worker as a separate quota.
Quota observations remain unknown when unavailable. Additional-model use must be
explicit rather than hidden inside a connector or remote process.

## Start with the appropriate entry point

**For A:** use normal Chat with the connectors required by the task. No Fleet,
Codex or GPU installation is required for connector-only work. For a GitHub-backed
project, use [PROJECT_BOOTSTRAP_PROMPT](docs/PROJECT_BOOTSTRAP_PROMPT.md) and
[PROJECT_BOOTSTRAP_PROTOCOL](docs/PROJECT_BOOTSTRAP_PROTOCOL.md).
That kit is the GitHub-project lane, not a prerequisite for mail or other app tasks.

[INSTALLATION_KIT_INDEX](docs/INSTALLATION_KIT_INDEX.md) covers the project workspace
and supported launcher/handoff setup. Scheduled Tasks are optional where available.
A [Codex handoff](docs/CHATGPT_TO_CODEX_HANDOFF.md) is an explicit escalation for a
real capability boundary, not the automatic next step after Chat.

**For B:** review [FLEET_OPERATOR_PLUGIN](docs/FLEET_OPERATOR_PLUGIN.md),
[FLEET_OPERATOR_RELAY](docs/FLEET_OPERATOR_RELAY.md) and the
[roadmap](docs/ROADMAP.md) before deployment. The relay is a transitional/fallback
transport, not a mandatory route for Gmail, GitHub or Cowboy operations in A.
Existing installation/run recipes are not an instruction to resume paused services.

## Existing implementation and physical layout

| Area | Current location | Responsibility |
| --- | --- | --- |
| Chat project workflows and optional delegation | `skills/`, `.chatgpt/`, workflow docs | A and shared handoff conventions |
| Cost/capability recommendation and validation | `cost_router/router.py`, `capabilities.py`, `validation.py`, `__main__.py` | Decision support; does not itself invoke Chat apps or machines |
| Versioned policy, schemas and local operation state | `policy/`, `schemas/`, `cost_router/handoff.py`, `cost_router/ledger.py` | Shared building blocks |
| Machine access, MCP, relay and packaging | `fleet_operator/`, `scripts/fleet_operator*.py` | B |
| Codex broker, budgets, health, remote endpoints, mesh and supervision | Worker/mesh modules in `cost_router/` and `scripts/` | B; still physically mixed into the historical package |
| Durable test evidence | `.chatgpt/test-receipts/`, dated validation documents | Historical action-scoped proofs, not current fleet telemetry |

The [architecture review](docs/ARCHITECTURE.md) maps the real modules and remaining
coupling. The [engine specification](SPEC.md) describes that component, not the
whole A/B product. No module, import path or CLI was renamed during this review.

## Local deterministic example — not a fleet/model call

Use Python 3.11+ for the documented development setup, from this checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m cost_router route examples/request.json --at 2026-09-05T00:30:00Z
python3 -m cost_router validate handoff examples/handoff.json
python3 -m unittest discover -s tests -v
```

These are opt-in development instructions, not commands executed by this review.
Fixtures and prices are synthetic. `--at` replays fixture time; real decisions need
fresh observations. The CLI recommends/validates without launching a surface.
Exit codes are `0` valid/routed, `2` invalid input and `3` blocked.
See [ROUTING_SPEC](docs/ROUTING_SPEC.md) and [EXECUTION_PROTOCOL](docs/EXECUTION_PROTOCOL.md).

## Evidence, skills and next work

Use [VALIDATION_STATUS_2026-09-11](docs/VALIDATION_STATUS_2026-09-11.md) for the
authoritative historical snapshot. T14-alt's Gmail proof belongs to Codex Mac Chat
with built-in Gmail, not automatically to a scheduled Developer-MCP lane.
T35B-T37 record relay/SSH, multinode dispatch and hardening proofs, not complete
product certification or a guarantee that the fleet is currently online.

Five canonical skills live in `skills/`: `capability-router`, `surface-handoff`,
`project-workspace-bootstrap`, `cloud-to-codex-handoff` and `codex-to-cloud-return`.
Read them from the pinned repository revision; cloning alone does not prove that a
host loaded them. See [INSTALLATION](docs/INSTALLATION.md).

The [A/B roadmap](docs/ROADMAP.md) separates connector operations, machine lifecycle
and the minimal shared contract. Cost-savings percentages in older economics/audit
documents remain hypotheses. Do not restart the stopped quota-burn experiment.
Assess useful completed outcomes, optional model calls and known/unknown costs
without making a new token experiment a prerequisite for A.
