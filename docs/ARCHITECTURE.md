# A/B implementation architecture

## Product boundaries

```text
Native Chat driver / optional bound MCP adapter
  -> chat_ops (A) -> authorized Gmail / GitHub / Cowboy / other tools
        | optional, explicit fleet action
        v
CLI / private MCP -> Fleet gateway -> fixed node CLI -> fleet_operator.jobs (B)
                                                        |
                                                        +-- owned ordinary process
                                                        +-- immutable workspace + receipt
```

`operation_contracts` is the common authorization/journal boundary, not an agent.
A imports neither a worker runtime nor a model provider. B's ordinary job service
requires neither Chat nor the cost decision engine. Legacy workers now physically
live in `fleet_operator/workers`; `cost_router` compatibility modules alias their
exact module identity so old imports and patch points continue to work.

## A workflow state and external effects

Workflows carry version/project/idempotency/deadline and ordered named steps.
The runtime checks resource/action grants before work and exact resource arguments
when references resolve. Catalog descriptors cannot weaken built-in write rules.

Each step has a journaled state, optional preflight, one call, required write
verification, optional read-only recovery and an input-bound approval. Capability
observations have a scoped identity, current surface/session, TTL and evidence ref.
Visibility, invocability, verification and denial are different facts.

Dispatch atomically compares the current effect data and fences cancellation and
expired writes. Pending calls use single-use tokens; late results cannot overwrite
a newer reconciliation token. Cancellation stops future effects, not past external
changes. Read-back may finish after the workflow deadline without permitting new writes.

A lost write return is UNCERTAIN. Reconciliation issues only a read. When the read
requires a lost object ID, an explicit independently addressable recovery read must
recover it; absence of that read fails closed. Reconciliation never assumes that
an exception means the external write did not happen.

## B execution and ownership

A node owns its principal, project grants, named profiles, repositories and state
root. Requests cannot select arbitrary commands, filesystem roots or credentials.
Profiles fix argv, timeout, output bounds, artifacts and isolation mode. Source
snapshots come from the bound repository's exact commit, not its dirty working tree.

SQLite registers an idempotency key, immutable request and policy digest. Concurrent
submissions deduplicate. Starting claims a slot, then a supervisor; the supervisor
claim is itself single-use. A duplicate or stale invocation cannot spawn again.
Policy changes block continued execution under stale authorization.

The supervisor owns a process group, bounded stdout/stderr, heartbeat and optional
`FLEET_PROGRESS` records. Timeouts/cancellation target that owned group. Result files
are private and fsynced before SQL completion. A receipt saved before a SQL failure
can be reconciled exactly; an unknown outcome stays UNCERTAIN and is not restarted.

Artifact retrieval opens only manifest-listed regular files without following
symlinks, checks full size/hash and returns bounded base64 chunks with chunk hashes.
Linux `/proc` yields direct-process CPU/RSS; unsupported platforms return unknown,
not invented metrics. Health includes queue counts, capacity, load and free disk.

## Gateway and relay

The public MCP builder uses `configured_runner`, not the broader historical runner.
The command policy accepts a small bounded read set and fast-forward Git pull;
ordinary computation uses a project-bound profile. Git hook/fsmonitor/pager/config
escape options, relative executables and raw destructive commands are rejected.
Filesystem helper code is fixed, component-confined and does not follow symlinks.
Operator-owned repository metadata and local binaries remain trusted.

Typed node calls use configured runtime paths and strict JSON. Replies can be pinned
to node/runtime/policy identity. A submit acknowledgement is not job success.

The relay claims once, saves a result and separately publishes its outbox. Failed
publication can retry independently of the original command file or gateway config.
Recovery checks a saved private result before creating an UNCERTAIN result. Payload
conflicts never overwrite the saved result or cause re-execution. Legacy entry points
delegate to this canonical path. GitHub result branches are not secret storage.

## Enrollment and release management

Local operator commands stage exact Git revisions with file hashes, verify releases,
produce enrollment plans tied to current configuration and apply only reviewed
host bindings. No arbitrary unconfigured SSH destination is added by a request.
Activation and rollback require an idle journal with no uncertain jobs. They atomically
switch an active record but do not reload a service. Bootstrap verifies the selected
release and pins a node configuration before executing it.

User launchd/systemd definitions are generated but never installed or loaded by the
renderer. Actual SSH enrollment requires installing the same verified runtime and
private configuration on the target, then binding its real paths and validating
reachability. Remote copying, OS provisioning and public OAuth are not implicit.

## Trust and compatibility boundaries

Project isolation is logical authorization plus separate workspaces. `trusted-local`
is not containment against hostile code under the same OS user. Container command
construction and owned-ID cleanup are implemented; engine, macOS and real SSH tests
remain deployment gates. Use a separately tested container/VM for untrusted code.

Legacy mesh speaks worker/prompt and remains a private opt-in compatibility API;
it is not relabelled as a complete multi-project scheduler. Account reservations are
operator budgets, not provider quota telemetry. External auth, native Chat attachment,
Serena, PAIR and model APIs are distinct optional integrations.
