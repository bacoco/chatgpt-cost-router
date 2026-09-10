# T13 quota measurement stop receipt

- test: `T13`
- status: `PARTIAL_STOPPED`
- decision: active matched-task quota burn test stopped by owner
- reason: Usage UI exposes coarse percentage buckets; forcing a visible delta would require deliberately consuming material allowance and conflicts with the cost-minimization objective
- S0 general weekly: 99% left
- S1 general weekly: 99% left
- S0 GPT-5.3-Codex-Spark 5h: 100% left
- S1 GPT-5.3-Codex-Spark 5h: 100% left
- S0 GPT-5.3-Codex-Spark weekly: 100% left
- S1 GPT-5.3-Codex-Spark weekly: 100% left
- credits: €0 -> €0
- conclusion: no observable change at UI precision after the ChatGPT.com + GitHub Developer MCP leg; this is not proof of zero compute/token use
- operational assumption: keep ordinary ChatGPT Chat accounting separate from the agentic/Codex pool for routing unless higher-resolution product evidence makes the distinction material
- future revisit: only if higher-resolution telemetry becomes available or a real routing decision depends on it
- paid_API_used: no

T13 remains PARTIAL rather than PASS. The experiment is intentionally stopped, not failed.