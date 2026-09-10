# Current project checkpoint

Task: consolidate validated Cloud/Codex/GitHub and Codex-Mac Gmail capabilities
Status: CORE_ROUND_TRIP_VALIDATED — scheduler/chat/GitHub workspace recovery plus a real bounded ChatGPT Cloud -> Codex -> ChatGPT GitHub handoff round trip are verified. Codex Mac Chat also has a separately verified standard-Gmail route for read/search/Sent/draft/send operations.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before this consolidation write: `b15b3a626eafce63ec82300d1237a9e57cf0836f`
Source-kit SHA used by the workspace bootstrap: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated

- T01-T09: PASS where applicable.
- T15 scheduler-associated-chat continuation: PASS.
- T16 literal fresh-chat recovery: PASS.
- T16A independent-context recovery: PASS.
- T17 Scheduled Task -> GitHub Actions Developer MCP read-only control-plane validation: PASS.
- T18 hosted Actions capability gate: PASS.
- T19 repo-specific Scheduled Task workspace consumption: PASS.
- T20 full ChatGPT Cloud -> Codex -> ChatGPT round trip: PASS.
  - handoff branch: `test/t20-cloud-to-codex-handoff-20260910`
  - handoff commit: `be8b29f191b877072e1def641aa3aeec51ec2ab8`
  - Codex blocked-attempt commit: `de7d7cb6ee5aff2094c8572181d99739f24e3566`
  - final Codex return commit: `16bb9c9dc5d691334c57897d7145df1a16b83d00`
  - T23: PASS — Python 3.9.6, 40/40 tests, `build_schemas` exit 0.
  - T24: PASS — ChatGPT verified exact pushed return, branch history, changed-file scope and absence of a PR.
- T21 workflow skill/frontmatter structure: PASS.
- T22 project-workspace self-bootstrap: PASS.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated search/read, Sent search, draft creation/read-back, and one real deduplicated self-send via `Gmail.send_email`; exact subject/Sent state were reverified and the user independently confirmed receipt. No dedicated safe draft-delete action was exposed for the earlier test draft.
- T13 remains PARTIAL: representative zero-paid-API routes and one real Codex execution are recorded, but allowance/quota-pool interaction remains unmeasured.

## Durable receipts on main

- `.chatgpt/test-receipts/T14_GMAIL_DEVELOPER_MCP_BLOCKED_2026-09-10.md`
- `.chatgpt/test-receipts/T14_CODEX_MAC_GMAIL_2026-09-10.md`
- `.chatgpt/test-receipts/T15_SCHEDULER_CHAT_CONTINUATION_PENDING_2026-09-10.md` — legacy filename; content records PASS
- `.chatgpt/test-receipts/T16_FRESH_CHAT_RECOVERY_2026-09-10.md`
- `.chatgpt/test-receipts/T16A_INDEPENDENT_CONTEXT_RECOVERY_2026-09-10.md`
- `.chatgpt/test-receipts/T17_ACTIONS_MCP_2026-09-10.md`
- `.chatgpt/test-receipts/T19_SCHEDULER_WORKSPACE_2026-09-10.md`
- `.chatgpt/test-receipts/T20_CLOUD_TO_CODEX_HANDOFF_READY_2026-09-10.md`
- `.chatgpt/test-receipts/T22_PROJECT_WORKSPACE_BOOTSTRAP_2026-09-10.md`
- `.chatgpt/test-receipts/T23_CODEX_EXECUTION_2026-09-10.md`
- `.chatgpt/test-receipts/T24_CODEX_RETURN_VERIFICATION_2026-09-10.md`

## Remaining gaps

- T10: `NOT_YET_FORMALLY_TESTED` — distinct persistent-VM Codex proof was not run; T23 proves the real GitHub handoff path, not that persistent-VM design.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — do not build a persistent Codex Worker merely to satisfy test numbers.
- T13: `PARTIAL` — quota/allowance-pool interaction remains unmeasured.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — no Gmail Developer MCP is available in this developer-MCP-restricted ChatGPT conversation. Separately, Codex Mac Chat standard Gmail is empirically PASS for read/search/Sent/draft/send including one real deduplicated self-send; this does not prove scheduler/Developer-MCP Gmail.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by the observed `403 Resource not accessible by integration`.

## Next safe actions

1. Manually delete the exact draft `[T14 TEST] Codex Mac Gmail capability validation` from Gmail Drafts if it is still present; no safe dedicated draft-delete action was exposed in the tested Codex Mac connector.
2. If scheduler/ChatGPT-native Gmail is still required, connect an actual Gmail Developer MCP and test bounded allowlisted operations. Codex Mac Chat is already a validated alternative for read/search/Sent/draft/send.
3. T13: run matched tasks if economic/quota measurement is still desired.
4. T10: run persistent-VM Codex proof only if that architecture remains operationally relevant.
5. Keep T11/T12 deferred unless measured limitations justify a persistent worker.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.

Codex used for T23: yes — ChatGPT-account Codex session; no paid API.
Codex Mac Gmail test: yes — standard Gmail connector; one self-addressed email sent and verified; no paid API.
Paid OpenAI API used: no.
Hosted GitHub Actions runner used: no.