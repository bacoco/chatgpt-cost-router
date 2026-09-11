# A/B delivery status — 11 September 2026

**GitHub publication is partial. Do not merge or deploy as a completed A/B rollout.**

The owner requested implementation after the documentation review. Work resumed
from `9a24054bd9ad392a2b16f158fb326cb5e1367b4d` and preserved the concurrent changes
at `cd897ddf3856ffdabef68ba1a71b43dd99efad46`. The separate delivery branch
`feat/ab-runtime-completion-20260911` avoids overwriting the active original branch.

## Published on this branch

A/shared source: serialized native workflows, cancellation/deadlines, read-only
reconciliation, exact resource grants, session/account isolation, multiple MCP
accounts, bounded schema-checked HTTP transport, completed CLI/MCP lifecycle,
account reservation idempotency and shared owned-process I/O utilities.
Ten additional A regression tests accompany the changes.

The B metrics module is present but is not wired into the restored B runtime.
B's ordinary runtime, relay, gateway and optional worker modules otherwise retain
the earlier implementation. The physical worker migration and full B continuation
are NOT published on this branch.

## Publication interruption and recovery

The connector blocked a four-file B dependency batch for a safety review, without
identifying the responsible file. No alternative route or encoded upload was used.
The blocked batch was not committed. Its dependent B supervisor changes, briefly
committed as `faba62f526d7a4d0b5d1d16adf70ed9cd45d13c2`, were restored by
`d96ebbd8c1840f2412356b478baafed4de700e8d` so this branch has no missing imports.
This was repository-source rollback, not a change to installed services.

The prepared complete source tree is delivered separately in the chat as
`chatgpt-cost-router-ab-source-20260911.zip`, with tests, documentation, manifests
and logs. That artifact is not a GitHub commit and is not automatically deployed.

## Distinct verification scopes

| Tree/check | Observed result |
| --- | --- |
| Original recovered source | 100 tests passed |
| Initial A/B branch | 124 tests passed |
| Published A/shared subset, reconstructed locally | 134 tests passed, 17.338 seconds |
| Prepared A/B source artifact | 177 run: 176 passed, one SDK smoke skipped, 27.172 seconds |
| Prepared Python wheel | Built offline, installed into an isolated target, seven entry-point help checks passed |

The official SDK smoke was skipped because the pinned optional MCP package was
unavailable in the offline environment. Loopback protocol fixtures are separate.
No 177-test GitHub or CI PASS is asserted. Current CI status must be read directly.

The source artifact adds B supervision/recovery, immutable artifacts, typed gateway,
reliable outbox, enrollment/service templates, release/rollback tooling, packaging
and physical worker separation. These are prepared-source capabilities, not claims
about this branch or the user's installed machines.

## Preserved boundaries

No main merge, deployment, service installation/reload, new user-machine job, T38,
quota-burn test, paid model call, PAIR/Serena installation, Gmail send or Cowboy
publication. No real container-engine enforcement, live SSH lifecycle or native
Chat custom-app attachment was validated by this continuation. Private HTTP
identity mapping and OS isolation remain deployment responsibilities.

Historical receipts and `docs/VALIDATION_STATUS_2026-09-11.md` keep their original
scope. The earlier 100 tests are not the final A/B test count. A locally prepared
file is not a published file, and a generated service template is not a running service.
