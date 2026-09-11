# Chat-first Operations & Fleet Operator

Two independent products in the repository historically named ChatGPT Cost &
Capability Router. A can use B as a tool; neither requires the other.

| Product | Purpose |
| --- | --- |
| **A — Chat-first Operations** | Finish authorized work through Gmail, GitHub, WordPress/Cowboy and other available connectors, without default Work/Codex/model-API delegation. |
| **B — Fleet Operator** | Access machines, run and supervise ordinary processes, monitor them and retrieve results, with or without Chat. Model workers are optional. |

**Implementation publication is partial.** A/shared corrections are committed on
this delivery branch. A connector safety block interrupted the B dependency batch;
its dependent source changes were restored to keep the branch coherent. The full
prepared A/B source is supplied separately as an artifact, not as a claimed GitHub
or deployment success. Read the [delivery status](docs/AB_DELIVERY_STATUS_2026-09-11.md)
and [CURRENT](.chatgpt/CURRENT.md) before using any implementation claim.

## A source on this branch

`chat_ops/` implements project/resource/account/session-scoped capability evidence,
connector-independent action descriptors, native single-tool instructions, exact
approvals, read-back verification, workflow output references, cancellation,
deadlines and read-only reconciliation. Pending mutations are not redispatched.

CLI and private MCP expose the same engine. The optional direct MCP adapter binds
operator-owned endpoints/accounts/tool names, validates discovered input schemas,
handles bounded JSON/SSE replies and refuses redirects or remote schema fetching.
The native lane invokes the actual client's connectors; it does not steal their
credentials or turn a Python process into a Chat subscription. Native result
records are caller-observed, not independently provider-verified evidence.

The catalog includes Gmail, GitHub, Cowboy, calendars, documents, contacts and
optional Fleet/Serena actions. An issue is one output among many. External apps
remain their own implementations; capabilities must be observed for the actual
surface, account and action. Session identifiers scope evidence, not authentication.

## B source and remaining publication

The earlier B implementation is retained. It contains ordinary process profiles,
a node lifecycle, gateway/MCP and relay foundations, plus optional legacy workers.
The prepared continuation's supervisor, immutable artifacts, gateway/outbox fixes,
physical worker migration, enrollment, release tooling and packaging are not all
published here. Do not claim a complete tenant-isolated fleet from this branch.

T38, user-machine jobs, services and deployments remain paused. PAIR and Serena
were not installed. Public exposure requires separate authentication and OS
isolation; trusted local process execution is not a hostile-code sandbox.

## Tests and evidence

The reconstructed published subset passed **134 local tests**. The separate full
prepared source ran **177 tests: 176 passed and one official-SDK smoke skipped**.
Those are different trees. No unobserved CI result or live deployment PASS is claimed.
The artifact also contains a built/isolated-install-checked Python wheel.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 -m chat_ops --help
python3 -m fleet_operator --help
```

[Architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md),
[historical validation](docs/VALIDATION_STATUS_2026-09-11.md),
[surface map](docs/SURFACE_CAPABILITY_MAP.md) and
[project bootstrap](docs/PROJECT_BOOTSTRAP_PROTOCOL.md) distinguish existing source,
prepared changes and live proofs. [SPEC](SPEC.md) describes the decision engine,
not the entire A/B product. Keep credentials and private runtime state outside Git.
