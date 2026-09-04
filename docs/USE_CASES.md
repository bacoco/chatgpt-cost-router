# Use Cases

| Use case | Default | Escalate when |
|---|---|---|
| General analysis | Chat | rarely |
| Web research | Chat | interactive browser required |
| GitHub issue | Chat | usually never |
| GitHub PR/review | Chat | large refactor/test loop |
| Coding 1–20 files | Chat + GitHub | local tests dominate |
| Large refactor | Chat first | Codex likely |
| CI diagnosis | Chat + GitHub Actions | local-only repro needed |
| Monitoring | Scheduled Chat | event webhook needed |
| Newsletter | Scheduled Chat | UI-only publication |
| Gmail | Chat/Scheduler | rarely |
| WordPress via app/API | Chat/Scheduler | UI-only admin |
| Python/data | Chat/Scheduler | special compute/network needed |
| Public API GET | Web -> Python | auth/write needed |
| Private API | MCP/app | external backend otherwise |
| SSH/VPS | MCP gateway | Work until gateway exists |
| ComfyUI/Sparky | media MCP | Work/local UI if no gateway |
| Image | Chat | specialized local pipeline |
| Video | media MCP/local | Work if UI-only |
| True subagents | pseudo-agent schedulers | Work/Codex/SDK if synchronous delegation required |
| Local Mac apps/files | limited | Work/Codex Desktop |
