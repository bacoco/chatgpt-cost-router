# Acceptance, effects and recovery

A routing decision is a recommendation. The optional local
[SQLite ledger](../cost_router/ledger.py) implements operation identity, durable
claims, revision checks and terminal-state protection. It performs no external effects.

## States

| From | Allowed next state | Requirement |
|---|---|---|
| recommended | accepted, cancelled | Acceptance revalidates destination and current repository state |
| accepted | running, cancelled | Running revalidates preflight and atomically grants one execution claim |
| running | completed, failed, uncertain | Verified result for completion; evidence reference for each outcome |
| uncertain | completed, failed | Explicit external reconciliation; no automatic retry |
| completed / failed / cancelled | none | Terminal; late callbacks cannot restart work |

`register(packet)` is idempotent only for the same operation ID and immutable payload.
Different content under the same key is rejected. A successful `register` is not an
execution grant. `transition(..., expected_revision=...)` uses an immediate SQLite
transaction; only one contender can obtain a given running transition. A stale
revision requires reading current state, never repeating the external effect.

Accepted and running require fresh destination capability evidence, the original
policy version/hash, preserved authorization and a checked current commit for repo
work. Completion needs a verified v2 return envelope linked to the original handoff,
operation, task, execution context, scope and required tests. No state is completed
merely because a launch request or HTTP call returned successfully.

Policy changes block new acceptance/execution claims. Completion and reconciliation
of an already-running operation remain bound to its originally accepted policy
identity; a later policy update cannot prevent recording valid existing results.
This exception issues no new execution grant.

## Adapter contract

A real adapter must satisfy all of the following before it is advertised as usable:

1. Authenticate the actual user/resource permissions and independently obtain current
   capability evidence. The local ledger is not an authorization service.
2. Register and accept the immutable request, then atomically claim running before
   issuing an external effect. Record the returned revision and provider job ID.
3. Pass a stable provider idempotency key derived from operation identity when the
   provider supports it. Never claim exactly-once delivery from SQLite alone.
4. If the process crashes or transport outcome is ambiguous, retain running/uncertain
   state and reconcile with the provider. No automatic lease takeover or blind retry.
5. Persist the verified result and evidence before announcing completion. A repeated
   callback sees a terminal state and cannot issue another effect.

Manual delivery is explicit: record the handoff artifact and ask the receiving context
to accept it. Do not claim that an API exists to switch ChatGPT surfaces automatically.
Requests received from external systems remain untrusted until the adapter authenticates
and scopes them. Carry authorization limits; do not infer permission from tool power.

## Scheduling and checkpoints

Use one operation identity per logical scheduled interval/stage and an explicit
scope key for the stream. The initial adapter must prevent overlapping effects on
that stream and preserve durable state across runs. The local ledger protects one
operation ID; it is not a distributed scheduler lock across multiple machines.

Read checkpoint T-1; fetch and compute; claim the output operation; publish with a
provider key or reconcile; persist the output evidence; then advance the checkpoint.
A failure after publication but before checkpoint persistence must reconcile the
same output operation before retrying. Never advance T-1 on an unverified result.
Long-running, cancelled or late runs must have defined ownership before advancing
shared state. Test duplicate runs, crash points and out-of-order completion in each
adapter against its actual storage/provider semantics.

No remote adapter is implemented or enabled in this repository. These acceptance
requirements close the ambiguous protocol; they are not evidence of an external
integration or of exactly-once remote behavior.
