# Fleet Operator GitHub relay

## Purpose

The relay is the immediate compatibility path when ChatGPT can write GitHub but cannot invoke custom MCP write tools. It lets ChatGPT enqueue a bounded machine operation without making the user paste terminal commands.

```text
ChatGPT GitHub connector
    |
    | .fleet/jobs/<job_id>.json on fleet/commands
    v
Fleet relay LaunchAgent on gateway
    |
    | same FleetRunner allowlists
    v
local / SSH host
    |
    v
fleet/results/<job_id> branch
    |
    v
ChatGPT reads .fleet/results/<job_id>.json
```

## Job contract

Jobs are JSON files at `.fleet/jobs/<job_id>.json` on branch `fleet/commands`.

```json
{
  "version": 1,
  "job_id": "job-20260910-example",
  "host": "worker-1",
  "action": "exec_read",
  "args": {
    "argv": ["git", "status", "--short", "--branch"],
    "cwd": "/allowed/repo"
  },
  "expires_at_unix": 1789069000
}
```

Supported actions are `status`, `exec_read`, `exec_write`, `read_file`, and `git_pull`. `exec_write` still passes through the FleetRunner command allowlist and destructive-command gate.

## Execution semantics

1. fetch only the configured command branch;
2. list only `.fleet/jobs/*.json`;
3. validate version, exact filename/job id, action, args and expiry;
4. skip completed job ids using a local mode-0600 ledger;
5. execute through FleetRunner;
6. write a local mode-0600 result first;
7. push a sanitized result commit to `fleet/results/<job_id>`;
8. only then mark the job complete locally.

If result push fails, the ledger is intentionally left open so the next poll retries instead of silently losing evidence.

## Trust boundary

The command branch is an execution authority. Protect write access to it as carefully as code deployment access. The relay does not execute PR content, issue text or arbitrary branches. It does not make model/API calls. Root/admin commands remain blocked by FleetRunner.

## Result

The result branch contains `.fleet/results/<job_id>.json` with host alias, action, timing, exit status and bounded stdout/stderr. It never contains the SSH target or authentication material.
