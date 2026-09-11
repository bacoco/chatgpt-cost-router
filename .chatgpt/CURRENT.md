# Current project checkpoint

Task: strategic pause — separate Chat orchestration and Fleet Operator
Status: `STRATEGIC_REVIEW_TWO_PROJECTS` — the owner clarified two independent needs: maximize work orchestrated from Chat, and operate/monitor processes across machines, with placement optional. NVIDIA PAIR is the Personal AI Router, not PER/PIR. The proposed split and researched PAIR scope are recorded in `docs/TWO_PROJECTS_AND_PAIR_2026-09-11.md`. No implementation, deployment, or live test is authorized by this documentation-only review.

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`

## Previously validated core — historical evidence, not a new live fleet check

- T01-T34: PASS where recorded, except intentionally deferred/blocked experiments documented in the authoritative status.
- T28A/T28B: PASS for two distinct authorized OpenAI account workers isolated by `CODEX_HOME`.
- T30: PASS for live local broker alias dispatch.
- T31A: PASS for deterministic quota/budget-aware selection logic; provider quota ingestion itself remains unproven.
- T32: PASS for private second-device Tailscale dispatch to `openai-B`.
- T33: PASS for heartbeat registration and cross-machine `--worker auto` mesh dispatch.
- T34: PASS for per-user LaunchAgent supervision and forced-crash recovery without manual restart or model call.
- T35A: CODE COMPLETE / LOCAL TESTS PASS for Fleet Operator.
- T35B: PASS for autonomous ChatGPT -> GitHub relay -> gateway -> host -> GitHub result, including remote SSH/Tailscale execution and a live loopback MCP server.
- T36: PASS for real multi-node automatic selection. `macbook-pro-de-loic/openai-B` and `macstudio-worker/openai-A` were simultaneously ready, and live `--worker auto` selected the priority-10 Mac Studio worker and returned `MULTINODE_OK` using `gpt-6-astra`, 4,896 reported tokens, exit 0, read-only/ephemeral, paid-API environment removed.
- T37: PASS for live safety hardening. The full repository suite passed 100 tests. After reloading Fleet Operator, `exec_read` rejected an attempted `python3 -c` file write before execution while allowing `git status`. A real Sparky Codex authentication failure then persisted `openai-A` as `quarantined/auth_failure`; the next mesh heartbeat advertised `ready=false`, `auth=unavailable`, while the valid MacBook and Mac Studio workers remained `ready=true`.

## Fleet Operator boundary

The gateway resolves only locally configured host aliases. SSH destinations/credentials stay on the gateway. SSH is batch/strict-host-key mode. Runtime policy/config lives outside GitHub with mode `0600`. Read mode is command-aware after T37; the write lane remains broader and is the next safety-hardening target.

The GitHub relay remains the immediately usable execution path from this ChatGPT context. Direct Secure MCP Tunnel/custom-app attachment is separate and does not block autonomous fleet operation.

## Next useful action

Review and approve the two-project boundary before resuming implementation:

1. Chat Orchestration: evidence gathering, reasoning, plans, issues/PRs and other authorized connector actions across projects. Serena is optional code-context tooling; a fleet job is not mandatory.
2. Fleet Operator: node enrollment/access, bounded process execution, supervision, monitoring and results; optional placement across machines and optional Codex/Claude/local-inference adapters. It must also be usable without Chat.
3. Shared contract: project/repository/SHA, authorized operation, run identity, permitted resources/account reference, budget, status and evidence. No credentials in requests or GitHub receipts.

Keep T38 and further installations paused. Do not install PAIR or Serena, move code, split repositories, change services, or submit fleet jobs as part of this review. The broad write-lane risk remains an open issue; this pause does not certify it safe. PAIR is a candidate for local inference only, not a general process manager or subscription-account router. Keep existing test receipts and the authoritative validation snapshot unchanged.

The design stays in the existing repository for review. Separate repositories are a later packaging decision, not a prerequisite for independent responsibilities. Next acceptance scenarios should separately prove (A) a real Chat-to-GitHub project deliverable without an extra model call and (B) an enrolled node running and monitoring a bounded non-LLM task. These are plans, not executed tests.

Fleet Operator spec: `docs/FLEET_OPERATOR_PLUGIN.md`.
Relay spec: `docs/FLEET_OPERATOR_RELAY.md`.
T36 receipt: `.chatgpt/test-receipts/T36_TWO_NODE_MESH_LIVE_2026-09-10.md`.
T37 receipt: `.chatgpt/test-receipts/T37_FLEET_READ_AND_WORKER_QUARANTINE_LIVE_2026-09-11.md`.

Paid OpenAI API use for recorded validation: none. T37 required no successful model call.
