# T26 — Codex Mac Work handoff write/return test

Goal: prove that Codex Mac Work can consume a correctly targeted GitHub handoff and produce one bounded return commit/push that ChatGPT independently verifies.

Source handoff:
- repo: `bacoco/chatgpt-cost-router`
- branch: `test/t20-cloud-to-codex-handoff-20260910`
- path: `.chatgpt/handoffs/T20/TO_CODEX.md`
- original handoff commit: `be8b29f191b877072e1def641aa3aeec51ec2ab8`

Test destination:
- dedicated branch: `test/t26-work-return-20260910`
- only allowed new file: `.chatgpt/test-receipts/T26_WORK_RETURN.md`

Required return file fields: surface, source branch/path/commit read, T20 objective summary, Work local pwd, GitHub write method used, forbidden effects, paid API status.

Forbidden: application/test/workflow changes, merge, PR, issue, Actions, Gmail mutation, deploy/release, secrets, paid API.

PASS only if Work actually reads the handoff, writes and pushes exactly the one allowed file on the dedicated branch, and ChatGPT later verifies the live GitHub branch/commit/diff. Tool visibility alone is not PASS.
