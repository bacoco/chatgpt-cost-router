# Canonical project scheduler prompt

This is the ChatGPT project workspace launcher for repository `bacoco/chatgpt-cost-router`.

Use only authorized connectors/apps that are actually available in the current session. Resolve the repository default branch freshly. Read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, and `.chatgpt/SCHEDULER.md`, then verify all referenced branch/commit/PR/issue state against GitHub.

If scheduled work is actually due, execute only the authorized bounded work and persist a fresh checkpoint or receipt in `.chatgpt/`. If no project work is due, do not invent work; return a concise current-state summary and the exact next safe action.

Never treat this chat or its local filesystem as durable project state. Do not repeat an already verified external effect. Prefer native Chat capabilities and authorized connectors. For executable verification, use the current authorized Chat/local runtime when sufficient or an enrolled Fleet profile when a machine is actually required.

GitHub Actions is forbidden: do not create, restore, dispatch, rerun or use `.github/workflows/`, hosted runners or an Actions control connector as execution, validation, recovery or publication. The GitHub Fleet relay is a branch-based transport to a user-level relay and is not GitHub Actions.

If Codex becomes materially useful after a concrete capability boundary is observed, create a persisted Cloud-to-Codex handoff in GitHub and stop at that handoff boundary. Never silently use a paid API.
