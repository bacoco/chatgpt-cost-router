# Current A/B implementation state — September 11, 2026

Repository: `bacoco/chatgpt-cost-router`.
Verified source branch: `feat/ab-products-20260911`.
Verified pre-delivery head: `cd897ddf3856ffdabef68ba1a71b43dd99efad46`.

Core A/B implementation, examples and regression tests have been committed on the
feature branch using the actual GitHub write connector. The earlier ZIP-only delivery
and assertion that writes were unavailable were incorrect. No PR, main merge or
deployment was performed. Fresh local revalidation: 201 tests, 200 passed, no failures
or errors, one optional official MCP SDK test skipped. Evidence is recorded under
`audits/ab-implementation-20260911/`; live acceptance is separate from code delivery.

Implemented: physical worker/mesh separation with compatibility aliases; A workflow
execution/verification/cancellation/recovery; B ordinary job lifecycle, immutable
workspaces, monitoring/results/artifacts; secure typed gateway; durable non-replaying
relay; local enrollment, staged releases, activation/rollback and service rendering;
packaging, examples, schema and regression/failure-injection coverage.

Read `../docs/AB_USAGE.md`, `../docs/AB_VALIDATION.md` and `../docs/ROADMAP.md`. Live native Chat
attachment, actual connector workflows, target SSH/macOS/container behavior and
service installation remain explicit acceptance gates, not inferred PASS results.

**T38 and all existing deployments/services/schedulers remain paused and unchanged.**
No paid API, Codex smoke, real email/publication or job on the owner's machines was
performed to validate this code. Local temporary test processes are not fleet jobs.
