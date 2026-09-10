# Handoff policy

GitHub is the durable transfer bus between ChatGPT Cloud and Codex.

For Cloud -> Codex, use `.agents/skills/cloud-to-codex-handoff/SKILL.md` and write `.chatgpt/handoffs/<task-id>/TO_CODEX.md` tied to an exact repository commit.

For Codex -> Cloud, use `.agents/skills/codex-to-cloud-return/SKILL.md` and write `.chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md` tied to the resulting commit.

A handoff preserves, and never expands, the user's authorization. It must preserve repository, branch/SHA, constraints, tests, completed work, remaining work, and evidence. Do not copy the full chat transcript. Do not merge, deploy, release, access secrets, or use paid APIs merely because the receiving surface has those capabilities.