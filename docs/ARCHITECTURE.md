# Architecture

```text
User task
  |
  v
Capability Router
  |
  +--> CHAT
  +--> SCHEDULED_CHAT
  +--> LOCAL/MCP
  +--> CODEX / WORK (fallback)
  +--> API (last resort)
```

## Responsibilities
- Apps / MCP / Web = I/O and network
- Python / shell = deterministic compute
- ChatGPT = reasoning/orchestration
- GitHub / Library = persistent state/evidence
- Codex / Work = expensive specialist fallback

## Observed Scheduled Chat capabilities
PASS: Web, public JSON via Web, Python, shell, GitHub read/write, Gmail read/draft, Contacts, Files/Library.
NOT EXPOSED: true subagents, generic parallel primitive.
FAIL: direct Internet from Python/shell.
