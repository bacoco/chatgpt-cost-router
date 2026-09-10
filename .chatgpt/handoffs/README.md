# Handoffs

One directory per logical transferred task:

```text
.chatgpt/handoffs/<task-id>/
  TO_CODEX.md
  handoff.json          # optional Surface Handoff v2 packet
  RETURN_FROM_CODEX.md
```

The Markdown artifacts are human-readable transfer records. Any machine packet must remain consistent with the same task/repository/branch/commit and must not invent missing authorization or evidence.

Never store credentials or unrelated conversation history here.