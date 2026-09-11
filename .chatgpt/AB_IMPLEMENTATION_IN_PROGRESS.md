# Historical checkpoint resolved by the A/B branch delivery

The earlier checkpoint on this branch was not validated and named concrete missing
wiring/recovery work. The branch was subsequently reread at exact commit
`9a24054bd9ad392a2b16f158fb326cb5e1367b4d`; the following are now implemented in the
feature-branch delivery, with new tests rather than reuse of its historical test count.

- Public Fleet MCP uses the bounded configured runner and typed job calls.
- Remote jobs use configured runtime bindings and can pin node/runtime/policy identity.
- Outbox connections close, saved receipts survive interrupted SQL updates and
  publication can retry without re-execution or access to the original command file.
- Legacy worker/mesh modules physically reside under Fleet Operator with old aliases.
- A handles preflight failures, uncertain effects, lost IDs, expired read-back and
  cancellation races without replaying writes.
- B handles duplicate supervisor claims, actual cancellation/deadlines, fsynced result
  recovery, stale work beyond list pagination, metrics and verified artifact chunks.
- Local enrollment, exact-version staging/activation/rollback, user-service rendering,
  core packaging, examples, schema and validation tooling are provided.

The code is now committed on `feat/ab-products-20260911` through the GitHub connector.
The earlier claim that no write action was available was incorrect. No main merge
or deployment was performed. See `CURRENT.md`, `../docs/AB_VALIDATION.md` and
`../audits/ab-implementation-20260911/` for evidence and remaining live acceptance gates.
T38, deployments and real services remain paused.
