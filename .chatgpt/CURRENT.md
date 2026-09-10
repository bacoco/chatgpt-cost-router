# Current project checkpoint

Task: T27 callable worker primitive after T25/T26 Work validation
Status: CORE_SURFACES_VALIDATED — ChatGPT.com Chat, Codex Mac Chat, Codex Mac Work, and Codex CLI local worker now have bounded empirical capability evidence. T26 proves Codex Mac Work can consume a GitHub handoff and create a pushed durable return.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Main SHA observed before T10C2 receipt write: `48c42bdd71ddb00e95104fc695447585b81567dd`
T10A receipt commit: `5575007aaf2d26903bd0e35cf34f6e8b9cd55f21`
T10B receipt commit: `4266e931e8aef7fa9dedfe2016236a97e8067d1e`
T10C1 receipt commit: `aadd31f5b057511a9d9f23683c4aa3f5d7150ed8`
T10C2 receipt: `.chatgpt/test-receipts/T10C2_CODEX_CLI_REPO_RECOVERY_2026-09-10.md`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

## Validated core

- T01-T09: PASS where applicable.
- T14-alt Codex Mac Chat + built-in Gmail: PASS for authenticated read/search/Sent/draft/send, including one deduplicated self-send and user receipt confirmation.
- T15/T16/T16A: PASS for scheduler-associated continuation and fresh/independent GitHub checkpoint recovery.
- T17/T18/T19: PASS for Actions MCP read/control-plane gate and repo-specific scheduler workspace.
- T20/T23/T24: PASS for full ChatGPT Cloud -> GitHub handoff -> real Codex -> GitHub return -> ChatGPT independent verification.
- T21/T22: PASS for workflow skill structure and project-workspace self-bootstrap.
- T10A: PASS for a real Codex CLI terminal session on macOS arm64 with ChatGPT-account login reported by `codex login status`, Codex CLI 0.153.4, git 2.50.1, gh 2.83.1, Python 3.9.6, Node v22.16.0, and creation of one controlled local persistence marker.
- T10B: PASS for a genuinely new independent Codex CLI session rediscovering exactly one marker under HOME without being given its path/hash/content, verifying 100 bytes, no trailing newline, SHA-256 `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`, and the exact content created by T10A.
- T10C1: PASS for a bounded persistent checkout at `/Users/loic/codex-t10-persistence-test/chatgpt-cost-router`, with `main` and `origin/main` both at `230e247cdd838f64a51b745df36fad6a8e73ec71`, clean before/after, 40 unit tests PASS, schema generation PASS, no repo files changed, and external state file SHA-256 `049d0dd34d31cfa72e16e96d8742e90b5d6a650c3a6f42e1714455aa406975f9`.
- T10C2: PASS from a third independent Codex CLI session. It rediscovered exactly one T10C state file and the persistent checkout, matched the recorded local HEAD `230e247cdd838f64a51b745df36fad6a8e73ec71`, reran 40 unit tests and schema generation successfully with no repo changes, then performed exactly one `git fetch origin`; `origin/main` advanced to `48c42bdd71ddb00e95104fc695447585b81567dd` while local HEAD and the clean working tree remained unchanged. This proves safe same-Mac workspace recovery plus live remote reconciliation without overwriting local state.
- T25: PASS for Codex Mac Work characterization: direct GitHub read, Gmail search, local filesystem, shell and Python were actually executed; broad plugins/connectors may be visible/installable but must be distinguished from installed/invokable/executed capabilities.
- T26: PASS after independent GitHub verification. Codex Mac Work read the historical T20 handoff at `be8b29f191b877072e1def641aa3aeec51ec2ab8` and pushed exactly one allowed file on `test/t26-work-return-20260910` in commit `290a40a87511c2696f37dc45fa885ef02bbdf647`; ChatGPT independently verified the commit and one-file diff.

## T13 decision

T13 remains `PARTIAL_STOPPED`, not FAIL. S0 -> S1 showed no observable change at UI precision (99%/100%/100%, credits €0 unchanged). The owner stopped further quota-burning because the displayed granularity is too coarse to justify deliberately consuming allowance.

Receipt: `.chatgpt/test-receipts/T13_MEASUREMENT_STOPPED_2026-09-10.md`.

## T10 current state

- T10 local macOS Codex CLI lane: `PASS`.
- T10A `PASS`: environment/toolchain creation in one real Codex CLI session.
- T10B `PASS`: same-Mac filesystem persistence across a new independent Codex CLI session.
- T10C1 `PASS`: persistent local repository checkout created/reconciled and locally verified with no repository mutation.
- T10C2 `PASS`: a later independent session rediscovered the same workspace, verified the persisted state first, reran 40/40 tests and schema generation, then fetched once and detected that remote `main` had advanced while preserving the local HEAD and clean working tree.
- Distinct Ubuntu/cloud persistent-VM variant: `NOT_YET_FORMALLY_TESTED` and optional; do not infer cross-machine/cloud persistence from this Mac result.

T10 durable receipts:
- `.chatgpt/test-receipts/T10A_CODEX_CLI_ENVIRONMENT_2026-09-10.md`
- `.chatgpt/test-receipts/T10B_CODEX_CLI_PERSISTENCE_2026-09-10.md`
- `.chatgpt/test-receipts/T10C1_CODEX_CLI_REPO_STATE_2026-09-10.md`
- `.chatgpt/test-receipts/T10C2_CODEX_CLI_REPO_RECOVERY_2026-09-10.md`

## Remaining gaps

- T10 local macOS Codex CLI lane: `PASS`; Ubuntu/cloud VM variant remains separately `NOT_YET_FORMALLY_TESTED` and optional.
- T11/T12: `DEFERRED_NOT_JUSTIFIED` as originally defined. The campaign now proceeds with a smaller worker primitive first: make one already-validated Codex CLI session callable non-interactively before designing any daemon/MCP worker.
- T13: `PARTIAL_STOPPED` — preserve S0/S1; do not deliberately burn quota.
- T14 canonical: `BLOCKED_MISSING_CONNECTOR` — Gmail Developer MCP in ChatGPT/Scheduled Tasks remains separate from the validated Codex Mac Gmail route.
- Repository creation from scratch through the tested GitHub Developer MCP remains blocked by observed `403 Resource not accessible by integration`.

## Surface synthesis

`docs/SURFACE_CAPABILITY_MAP.md` is now the concise global map. It separates ChatGPT.com Chat, Codex Mac Chat, Codex CLI terminal, and Codex Mac Work; places GitHub at the centre as durable state/transfer bus; separates allowance/cost pools; and keeps multi-account OpenAI and Claude/other-provider lanes as future explicit handoffs. The original requirements remain in `docs/SURFACE_CAPABILITY_MAP_TODO.md`.

## Next safe action

Run **T27 — callable Codex CLI worker primitive**. The purpose is to prove that an external controller can invoke the already-authenticated Codex CLI non-interactively with `codex exec`, obtain a deterministic bounded result, and do so using ChatGPT-account authentication rather than a paid API key. This is the minimum useful primitive for the future worker mesh. Do not build a daemon, broker, MCP gateway, multi-account rotation, or remote worker until this invocation primitive is proven.

Authoritative status: `docs/VALIDATION_STATUS_2026-09-10.md`.
Beginner entry point: `docs/INSTALLATION_KIT_INDEX.md`.
Surface map: `docs/SURFACE_CAPABILITY_MAP.md`.

Paid OpenAI API used for recorded validations: no.
Hosted GitHub Actions runner used for recorded core validation: no.


T25/T26 durable evidence:
- `.chatgpt/test-receipts/T25_CODEX_MAC_WORK_2026-09-10.md`
- `.chatgpt/test-receipts/T26_WORK_RETURN_VERIFICATION_2026-09-10.md`
- T26 worker commit: `290a40a87511c2696f37dc45fa885ef02bbdf647`
