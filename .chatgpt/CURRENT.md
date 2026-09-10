# Current project checkpoint

Task: consolidate cloud-first validation after T15/T16
Status: CLOUD_LANE_VALIDATED — scheduler-associated-chat continuation and literal fresh-chat recovery are now both verified; remaining gaps require external Codex capacity, a missing Gmail Developer MCP, or intentionally deferred worker infrastructure

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before T15/T16 receipt writes: `33ca2c8f6934f8217d028900721ad0f9648dd982`
Source-kit SHA used by the workspace bootstrap: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated

- T01-T09: PASS where applicable.
- T15 scheduler-associated-chat manual continuation: PASS; the user continued inside the Scheduled Task's own chat and that same chat successfully read current `main` through `GitHub — bacoco TEST`.
- T16 literal fresh-chat recovery from repository + `.chatgpt/CURRENT.md` only: PASS.
- T16A independent-context recovery from `.chatgpt/CURRENT.md`: PASS.
- T17 Scheduled Task -> `GitHub Actions — bacoco TEST` read-only control-plane validation: PASS.
- T18 hosted Actions capability gate: PASS; PR #10 merged and reconstructed local suite recorded 40/40 PASS.
- T19 repo-specific Scheduled Task workspace consumption: PASS.
- T21 workflow skill/frontmatter structure: PASS.
- T22 project-workspace self-bootstrap: PASS; PR #9 merged, seven installed paths re-verified, receipt persisted.
- T20 Cloud -> Codex handoff generation/read-back: PASS for the cloud half only.
  - branch: `test/t20-cloud-to-codex-handoff-20260910`
  - handoff: `.chatgpt/handoffs/T20/TO_CODEX.md`
  - exact handoff commit: `be8b29f191b877072e1def641aa3aeec51ec2ab8`
- T13 representative no-paid-API route ledger: recorded in `docs/COST_QUOTA_EXPERIMENT_2026-09-10.md`; quota interaction remains partial.

## Durable receipts on main

- `.chatgpt/test-receipts/T14_GMAIL_DEVELOPER_MCP_BLOCKED_2026-09-10.md`
- `.chatgpt/test-receipts/T15_SCHEDULER_CHAT_CONTINUATION_PENDING_2026-09-10.md` — legacy filename retained; content now records PASS
- `.chatgpt/test-receipts/T16_FRESH_CHAT_RECOVERY_2026-09-10.md`
- `.chatgpt/test-receipts/T16A_INDEPENDENT_CONTEXT_RECOVERY_2026-09-10.md`
- `.chatgpt/test-receipts/T17_ACTIONS_MCP_2026-09-10.md`
- `.chatgpt/test-receipts/T19_SCHEDULER_WORKSPACE_2026-09-10.md`
- `.chatgpt/test-receipts/T20_CLOUD_TO_CODEX_HANDOFF_READY_2026-09-10.md`
- `.chatgpt/test-receipts/T22_PROJECT_WORKSPACE_BOOTSTRAP_2026-09-10.md`

## Remaining gaps — do not misreport as failures

- T10: `BLOCKED_EXTERNAL_CAPACITY` — current Codex token allowance exhausted.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — persistent Codex Worker/MCP is optional and should not be built merely to satisfy a test number.
- T14: `BLOCKED_MISSING_CONNECTOR` — this developer-MCP-restricted conversation has no Gmail Developer MCP; a standard Gmail probe was rejected and not used as substitute evidence.
- Full T20 / T23 / T24: `BLOCKED_EXTERNAL_CAPACITY` until a real Codex session can consume the already-persisted T20 handoff and return `RETURN_FROM_CODEX.md` for ChatGPT verification.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by real `403 Resource not accessible by integration` responses.

## Next safe actions

1. Do not regenerate the T20 handoff while branch `test/t20-cloud-to-codex-handoff-20260910` still points to `be8b29f191b877072e1def641aa3aeec51ec2ab8` and remains valid.
2. When Codex capacity returns, execute only the bounded T23 instructions already in `.chatgpt/handoffs/T20/TO_CODEX.md`; then perform T24 by re-reading the return artifact and exact GitHub diff/tests.
3. For T14, connect an actual Gmail Developer MCP before testing the specified safe operations.
4. Keep T11/T12 deferred unless measured cloud limitations make a persistent worker economically or operationally justified.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.

Codex used for this consolidation: no
Paid OpenAI API used: no
Hosted GitHub Actions runner used: no
