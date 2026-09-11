# Architecture: independent A and B, shared contracts

[Deployment status](DEPLOYMENT_STATUS.md) is the authority for live installation. This document describes implemented responsibilities and remaining trust boundaries, not an assertion that every connector and host is deployed.

```text
Native Chat connectors         Optional direct MCP endpoints
          |                                  |
          +-------- A / chat_ops ------------+
                         |
            operation_contracts
          projects, accounts, journals
                         |
               optional A-to-B calls
                         |
   GitHub relay / private MCP / local CLI
                         |
      B gateway -> enrolled node -> named profile
                         |
          owned process, logs, receipt, artifacts
```

## Ownership

| Module | Responsibility |
| --- | --- |
| `chat_ops/` | Workflows, native-driver instructions, account/session-scoped capability observations, exact approval and read-back. |
| `operation_contracts/` | Project/resource grants, account reservations, private records, durable journals and common validation. |
| `fleet_operator/jobs/` | Independent process requests, immutable source workspaces, supervision, cancellation, metrics, logs and receipt-bound artifacts. |
| `fleet_operator/` | Guarded local/SSH transport, typed runtime-bound calls and durable relay publication. |
| `fleet_operator/enrollment/` | Revision staging/integrity, idle activation and planned gateway enrollment. |
| `fleet_operator/workers/` | Optional worker/mesh integrations, physically separated from routing. |
| `cost_router/` | Deterministic cost/capability decisions and compatible historical imports. |
| `scripts/ab_*` | Explicit owner deployment/validation tools; not an unrestricted public command API. |

A and B can run independently. The retained optional mesh/provider workers do not define B's ordinary process contract. `SPEC.md` describes only the decision engine.

## Evidence and recovery

A observations are scoped to principal, project, resource, account, surface and session. Native evidence remains caller-observed; it is not a provider-signed receipt. The actual connector enforces its own account authorization. Workflow decisions are serialized, write approval binds resolved inputs and successful writes need a separate verification read.

A missing response creates an uncertain state, not permission to repeat the mutation. Verification may recover the lost output for downstream steps. Cancellation/deadlines stop new dispatch; they do not undo completed external effects.

B distinguishes submission, owned execution and terminal completion. Journal/receipt tokens bind results to the requested policy and run. Process supervision and private logs have bounds. Artifact delivery checks the durable receipt and complete file hash before returning a bounded `data_base64` chunk with `verified`, offsets and EOF.

The relay's outbox separates effect execution from result publication. A lost push can retry the stored result without re-running the effect. Conflicting job/result identities are rejected. The current private queue and the old compatibility queue must not both receive one operation.

## Deployment boundaries

Runtime code is staged by exact SHA, uses a private virtualenv and is selected through explicit policy. Source delivery, configuration, service start, health, end-to-end completion and Chat attachment are distinct gates. Preserve the virtualenv executable path during activation.

`trusted-local` assumes trusted owner code; its workspace is not an OS security boundary. Real container isolation remains an acceptance gate. MCP is loopback-only unless placed behind separately configured authentication. A configured principal or session ID is not authentication for arbitrary internet callers. Multi-user deployment needs correctly authenticated contexts.

The installed owner profiles are deliberately narrow. Additional applications need their own project grants and profiles. Legacy services are retained separately for recovery; their retirement is not implied by deploying A/B. See [roadmap](ROADMAP.md).
