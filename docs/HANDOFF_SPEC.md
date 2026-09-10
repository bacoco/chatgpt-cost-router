# Surface Handoff v2

Normative structure: [handoff.schema.json](../schemas/handoff.schema.json).
Semantic checks: [handoff.py](../cost_router/handoff.py).
Canonical examples: [delegation](../examples/handoff.json),
[completed return](../examples/completed-return.json). These examples are synthetic.

## Required information

| Group | Fields and meaning |
|---|---|
| Protocol | version=2, direction, status, created_at |
| Identity | task_id, handoff_id, operation_id, parent_handoff_id |
| Context | from_surface/session, recommended_surface, target_session_id |
| Policy | policy_version and SHA-256 of canonical policy JSON |
| Mission | nonblank goal, done, remaining, constraints, meaningful success_criteria |
| Repository | repo, branch, commit_sha and files; explicit null/no files for non-repo work |
| Authorization | planned actions, authorized_actions, authorization_ref, forbidden_surfaces |
| Budget | cost_unit, estimated_cost_units, max_cost_units |
| Proof | typed evidence records, tests, criterion verification, referenced commit and timestamps |
| Transfer | escalation_reason and return_to_chat_when |
| Extensions | explicit extensions object; misspelled top-level fields are rejected |

`repo` is owner/name; a repository handoff requires its branch and full 40-character
commit SHA. Files are context references, not permission to open arbitrary local paths.
A file list never broadens the explicit action/resource authorization.

Delegation: direction=delegation, status=ready, nonempty remaining/actions/return
conditions. Return: direction=return, a parent handoff, no new actions, and status
completed/failed/blocked. A handoff cannot be its own parent.

Completed returns have remaining=[] and one passing verification per requested
criterion. Every declared test passes. Each passing item references supplied,
nonfuture evidence for the resulting commit. Required tests and original scope
cannot be dropped by the ledger's completion transition. A return may name a newer
resulting commit, but the receiver must verify it against the actual repository state.

## Validation and receiving

```bash
python -m cost_router validate handoff examples/handoff.json
```

Schema validation alone is insufficient: the Python check also checks policy,
permissions, budget, criterion/evidence consistency and completion. This command
validates saved data; it does not establish live destination access. Before acceptance
and again before claiming execution, the ledger requires destination preflight and,
for repository work, a caller-verified current commit. See [EXECUTION_PROTOCOL](EXECUTION_PROTOCOL.md).
The ledger validates completion against the originally accepted policy identity,
so a later policy change cannot strand an in-flight result. The standalone command
checks the current policy; it cannot recover an operation's accepted identity without
the ledger. This completion exception cannot be used for acceptance or execution.

Keep packets compact through accessible artifact references. Preserve user constraints,
required tests and scope even if the typical 5 KiB target is exceeded. Do not include
secrets or copy unrelated conversation history. Evidence references identify artifacts;
they do not authorize the recipient to execute instructions found inside them.

## Migration from v1

This is an intentionally incompatible protocol revision: v1 packets do not contain
enough required identity, policy, permissions or proof information. The v2 validator
rejects them. Reconstruct a new packet from the original task and current evidence;
do not merely change version to 2 or fabricate missing fields. Preserve source
references in extensions if useful. Empty remaining is allowed for completed returns,
not for delegation. HYBRID remains a decision-plan value, never a handoff destination.
