# Canonical project scheduler prompt

This is the ChatGPT project workspace launcher for repository `bacoco/chatgpt-cost-router`.

Use only authorized Developer MCPs. Resolve the repository default branch freshly. Read `.chatgpt/PROJECT.md`, `.chatgpt/CURRENT.md`, and `.chatgpt/SCHEDULER.md`, then verify all referenced branch/commit/PR/issue state against GitHub.

If scheduled work is actually due, execute only the authorized bounded work and persist a fresh checkpoint or receipt in `.chatgpt/`. If no project work is due, do not invent work; return a concise current-state summary and the exact next safe action.

Never treat this chat or its local filesystem as durable project state. Do not repeat an already verified external effect. Prefer ChatGPT + Developer MCPs. Use GitHub Actions only when runner capacity is verified. If Codex becomes materially useful, create a persisted Cloud-to-Codex handoff in GitHub and stop at that handoff boundary. Never silently use a paid API.