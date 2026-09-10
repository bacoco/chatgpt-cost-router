# T26 — ChatGPT independent verification of Codex Mac Work return

Date: 2026-09-10
Result: `PASS`

## Claimed Work result

Codex Mac Work reported:
- source handoff read: PASS;
- source handoff commit: `be8b29f191b877072e1def641aa3aeec51ec2ab8`;
- destination branch: `test/t26-work-return-20260910`;
- return file: `.chatgpt/test-receipts/T26_WORK_RETURN.md`;
- pushed commit: `290a40a87511c2696f37dc45fa885ef02bbdf647`;
- paid API used: NO.

## Independent GitHub verification from ChatGPT

ChatGPT re-read live GitHub state through `GitHub — bacoco TEST`.

Verified commit:
`290a40a87511c2696f37dc45fa885ef02bbdf647`

Observed commit message:
`test: record T26 Codex Mac Work return [skip ci]`

Observed diff:
- exactly one changed file;
- `.chatgpt/test-receipts/T26_WORK_RETURN.md`;
- status `added`;
- 18 additions;
- no application, test, workflow, or other repository file changed.

The file itself records:
- source repository `bacoco/chatgpt-cost-router`;
- source branch `test/t20-cloud-to-codex-handoff-20260910`;
- source path `.chatgpt/handoffs/T20/TO_CODEX.md`;
- source handoff commit `be8b29f191b877072e1def641aa3aeec51ec2ab8`;
- destination branch `test/t26-work-return-20260910`;
- Work local task directory;
- direct GitHub Contents-API write method;
- `forbidden_effects_performed: NO`;
- `paid_api_used: NO`.

Branch history shows the T26 commit directly above the branch base commit `30ba10b5732d80d473d4d553b90240877eababe3`.

## Conclusion

T26 PASS proves that **Codex Mac Work can consume a GitHub handoff and create a real pushed durable return on a bounded GitHub branch**, and that ChatGPT can independently verify the resulting commit/diff.

It does not prove Work persistence across independent Work sessions and does not imply that every visible/installable plugin is installed or invokable.
