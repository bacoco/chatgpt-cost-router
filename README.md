# ChatGPT Cost & Capability Router

Choose a sufficient execution plan using **verified capabilities, user authorization
and estimated total cost**. Code does not automatically require Codex; complexity
alone does not require Work. Owned hardware is an option when its actual capabilities
and costs fit the task.

The repository now contains a deterministic recommendation engine, versioned JSON
contracts, two repository-backed skills, a durable local operation ledger and tests.
It evaluates caller-supplied plans. It does not discover host tools, launch another
ChatGPT surface, operate hardware, send messages or implement remote MCP gateways.

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
- [surface-handoff](skills/surface-handoff/SKILL.md): prepare a v2 delegation or return
  envelope preserving scope, state and proofs.

Native repository discovery uses the `.agents/skills` symlinks. GitHub-only use can
read the skills and their linked contracts at one pinned commit. See
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
