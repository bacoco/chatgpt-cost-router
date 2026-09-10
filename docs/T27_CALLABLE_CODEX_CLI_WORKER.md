# T27 — callable Codex CLI worker primitive

Status: `READY`

## Why this test exists

T10 proved that Codex CLI on the Mac is a persistent local engineering environment.
T25/T26 proved Codex Mac Work can read a handoff and push a bounded GitHub return.

The next missing primitive for a worker mesh is **external callability**: can an ordinary controller process launch Codex non-interactively, using the user's existing ChatGPT-account Codex authentication, and receive a deterministic result without opening an interactive Codex session or using a paid API key?

This test deliberately stops before any daemon, MCP gateway, remote networking, multi-account routing, or broker implementation.

## T27A — capability discovery

From a normal macOS shell, outside an interactive Codex session, capture:

```text
codex --version
codex exec --help
codex mcp --help
codex mcp-server --help
codex login status
```

A missing `mcp` or `mcp-server` subcommand is not a T27A failure. The required primitive is `codex exec`.

Do not expose auth tokens or config file contents.

## T27B — one headless invocation

Create/use an empty temporary working directory outside repositories:

`~/codex-t27-worker-smoke`

Then invoke Codex once non-interactively with a read-only sandbox and no repository mutation. Use the CLI's supported `codex exec` syntax from `--help`.

The task sent to Codex must be:

```text
Return exactly:
WORKER_OK
surface=codex-exec
cwd=<actual current working directory>
paid_api_used=NO
Do not modify any file.
```

Requirements:
- ChatGPT-account authentication, not an API key;
- no paid API;
- no GitHub mutation;
- no MCP calls;
- no file writes;
- no approval bypass / no `--dangerously-bypass-approvals-and-sandbox`;
- run exactly once.

Capture exit code and exact stdout/stderr.

## PASS rule

`T27 PASS` requires:
1. `codex exec` is actually available;
2. a normal shell process invokes it non-interactively;
3. invocation succeeds with exit code 0;
4. result contains `WORKER_OK`;
5. no files are changed/created by the task;
6. authentication is the ChatGPT-account Codex login;
7. no paid API key is used.

If `codex exec` requires an unsafe approval bypass, T27 is `BLOCKED`, not PASS.

## What PASS would prove

A controller, scheduler, local service, or future broker can call Codex as a bounded worker primitive without a human entering an interactive Codex session.

It would **not** yet prove:
- remote invocation;
- multi-account isolation;
- daemon reliability;
- MCP-server reliability;
- concurrent workers;
- quota-aware scheduling.

Those become later tests only after T27.
