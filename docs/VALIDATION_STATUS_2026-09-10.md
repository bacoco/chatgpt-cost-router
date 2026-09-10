# Validation status — 10 September 2026

This is the **authoritative current status snapshot**. Historical experiment logs preserve earlier states; when they conflict, use this file plus durable receipts and current GitHub state.

## Status vocabulary

- `PASS`: requested behavior actually executed and verified with observable evidence.
- `PARTIAL_STOPPED`: useful evidence preserved, but further measurement intentionally stopped.
- `BLOCKED_MISSING_CONNECTOR`: required connector unavailable in the tested context.
- `DEFERRED_NOT_JUSTIFIED`: intentionally not built/tested because current evidence does not justify the cost.
- `NOT_YET_FORMALLY_TESTED`: distinct test remains unexecuted.

## Current validated state

```text
T01-T09     ChatGPT/GitHub cloud capabilities                 PASS where applicable
T10         Codex CLI persistent local Mac worker             PASS — A/B/C1/C2
T10-VM      distinct Ubuntu/cloud persistent VM               NOT_YET_FORMALLY_TESTED — optional
T11/T12     original persistent Worker MCP / scheduler lane   DEFERRED_NOT_JUSTIFIED
T13         quota/cost experiment                             PARTIAL_STOPPED
T14         Gmail Developer MCP in ChatGPT/Scheduled Tasks    BLOCKED_MISSING_CONNECTOR
T14-alt     Codex Mac Chat + built-in Gmail                   PASS
T15/T16/16A scheduler-chat continuation / repo recovery       PASS
T17/T18/T19 Actions control gate / repo scheduler workspace   PASS
T20/T23/T24 ChatGPT Cloud -> Codex -> ChatGPT round trip      PASS
T21/T22     workflow skills / project bootstrap               PASS
T25         Codex Mac Work capability characterization        PASS
T26         Codex Mac Work -> pushed GitHub return            PASS — independently reverified
T27         headless callable Codex CLI via codex exec        PASS
T28A        CODEX_HOME auth/state isolation                   PASS
T28B        two distinct authorized account workers           PASS
T29         standalone parallel smoke                         DEFERRED_NOT_JUSTIFIED
T30         two-worker local broker                           PASS — live alias dispatch verified
T31A        quota/budget-aware selection logic                PASS — deterministic local tests
T32         private remote worker over Tailscale Serve        PASS — live second-device dispatch
T33         automatic node registry / cross-node mesh routing PASS — live two-machine auto dispatch

GitHub Actions control plane                                  PASS
GitHub hosted runner allocation                               BLOCKED_EXTERNAL_CAPACITY during observed test
Create repository via tested GitHub Developer MCP             BLOCKED — observed 403
Paid OpenAI API                                               NOT USED
```

## Recent worker evidence

T30 proved a controller can address a specific isolated ChatGPT-authenticated Codex worker by alias without manual account swapping. T31A added deterministic budget-aware selection without a model call.

T32 then proved the private remote primitive end to end. A second Tailscale device resolved and pinged the worker Mac, reached the loopback-only broker through Tailscale Serve, saw only `openai-B`, and remotely dispatched it. The result was `REMOTE_OK`, provider `openai`, model `gpt-6-astra`, 4,610 reported tokens, 6.753 s, exit 0, read-only/ephemeral, with paid-API environment removed. The live caller used the owner's Tailscale identity; a separate external-person identity remains untested.

## T33 — automatic node registration / live cross-node mesh

T33 adds a private control plane and node heartbeat agent. A node advertises only its `.ts.net` Serve endpoint, location, worker aliases, ready/auth state, cost class, priority and optional non-secret budget observations. It does not advertise `CODEX_HOME`, local paths, credentials, token material or email addresses. Runtime owner binding is stored as a SHA-256 value, not the login itself.

Seven isolated T33 tests pass without a model call: identity/endpoint validation; durable registration + TTL expiry; node-id takeover rejection; namespacing/ambiguity; headroom-aware selection; safe cross-node forwarding; and local advertisement redaction. Python compilation and Bash syntax checks also pass.

The live proof then succeeded across two machines. The MacBook heartbeat agent registered node `macbook-pro-de-loic` with worker `openai-B` into the Mac Studio control plane. The control plane reported the node with a fresh heartbeat and exposed `macbook-pro-de-loic/openai-B`. A `run --worker auto` request dynamically selected that mesh worker and returned `MESH_OK` through the remote T32 endpoint. Execution telemetry: provider `openai`, model `gpt-6-astra`, 4,612 reported tokens, 5.888 s, exit 0, read-only/ephemeral, paid-API environment removed.

Therefore T33 is PASS for automatic node registration/discovery and cross-machine automatic dispatch. This single-node live smoke does not yet establish useful load balancing among two simultaneously available worker nodes.

Specification: `docs/T33_MESH_NODE_REGISTRATION.md`.
Receipt: `.chatgpt/test-receipts/T33_MESH_LIVE_2026-09-10.md`.

## Remaining gaps

1. Automatic/reliable live 5-hour and weekly allowance ingestion per account.
2. Separately shared external-user Tailscale identity/ACL smoke when available.
3. Always-on launch/supervision packaging for control plane and nodes.
4. A second simultaneously live worker-bearing node to validate real multi-node selection/load distribution.
5. Useful broker-managed concurrency when an actual workload benefits from it.
6. Claude/other-provider worker adapters plus provider-neutral handoff.
7. Canonical Gmail Developer MCP only if operationally required.
8. Repository creation through the tested GitHub Developer MCP remains blocked by the observed 403.

No paid OpenAI API was used for these validations.
