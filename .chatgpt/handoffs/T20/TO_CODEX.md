# T20 — Cloud to Codex handoff

Task ID: `T20`

## Definition of done

Validate the real Codex side of the repository handoff without redoing completed cloud work: Codex fetches and verifies this exact handoff/branch state, performs only the bounded local verification below, and commits `.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md` with exact results and the resulting commit identity. ChatGPT Cloud will later re-read that return artifact and GitHub state for T24.

## Repository identity

- Target repository: `bacoco/chatgpt-cost-router`
- Base branch: `main`
- Base/main SHA when the handoff branch was created: `39a337a61eeb0ddbd9b71b89f0eb80b7aff7b554`
- Working branch: `test/t20-cloud-to-codex-handoff-20260910`
- Working SHA before this TO_CODEX write: `8d934e8f471a17c21f0d02befd14efe693cc167d`
- Source-kit revision: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`
- Related issue: none
- Related PR: none; do not create or merge a PR for this handoff test unless separately authorized.

## Completed work — do not redo

- T01-T09 cloud/GitHub tests passed where applicable.
- T16A independent-context recovery: PASS with receipt on `main`.
- T17 Scheduled Task -> GitHub Actions Developer MCP read validation: PASS with receipt on `main`.
- T18 hosted-runner capability gate: merged via PR #10; reconstructed local suite was reported 40/40 PASS. This does not prove hosted runner availability.
- T19 repo scheduler/workspace validation: PASS with receipt on `main`.
- T21 workflow skill/frontmatter format: PASS.
- T22 self-bootstrap: PASS; PR #9 merged; seven installed workspace/skill paths re-verified on `main`; T22 receipt committed on `main`.
- No Codex, paid OpenAI API, deployment, release, or hosted Actions runner was used to prepare this handoff.

## Files inspected for this handoff

- `.chatgpt/PROJECT.md`
- `.chatgpt/CURRENT.md`
- `.chatgpt/SCHEDULER.md`
- `.chatgpt/HANDOFF_POLICY.md`
- `.agents/skills/cloud-to-codex-handoff/SKILL.md`
- `skills/surface-handoff/SKILL.md` at source-kit SHA
- `docs/HANDOFF_SPEC.md` at source-kit SHA
- `docs/EXECUTION_PROTOCOL.md` at source-kit SHA
- `.chatgpt/test-receipts/T16A_INDEPENDENT_CONTEXT_RECOVERY_2026-09-10.md`
- `.chatgpt/test-receipts/T17_ACTIONS_MCP_2026-09-10.md`
- `.chatgpt/test-receipts/T19_SCHEDULER_WORKSPACE_2026-09-10.md`
- `.chatgpt/test-receipts/T22_PROJECT_WORKSPACE_BOOTSTRAP_2026-09-10.md`

## Files changed by ChatGPT Cloud on this working branch

- `.chatgpt/CURRENT.md` — updated to the T20 handoff boundary.
- `.chatgpt/handoffs/T20/TO_CODEX.md` — this handoff.

## Existing verification evidence

- PR #9: T22 bounded bootstrap, merged.
- PR #10: T18 capability-gate regression test, merged; PR body records reconstructed local suite 40/40 PASS.
- Receipts listed above are durable GitHub evidence for T16A/T17/T19/T22.
- Hosted GitHub Actions runner capacity is unavailable in the current account context; do not use a hosted runner as a substitute for local verification.

## Environment limitation / concrete capability boundary

The user reports that the current Codex token allowance is exhausted. ChatGPT Cloud therefore stops here and does not claim Codex acceptance or execution. The remaining requirement specifically needs a real Codex session to prove T23 and enable T24.

## Remaining work for Codex only

When Codex capacity is available:

1. fetch/reconcile `bacoco/chatgpt-cost-router`;
2. check out `test/t20-cloud-to-codex-handoff-20260910`;
3. verify that this handoff is at the exact handoff commit supplied by ChatGPT Cloud and that the branch has not moved unexpectedly;
4. read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, this file, and `.agents/skills/codex-to-cloud-return/SKILL.md`;
5. make no application-code change for this test;
6. run the required local verification commands below;
7. write and commit `.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md` with status, exact commands/results, resulting branch/commit, blockers if any, and confirmation that scope/authorization were preserved;
8. do not merge, deploy, release, send email, access secrets, trigger GitHub Actions, or use a paid API.

## Required Codex tests

Run from the reconciled checkout and report the exact outcome; do not invent PASS if the environment cannot execute them:

```text
python -m unittest discover -s tests -v
python scripts/build_schemas.py
```

If either command cannot run, return `blocked` with the precise environment reason rather than changing unrelated files.

## Authorization and forbidden actions

Authorized actions are limited to: repository read/fetch on this target, checkout/reconciliation of this working branch, local test execution, and creation/commit of the required return artifact on this same branch.

Forbidden: merging; PR creation unless separately authorized; application-code edits; workflow edits; hosted Actions trigger/rerun; deployment/release; secret access; email; external publication; paid APIs; widening repository scope.

## Expected return artifact

`.chatgpt/handoffs/T20/RETURN_FROM_CODEX.md`

The return must be committed on `test/t20-cloud-to-codex-handoff-20260910` and must reference this handoff commit exactly. ChatGPT Cloud will treat the return as a claim to verify against live GitHub state, not as proof by itself.
