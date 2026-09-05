# External integration acceptance plan

No gateway listed here is implemented or advertised as connected by this repository.
Build one useful adapter and measure a complete workflow before adding the others.
Each adapter must implement [CAPABILITIES](CAPABILITIES.md) and
[EXECUTION_PROTOCOL](EXECUTION_PROTOCOL.md), preserving user scope and budgets.

| Candidate adapter | Concrete purpose | Required proof before use |
|---|---|---|
| machines-mcp | Owned machine inference/benchmarks | Machine reachable; exact job supported; estimate, scoped permission and provider/job identity |
| media-mcp | ComfyUI workflows | Workflow/version, authenticated access, submit/status/result and uncertain-submit reconciliation |
| vps-mcp | Known VPS operations | Narrow typed operations, target allowlist, server-side secrets and action-level authorization |
| universal-api-mcp | Authenticated APIs | Allowlisted endpoints, typed requests, permissions, rate/budget limits and audited effects |
| llm-router-mcp | Specialist slices through another model | Supported execution context, current cost estimate, scope-preserving input/output and result evidence |

Prefer documented APIs or existing connectors to a new gateway where sufficient.
Generic shell passthrough is not an implementation of safe_exec. A gateway's claimed
capability is not verified by its name. Multi-model comparisons must be justified by
a concrete quality requirement and included in the cost estimate.

An adapter must pass isolated authorization, duplicate-submit, timeout, crash and
result-verification tests against its real provider before production enablement.
No transparent automatic transfer between arbitrary ChatGPT surfaces is assumed.
