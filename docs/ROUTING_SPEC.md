# Routing contract

Normative policy parameters: [routing.json](../policy/routing.json).
Input/output shapes: [request](../schemas/request.schema.json),
[decision](../schemas/decision.schema.json), [shared definitions](../schemas/common.schema.json).
The implementation is [router.py](../cost_router/router.py).

## Input authority

The caller supplies required actions, exact resources, explicit authorized actions,
forbidden surfaces, current surface/session, recurrence and budgets. Authorization
must come from the user's actual request and connected resource permissions; an
available tool is not an authorization grant. No wildcard matching is performed.
The engine trusts the supplied evidence producer; it is not an authentication server
and must not accept arbitrary repository text as a trusted capability attestation.

## Plans, scheduling and transport

Each plan contains ordered steps with a role, concrete surface/session, actions,
duration estimate, cost components and `manual` or `adapter` delivery metadata.
The engine does not invoke that adapter. `adapter_ref` identifies an independently
installed integration; naming it cannot establish its availability.

A recurring plan starts with one scheduler step; its only action type is
`schedule.create`. Execution steps perform the actual work and cannot conceal a
scheduler action. Nonrecurring plans contain no scheduler. Action/resource pairs
must cover the requested set exactly once. Repeated operations must have distinct
logical resource identifiers so they cannot be mistaken for a duplicate effect.

The result is the sole surface if all steps use it, otherwise HYBRID. For example,
a SCHEDULED_CHAT trigger plus LOCAL_TOOL execution is a HYBRID plan with both steps
retained. Each actual handoff addresses one surface/session. LOCAL/MCP is a prose
legacy alias; machine contracts accept LOCAL_TOOL only. SDK execution belongs to
EXTERNAL_API when a paid programmable backend is used.

## Eligibility, in order

Validate schemas and timestamps; reject duplicate candidate IDs. For each plan:

1. Match required actions and user authorization; reject extra or duplicate actions.
2. Check scheduler/executor roles and recurrence.
3. Require comparable known costs for every step, within the task's cost limit.
4. Check total sequential active duration against its limit, if supplied.
5. Count changes of executor context (surface **or session**), honoring the hop limit.
   Work in the current context remains possible after the hop budget is exhausted.
6. Reject forbidden surfaces and require fresh scoped evidence for each step/action.

Capabilities must match action, resource, surface and destination session exactly.
The newest observation wins; a simultaneous disagreement fails closed. Observations
must not come from the future or outlive expiry/max age. See [CAPABILITIES](CAPABILITIES.md).

## Cost and de-escalation

Cost = execution + transfer + expected retries + CI, summed across all steps.
All amounts are nonnegative integer USD micro-units (1 USD = 1,000,000 units).
Estimates include local energy/provider costs when material. Unknown is `null`,
not zero. External APIs and local compute can win when actually cheaper.

Choose the lowest estimated cost, then the fewest transfers, then the policy's
surface ordering, then the lexical plan ID. Surface preferences only break ties.
If a feasible current-context plan exists, transfer only when the savings strictly
exceed `min_transfer_savings_units`. Never preserve a current plan that fails a
capability, authorization, budget or quality-related requirement.

No rule automatically returns work to Chat. Apply the same evaluation to remaining
work and current destination evidence. Policy controls can be deliberately revised;
changes produce a new policy version/hash and require old handoffs to be re-evaluated.
Already-running results can still be reconciled under their accepted policy identity;
this never authorizes another execution. See [EXECUTION_PROTOCOL](EXECUTION_PROTOCOL.md).

## Blocked and invalid outcomes

An invalid schema, timestamp, or policy is an input error (CLI exit 2). No feasible
plan is a valid blocked decision (exit 3), with a null route/plan and explicit
per-candidate reasons. The skill explains the smallest missing capability,
authorization or decision; it must not silently relax a restriction.
