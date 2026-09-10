# ChatGPT Cost & Capability Router

Choose a sufficient execution plan using **verified capabilities, user authorization
and estimated total cost**. Code does not automatically require Codex; complexity
alone does not require Work. Owned hardware is an option when its actual capabilities
and costs fit the task.

The repository now contains a deterministic recommendation engine, versioned JSON
contracts, five repository-backed skills, a durable local operation ledger and tests.
It evaluates caller-supplied plans. It does not discover host tools, launch another
ChatGPT surface, operate hardware, send messages or implement remote MCP gateways.


## Cloud-first project bootstrap

This repository is also the **source installation kit** for a practical ChatGPT cloud workflow. The operational goal is to do as much project work as possible with normal ChatGPT + Developer MCPs, use Scheduled Tasks as project launchers/automation when useful, keep durable state in GitHub, and hand only the remaining specialist work to Codex.

For a new or existing GitHub project, the shortest entry point is [PROJECT_BOOTSTRAP_PROMPT](docs/PROJECT_BOOTSTRAP_PROMPT.md). Replace only the target repository:

```text
TARGET_REPO=<owner>/<repo>

Bootstrap this repository using the current `main` of `bacoco/chatgpt-cost-router`.
Read and execute `docs/PROJECT_BOOTSTRAP_PROTOCOL.md` at one pinned source SHA.
```

The bootstrap protocol installs a bounded `.chatgpt/` project workspace, initializes a durable checkpoint, and creates or reuses a repo-specific Scheduled Task/workspace entry point. When ChatGPT reaches a real capability boundary, the project is handed to Codex through a GitHub `TO_CODEX.md` packet and Codex returns through `RETURN_FROM_CODEX.md`; no full chat transcript needs to be copied.

Start with [INSTALLATION_KIT_INDEX](docs/INSTALLATION_KIT_INDEX.md). The cloud lane and its evidence are documented in [CLOUD_EXECUTION_LANE](docs/CLOUD_EXECUTION_LANE.md). The repo-workspace convention is in [REPO_SCHEDULER_WORKSPACE](docs/REPO_SCHEDULER_WORKSPACE.md), and the bidirectional Codex handoff is in [CHATGPT_TO_CODEX_HANDOFF](docs/CHATGPT_TO_CODEX_HANDOFF.md).

Current empirical status: authenticated GitHub MCP read/write, Scheduled Task GitHub access, scheduled write deduplication, bounded ChatGPT code changes and Actions control-plane access have been tested. The one-prompt bootstrap, scheduler-chat continuation on a clean profile, fresh-chat recovery and full ChatGPT → Codex → ChatGPT round trip still have explicit validation tests pending; see [VALIDATION_STATUS](docs/VALIDATION_STATUS_2026-09-10.md).

## Try the executable example

Requires Python 3.11 or newer. Run from this checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m cost_router route examples/request.json --at 2026-09-05T00:30:00Z
python -m cost_router validate handoff examples/handoff.json
python -m unittest discover -s tests -v
```

The request example and its observations are **synthetic fixtures**, not live
capability proofs or provider prices. `--at` explicitly replays historical time.
For real decisions, supply fresh observations and omit `--at`. Expired or unknown
capabilities cannot make a plan eligible. Exit codes: `0` valid/routed, `2` invalid
input, `3` blocked decision.

## Decision rules

1. Describe exact required and authorized actions, resource scope, current context,
   recurrence and cost/duration limits.
2. Validate each candidate's actions, authorization and current destination evidence.
3. Reject plans with missing capabilities, unknown costs, prohibited surfaces,
   uncovered recurrence, duplicate work or exceeded budgets.
4. Compare execution + transfer + retry + CI cost in integer USD micro-units.
   Break ties by staying in the current context, then the versioned preference order.
5. Emit the selected plan or an explicit blocked result with rejection reasons.
6. Re-evaluate remaining work and destination access at handoff. A recommendation
   becomes execution only through an adapter's explicit acceptance and claim.

The canonical values and parameters live in [policy/routing.json](policy/routing.json).
The normative algorithm and plan composition are in [ROUTING_SPEC](docs/ROUTING_SPEC.md).
`HYBRID` describes a plan spanning multiple surfaces; a handoff itself always names
one actual receiving surface and session.

## Skills

- [capability-router](skills/capability-router/SKILL.md): classify the remaining task,
  assemble evidence and plans, then evaluate them.
- [surface-handoff](skills/surface-handoff/SKILL.md): low-level v2 delegation/return
  contract preserving scope, state and proofs.
- [project-workspace-bootstrap](skills/project-workspace-bootstrap/SKILL.md): take a
  `TARGET_REPO`, install/reconcile the `.chatgpt/` project workspace and create or reuse
  a repo-specific Scheduled Task launcher.
- [cloud-to-codex-handoff](skills/cloud-to-codex-handoff/SKILL.md): persist only the
  remaining work in GitHub and emit a short Codex takeover prompt tied to an exact SHA.
- [codex-to-cloud-return](skills/codex-to-cloud-return/SKILL.md): make Codex return a
  verifiable result artifact/commit so ChatGPT can re-read and continue safely.

The three workflow skills deliberately build on `surface-handoff` instead of duplicating
its protocol. GitHub is the canonical source for their definitions. OpenAI Skills are
portable across supporting products, but installation/sync can differ by surface, so a
repo-backed skill must still be re-read or installed where it will execute.

Native repository discovery uses the `.agents/skills` links for skills that have been
installed into that discovery path. GitHub-only use can always read the canonical
`skills/*/SKILL.md` files and their linked contracts at one pinned commit. See
[INSTALLATION](docs/INSTALLATION.md); simply cloning a repository does not prove
that a particular host loaded or executed a skill.

## Evidence and execution

[CAPABILITIES](docs/CAPABILITIES.md) specifies scoped, expiring observations.
[HANDOFF_SPEC](docs/HANDOFF_SPEC.md) defines required fields and v1 migration.
[EXECUTION_PROTOCOL](docs/EXECUTION_PROTOCOL.md) defines durable claims, terminal
states, uncertain effects and scheduler checkpoints. `cost_router.ledger.Ledger`
implements the local claim/state contract using SQLite. External adapters must use
it before effects and implement provider idempotency or reconciliation. It does
not promise exactly-once remote effects.

## Economics

The earlier target of roughly 50–80% less Work/Codex usage remains an unvalidated
hypothesis. Displacing tasks can move cost to APIs, CI or local execution. Calling a
paid provider through MCP does not make it free. Record an initial baseline before
changing routes and compare matched task outcomes, quality and all costs.
See [TOKEN_ECONOMICS](docs/TOKEN_ECONOMICS.md).

## Project map

| Path | Purpose |
|---|---|
| [SPEC.md](SPEC.md) | Implemented scope and acceptance requirements |
| [cost_router/](cost_router/) | CLI, eligibility/cost evaluator, validation and local ledger |
| [policy/](policy/) | Canonical versioned policy |
| [schemas/](schemas/) | JSON Schema 2020-12 contracts; local references only |
| [examples/](examples/) | Synthetic requests and complete handoff examples |
| [tests/](tests/) | Canonical/negative fixtures and executable regression tests |
| [docs/](docs/) | Architecture, protocol, capabilities, economics and integration plan |
| [audits/2026-09-05/](audits/2026-09-05/) | Original audit, evidence, fixes and verification |

Read the [roadmap](docs/ROADMAP.md) for integrations that are still external to this
repository. The audit is historical; its [remediation record](audits/2026-09-05/REMEDIATION.md)
records which contracts and behaviors were changed and what was actually tested.
