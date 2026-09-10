# T27 — callable Codex CLI worker primitive receipt

- test: `T27`
- surface: normal macOS Terminal invoking Codex CLI non-interactively
- codex_version: `codex-cli 0.153.4`
- login_status: `Logged in using ChatGPT`
- codex_exec_available: YES
- codex_mcp_subcommand_available: YES — discovered via help only
- codex_mcp_server_available: YES — discovered via help only
- working_directory: `/Users/loic/codex-t27-worker-smoke`
- directory_before: EMPTY
- model: `gpt-6-astra`
- provider: `openai`
- approval: `never`
- sandbox: `read-only`
- reasoning_effort: `low`
- output: exact requested four lines, beginning `WORKER_OK`
- exit_code: `0`
- directory_after: EMPTY
- files_created_or_modified: NO
- tokens_used_reported_by_codex_exec: `10,215`
- paid_api_used: NO

Result: `PASS`.

T27 proves that an ordinary controller process can invoke the already-authenticated Codex CLI as a bounded non-interactive worker with `codex exec`, receive a deterministic result, and leave a read-only workspace unchanged. The reported token count is per-invocation telemetry, not proof of a particular 5-hour/weekly quota decrement.

T27 does not prove remote invocation, multi-account isolation, daemon/MCP-server reliability, concurrent workers, or quota-aware scheduling.
