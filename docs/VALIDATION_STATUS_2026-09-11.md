# Validation status — 11 September 2026

This is the **current authoritative status snapshot**. Older dated status files and experiment logs are historical when they conflict with this file plus durable receipts and current `main`.

## Status vocabulary

- `PASS`: requested behavior actually executed and verified with observable evidence.
- `PARTIAL_STOPPED`: useful evidence preserved, but further measurement intentionally stopped.
- `BLOCKED_MISSING_CONNECTOR`: required connector unavailable in the tested context.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built/tested because current evidence does not justify the cost.
- `NOT_YET_FORMALLY_TESTED`: distinct test remains unexecuted.

## Current validated state

```text
T01-T09     ChatGPT/GitHub cloud capabilities                 PASS where applicable
T10         Codex CLI persistent local Mac worker             PASS
T10-VM      distinct Ubuntu/cloud persistent VM               NOT_YET_FORMALLY_TESTED
T11/T12     original persistent Worker MCP / scheduler lane   DEFERRED_NOT_JUSTIFIED
T13         quota/cost experiment                             PARTIAL_STOPPED
T14         Gmail Developer MCP in scheduled context          BLOCKED_MISSING_CONNECTOR
T14-alt     Codex Mac Chat + built-in Gmail                   PASS
T15-T28B    scheduler/handoff/CLI/account isolation proofs     PASS where recorded
T29         standalone parallel smoke                         DEFERRED_NOT_JUSTIFIED
T30         two-worker local broker                           PASS
T31A        quota/budget-aware selection logic                PASS — live quota ingestion unproven
T32         private remote worker over Tailscale Serve        PASS
T33         automatic node registry / cross-node routing      PASS
T34         macOS LaunchAgent supervision/recovery            PASS
T35A        Fleet Operator SSH/MCP + GitHub relay code         PASS
T35B        autonomous Fleet Operator GitHub relay             PASS
T36         two live worker nodes / automatic selection        PASS
T37         Fleet read semantics / worker auth quarantine      PASS

GitHub Actions control plane                                  PASS
GitHub hosted runner allocation                               BLOCKED_EXTERNAL_CAPACITY during observed test
Create repository via tested GitHub Developer MCP             BLOCKED — observed 403
Paid OpenAI API                                               NOT USED
```

## T36 live multi-node proof

Fleet Operator autonomously brought `macstudio-worker/openai-A` online beside `macbook-pro-de-loic/openai-B`. Both were simultaneously `ready=true`. A real `run --worker auto` selected the higher-ranked Mac Studio worker and returned exactly `MULTINODE_OK` using `gpt-6-astra`, 4,896 reported tokens, exit 0, read-only/ephemeral, with paid-API environment removed.

Sparky was also inspected. Its cheap `codex login status` looked healthy, but a real task exposed a stale ChatGPT session and failed at authentication. That false-positive liveness finding motivated T37.

Receipt: `.chatgpt/test-receipts/T36_TWO_NODE_MESH_LIVE_2026-09-10.md`.

## T37 live safety hardening

Fleet Operator read mode is now semantic rather than executable-name-only. Interpreters/build tools are refused in `exec_read`; multi-purpose tools are restricted to known read-only forms. The full repository regression suite passed **100 tests** after the change.

After the Fleet services were reloaded, a live `exec_read` attempt using `python3 -c` to write a file was rejected before execution, while `git status --short --branch` succeeded. This proves the read lane remains useful while closing the interpreter bypass.

Worker health is now durable and execution-informed. A real Sparky Codex authentication failure caused `openai-A` to be stored locally as `status=quarantined`, `reason=auth_failure`. A fresh heartbeat advertised `spark-lolo/openai-A` as `ready=false`, `auth=unavailable`, while the MacBook and Mac Studio workers stayed `ready=true`. T37 needed no successful model call.

Receipt: `.chatgpt/test-receipts/T37_FLEET_READ_AND_WORKER_QUARANTINE_LIVE_2026-09-11.md`.

## Remaining gaps

1. Harden Fleet Operator write execution so shells/interpreters cannot bypass executable-level admin/destructive policy; separate bounded argv writes from any explicitly high-risk shell capability.
2. Automatic/reliable live 5-hour and weekly allowance ingestion per account.
3. Direct ChatGPT MCP app attachment via Secure MCP Tunnel in a supported workspace; current relay already works independently.
4. Separately shared external-user Tailscale identity/ACL smoke when useful.
5. Full logout/login or machine reboot lifecycle recovery for LaunchAgents, if operationally worth testing.
6. Useful concurrent-job/load-distribution behavior.
7. Claude/other-provider worker adapters plus provider-neutral handoff.
8. Canonical Gmail Developer MCP only if operationally required.
9. Repository creation through the tested GitHub Developer MCP remains blocked by the observed 403.

No paid OpenAI API was used for T37. T37's Sparky attempt failed at authentication before a successful model result.
