# Source and deployment status — 24 October 2026

These states have separate evidence and revisions. A local source-suite result
does not refresh an installation or establish current live availability.

| State | Revision | Evidence and limits |
| --- | --- | --- |
| **SOURCE-TESTED** | `d2438d95e2a3ceca994d60b7ec25522e23be5f83` | [24 October receipt](../audits/main-integration-20261024/validation.json): 255 tests, 254 PASS, 1 SKIP (optional official MCP SDK absent), no failures/errors; source unchanged. [Reproduction and environment](../audits/main-integration-20261024/README.md). |
| **DEPLOYED** | `10b3ee3e438d57b210b1155e2dbaf19aac9b00db` | [Last recorded deployment evidence](https://github.com/bacoco/chatgpt-cost-router/blob/cfd5dc7a0a452bbf4027871db1077bf6147b6fac/docs/DEPLOYMENT_STATUS.md), 11 September; host details retained below. No redeployment in this lot. |
| **LIVE-VERIFIED** | `10b3ee3e438d57b210b1155e2dbaf19aac9b00db` | [Same historical runtime record](https://github.com/bacoco/chatgpt-cost-router/blob/cfd5dc7a0a452bbf4027871db1077bf6147b6fac/docs/DEPLOYMENT_STATUS.md): process/artifact/cancellation on MacBook and macstudioprod only; remaining hosts, Chat attachment and connector gates are not certified. No fresh live check. |

The source receipt includes the independent fixes from PR #21 (queue revocation)
and PR #20 (account-scoped evidence). Later documentation/evidence commits do not
certify another source revision. Earlier test counts remain historical.

## Last recorded runtime observations — 11 September 2026

> **Source-policy note — 19 September 2026.** Current `main` now forbids
> GitHub Actions and recognizes scoped native Chat image + binary Git routes. This
> document remains the last deployment evidence for the installed A/B runtime and
> does not claim that runtime has been redeployed to the new source revision.

The A/B source was merged into `main` by PR #12 at `e96562155afd2c91e6dd05b8903746cd85557b20`. The table below records the last deployment evidence, not a new live availability check. A source merge does not update the installed runtime. Read [integration status](MAIN_INTEGRATION_STATUS.md) for source validation and the historical PR #13 exclusion.

Runtime under test: `10b3ee3e438d57b210b1155e2dbaf19aac9b00db`. Supplemental skill documents came from the same revision; later source commits improve deployment helpers/documentation without silently replacing installed runtime code.

| Host / surface | Observed state |
| --- | --- |
| MacBook | A and B node services started; 209 tests passed including official MCP; real completion, artifact and cancellation verified. |
| macstudioprod | B node service active with observed PID; real completion, artifact and cancellation verified. |
| macstudio | Installed but not accepted: first smoke is UNCERTAIN with PermissionError; not replayed. |
| Sparky | SSH became unavailable during rollout; not deployed. |
| Omen | SSH connection timed out; not deployed. |
| New relay | Installed; native GitHub queue health check reached the MacBook node. End-to-end terminal read-back is not certified by this source merge. |
| MCP | Direct loopback initialize passed for A and gateway; complete tools/list/node health acceptance still requires its own verified receipt. |

New services are separate from legacy services. T38 remains paused. Chat account attachment, real multi-connector application workflows, untrusted-container isolation and reboot/rollback acceptance remain separate gates. See [roadmap](ROADMAP.md).
