# Capability Router Skill

Choose the lowest-cost surface that can safely and verifiably finish the task.

Priority:
1. CHAT
2. SCHEDULED_CHAT when recurrence is required
3. LOCAL/MCP
4. CODEX
5. WORK
6. EXTERNAL_API

Rules:
- Code does not imply Codex.
- GitHub issue/PR/review does not imply Codex.
- Research does not imply Work.
- Browser UI interaction may imply Work.
- Deep edit/test loops may imply Codex.
- Prefer owned compute for suitable inference/media.
- Never claim a capability without runtime evidence.
- De-escalate back to Chat when expensive capabilities are no longer needed.
