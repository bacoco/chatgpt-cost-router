# Current project checkpoint

Task: T13 cost / allowance measurement
Status: CORE_ROUND_TRIP_VALIDATED — T13 measurement is now active. Scheduler/chat/GitHub workspace recovery, real Cloud -> Codex -> Cloud handoff, and Codex Mac Chat Gmail read/draft/send are verified.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
T13 protocol commit: `def4cb071f9b6de1c63429dc1c193ea0e90f05e5`
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
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated search/read, Sent search, draft creation/read-back, and one real deduplicated self-send via `Gmail.send_email`; exact subject/Sent state were reverified and the user independently confirmed receipt.
- T13 route ledger: representative no-paid-API ChatGPT/Scheduler/GitHub/Codex/Gmail routes recorded. Empirical before/after allowance measurement remains pending.

## T13 current measurement plan

Canonical measurement document: `docs/COST_QUOTA_EXPERIMENT_2026-09-10.md`.

T13-M1 uses one pinned read-only task on the same OpenAI account in:

1. ChatGPT.com Chat;
2. Codex Mac Chat.

Pinned repository state: `0cb7ff63464258fd9484db2f1485df4dd6b2bd73`.

Capture before/after Usage metrics where observable. Record unavailable metrics as `NOT_OBSERVABLE`; do not infer or fabricate token consumption.

OpenAI documentation checked on 2026-09-10 says Codex, ChatGPT Work and other eligible agentic features share an agentic allowance/credit pool on supported plans. Ordinary ChatGPT.com Chat remains a separately tracked surface in this experiment unless direct account evidence proves otherwise.

T13-M2 will compare Codex Mac Work / ChatGPT Work against the same pinned task if available. Multi-account/provider measurements are deferred to the surface-map campaign.

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

- T10: `NOT_YET_FORMALLY_TESTED` — distinct persistent-VM Codex proof was not run; it remains worth a bounded look after T13.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` — do not build a persistent Codex Worker merely to satisfy test numbers.
- T13: `PARTIAL — MEASUREMENT ACTIVE` — first matched before/after allowance sample is next.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — no Gmail Developer MCP is available in this developer-MCP-restricted ChatGPT conversation. Codex Mac Chat standard Gmail is separately PASS including real send.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by the observed `403 Resource not accessible by integration`.

## Next safe actions

1. T13-M1: capture account Usage baseline, run the pinned matched read task in ChatGPT.com Chat and Codex Mac Chat, then capture Usage again.
2. T13-M2: repeat once in Codex Mac Work / ChatGPT Work if available.
3. T10: run the separate persistent-VM/CLI Codex proof after T13 to characterize what it adds beyond the already-validated Mac/Cloud handoff.
4. Keep T11/T12 deferred unless measured limitations justify a persistent worker.
5. Canonical T14 Developer-MCP Gmail remains optional unless scheduler-native Gmail is operationally required.

## Deferred synthesis task

Create the concise global surface/capability map described in `docs/SURFACE_CAPABILITY_MAP_TODO.md`. It must distinguish ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, and future multi-account/provider lanes; place GitHub in the middle as durable state/transfer bus; support multiple OpenAI accounts and provider-neutral handoffs to/from Claude Code or another verified worker; and show allowance/cost semantics separately by account/provider.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.

Codex used for T23: yes — ChatGPT-account Codex session; no paid API.
Codex Mac Gmail test: yes — standard Gmail connector; one self-addressed email sent and verified; no paid API.
Paid OpenAI API used: no.
Hosted GitHub Actions runner used: no.
