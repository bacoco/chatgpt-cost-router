# Capability evidence

A capability observation is bound to action + resource + surface + session ID.
It has observed_at, expiry, status, method and an evidence reference. The shared
schema is [common.schema.json](../schemas/common.schema.json); the manifest schema
is [capabilities.schema.json](../schemas/capabilities.schema.json).

- `verified`: a trusted current action result or authoritative permission check,
  with evidence and finite expiry. The permission check must cover the specific
  action and reachable tool interface, not just account membership or tool visibility.
- `unavailable`: a scoped negative observation, not a universal product claim.
- `unknown`: visible, untested or lacking sufficient evidence; it cannot enable a plan.

Do not perform destructive writes merely to probe a capability. Use documented
permission introspection or evidence from an already authorized operation. Reading
one repository never proves write access elsewhere. Record authentication/permission
failures as scoped negatives; retain both observations so a newer denial overrides
an older success. Simultaneous conflicting observations fail closed.

Manifest captured_at and observation times cannot be in the future. An observation
cannot be newer than its containing manifest. Expiry must follow observation time;
expiry is exclusive. The versioned policy additionally limits maximum observation age.
The receiving execution context must provide its own evidence; the current Chat/Work
session cannot attest that a different or future session has the same tools.

Preflight again at each scheduled execution, handoff acceptance and execution claim.
A scheduler created successfully today does not prove tomorrow's connectors will
work. A remote call can still fail after preflight; follow the uncertain-effect protocol.

## Chat Operations account scope

For Chat Operations, persisted evidence also includes principal, project, connector
and account reference in its exact scope. Observations for different accounts or
connectors coexist; lookup uses the project's bound connector and account only.
Expiry, denial, observation ordering and same-timestamp conflict checks apply
within that complete scope.

### Existing Chat Operations journals

The account-aware scope uses eight-field JSON keys in `connector_evidence`:
`[principal, project, resource, action, connector, account_ref, surface, session]`.
Legacy six-field keys remain unchanged for inspection and are never looked up or
silently converted. After upgrading, obtain fresh scoped observations through the
normal discovery/observation path before invoking tools. Reopening a journal has
the same behavior; there is no automatic migration of historical evidence or
change to project grants. Previously overwritten observations cannot be recovered.

## Historical observations

The previous architecture document listed Scheduled Chat PASS/NOT EXPOSED/FAIL
claims without reproducible context or evidence links. They remain only in the
[historical audit](../audits/2026-09-05/original-audit.md). They are not current
capability grants. Start with [an unverified manifest](../examples/capabilities-unverified.json)
and add only actual observations from a trusted producer.

Examples and test fixtures explicitly contain synthetic observations. They must never
be reused as production attestations. The router validates scope/freshness/shape; it
does not cryptographically authenticate evidence or discover capabilities on its own.
