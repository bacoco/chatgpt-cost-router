# Roadmap: implementation versus acceptance

## Implemented in this A/B delivery

| Area | Code acceptance delivered |
| --- | --- |
| A workflows | Multi-connector action catalog; native tool loop; optional bound HTTP adapter; references, approvals, read-back, cancellation and read-only recovery. |
| Shared contracts | Versioned requests, operator project/resource/account grants, scoped capabilities, private journal, atomic claims and receipts. |
| B lifecycle | Independent CLI/MCP, immutable source, owned supervisor, queue/concurrency, logs/progress, cancellation/deadlines, stale recovery, results and artifact retrieval. |
| Gateway/relay | Typed project/node calls, bounded public commands, enrolled identity pins, non-replaying durable outbox and legacy entrypoint compatibility. |
| Structure | Physical worker/mesh migration with exact old import aliases; A and ordinary B have no implicit model runtime. |
| Operations | Local release staging/integrity, idle activation/rollback, explicit enrollment plans, user-service rendering and installable core wheel. |
| Delivery | Regression/failure-injection tests, local demonstration, schemas/examples, usage, feature-branch commits and machine-readable validation. |

## Gates before production integration or deployment

1. Review the committed feature branch and run validation in the target environment.
   Code publication is complete; main merge and deployment remain separate authorized
   actions. Read `../audits/ab-implementation-20260911/` for delivery evidence.
2. Run the optional official MCP SDK test with its pinned dependencies, then verify
   authenticated attachment from each actual Chat surface/account. Local HTTP tests
   and a tool-registration recorder are not that live acceptance test.
3. Validate one explicitly authorized harmless job on each actual target OS/SSH
   transport. Test service install/reload/reboot, measured metrics and version rollback.
4. Validate the pinned container image/engine and its filesystem/resource/network
   behavior on the real target before accepting untrusted workloads.
5. Exercise real connector workflows with an explicitly authorized test destination,
   actual per-action capability evidence and read-back. Do not send or publish merely
   to make a code test pass.

**T38 and deployment remain paused.** None of these gates authorizes itself.

## Deliberately optional extensions

Legacy worker/prompt mesh, placement optimization, provider-account telemetry,
local inference, Serena and PAIR are not prerequisites for A/B ordinary operations.
Public multi-tenant OAuth, automatic OS provisioning and a new project-aware mesh
would be separately scoped products, not claims made by this release.
