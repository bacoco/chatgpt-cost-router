# Roadmap and remaining acceptance gates

Read [deployment status](DEPLOYMENT_STATUS.md) for the current evidence and exact runtime revision. The A/B deployment is authorized; the earlier blanket deployment pause is obsolete. **T38 and quota-burning experiments remain paused.**

## Implemented and under live acceptance

A has durable native/direct connector workflows, project/account/session scopes, exact approvals, verification, cancellation and non-replaying recovery. B has independent jobs, supervised processes, logs/progress, receipts/artifacts, typed gateway routing and durable relay publication. Optional worker/mesh code is separated with compatible imports. Owner installers create separate revision-pinned user services.

Two acceptance classes must remain separate: a passing source test suite and a live service completing the owner's actual operation. Never infer either from a successful Git push or queue submission.

## Next operational gates

| Gate | Required evidence |
| --- | --- |
| Complete fleet coverage | Resolve the `macstudio` permission failure without replaying its uncertain job; restore authorized SSH availability on Sparky and Omen, then perform completion/cancellation/artifact checks. |
| A attached to a real Chat account | Authenticated app/transport attachment, fresh capability discovery and a real approved connector workflow, with native read-back. Local MCP discovery is not that attachment. |
| Application-specific use | Enroll the required projects, accounts and named script/build/service profiles. Current owner defaults are smoke and release validation. |
| Untrusted workloads | Exercise the real container engine, filesystem/network/resource restrictions and cleanup under failures. |
| Operational durability | Reboot/login persistence, backup/restore, staged upgrade and rollback with real service reload and uncertain-job handling. |
| Retire older paths | Check other projects' dependencies before disabling legacy relay/mesh/worker services; do not silently break them. |

## Optional, not prerequisites

Load distribution, local inference, extra provider workers, Serena and PAIR can be evaluated separately. They must not delay ordinary connector work or become implicit paid-model calls. Repository restructuring/branding beyond the implemented package boundaries is not needed to operate the current A/B path.
