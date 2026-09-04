# Surface Handoff

```json
{
  "version": 1,
  "task_id": "uuid",
  "from_surface": "CHAT",
  "recommended_surface": "CODEX",
  "goal": "Fix X",
  "done": ["root cause isolated"],
  "remaining": ["edit A", "run B"],
  "repo": "owner/repo",
  "files": ["src/a.py"],
  "constraints": ["do not change API"],
  "evidence": ["CI job 123 failed"],
  "tests": ["pytest tests/x.py"],
  "success_criteria": ["all tests pass"],
  "return_to_chat_when": ["implementation and tests complete"]
}
```

Receiving surface verifies current state, avoids unnecessary rediscovery, and returns a compact handoff when specialist work is complete.
