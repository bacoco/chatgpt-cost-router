---
name: capability-router
description: Choose a sufficient execution plan for a task using scoped capability evidence, user authorization and estimated total cost. Use when selecting or reconsidering Chat, scheduling, local tools, Codex, Work or API execution.
---

# Capability Router

Preserve the user's requested task, restrictions and existing authorization.
Code alone does not imply Codex; a named tool alone does not prove capability.

1. Identify the remaining actions and exact resources, current surface/session,
   recurrence, budget and authorized scope. Ask only for information that changes
   feasibility; otherwise record unknowns explicitly.
2. Read the [routing contract](../../docs/ROUTING_SPEC.md) and
   [canonical policy](../../policy/routing.json) at the same repository revision.
   Build candidate plans from actual host capabilities, not a surface-name lookup.
3. Obtain fresh, trusted, action/resource/session-scoped observations following
   [capability evidence](../../docs/CAPABILITIES.md). Do not perform a write merely
   to test access. A connection in this session does not establish destination access.
4. Produce a request conforming to [request.schema.json](../../schemas/request.schema.json).
   Include authorization, all cost components and ordered plan steps. Keep scheduler,
   executor and transport roles distinct; asynchronous schedules cannot satisfy a
   request for synchronous isolated workers.
5. When a checkout and Python dependencies are available, run
   `python -m cost_router route request.json` from its root. Otherwise apply the
   same contract and label the recommendation as reasoned, not engine-executed.
   Emit `blocked` if no plan has sufficient evidence and authorization.
6. Compare total estimated marginal cost after feasibility checks. Prefer the current
   context on a tie. Transfer only for a verified benefit; re-evaluate the destination
   and remaining work instead of unconditionally returning to Chat.
7. A routed decision is a recommendation. For an actual transfer, use the
   [surface-handoff skill](../surface-handoff/SKILL.md) and the receiving adapter's
   acceptance protocol. Do not report launch or completion without its evidence.

For GitHub-only use, resolve relative references at the same pinned commit. For
native discovery, use the full checkout and its `.agents/skills` links; copying only
this file loses its contracts. See [installation](../../docs/INSTALLATION.md).
