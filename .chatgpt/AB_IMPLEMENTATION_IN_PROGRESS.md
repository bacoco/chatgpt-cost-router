# A/B implementation checkpoint

This branch is work in progress. It must not be presented as a fully verified release.
Base: `6a5b72c490b319f04d90c97ecd47dcb331ce19bd`.
Branch: `feat/ab-products-20260911`.

## Implemented source on this branch

- `operation_contracts/`: strict JSON, operator-owned project/resource/account grants,
  durable SQLite operation/effect journal, exact approvals, private atomic receipts,
  optional operator account budgets, optional MCP SDK compatibility helper.
- `chat_ops/`: full multi-connector action catalog (not issue-only), scoped capability
  observations, native Chat tool driver, bound approvals, preflight/read-back,
  verification-only reconciliation, CLI, MCP app and bound Streamable HTTP client.
  No additional model runtime is imported or invoked by A.
- `fleet_operator/jobs/`: independent ordinary-process profiles, immutable repository
  snapshots, isolated work directories, explicit trusted-local/container modes,
  detached supervisor, progress, bounded logs, owned-child cancellation, timeout,
  durable result reconciliation, CLI and private MCP app.
- `fleet_operator/{secure_gateway,command_policy,host_io,remote_jobs}.py`:
  bounded public gateway policy, confined read helper and typed remote job calls.
- `fleet_operator/{outbox,redaction,relay_bus,relay_service}.py`:
  non-replaying durable dispatch/outbox and idempotent result publication.

## Required before integration

1. Retrieve the actual current branch contents and verify every intended write.
2. Finish wiring the public Fleet MCP server to `configured_runner` and typed job calls.
3. Fix `remote_jobs.call` to use `runner.runtime_bindings`, not only HostSpec.runtime.
4. Close SQLite connections in Outbox.connect using a contextmanager.
5. Preserve/reconcile an already-written private result if interruption occurs between
   atomic result creation and outbox SQL update; never re-execute the command.
6. Finish physical migration of historical A/B/shared modules with compatibility aliases.
7. Finish enrollment/service packaging, versioned upgrades, examples, schemas and docs.
8. Restore/add and run the new A/B and adversarial regression tests. The earlier 139-test
   local development result is historical, not a validation of this reconstructed branch.
9. Run isolated host validation through Fleet Operator when a fresh relay result is available.
10. Only then integrate a verified exact revision into main and publish a truthful receipt.

## Safety boundaries

- No paid model API, no Codex smoke, no real email sending/publication merely to test code.
- No main merge or existing service reload has been requested for this branch yet.
- The current gateway readiness probe is diagnostic only. Absence of its result does not
  prove the gateway is online, offline, or that any deployment executed.
- trusted-local is not an OS security sandbox. Use containers/VMs for untrusted projects.
- A native tool receipt is caller-observed, not an independently obtained connector proof.
- Custom app attachment and transport authentication are separate live validation gates.
- The GitHub relay is owner-operated fallback transport, not a confidential log store.
- PAIR/Serena/provider adapters are optional, not implicit dependencies or hidden model calls.
