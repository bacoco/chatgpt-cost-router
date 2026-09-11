# A/B operator guide

Start with [installation](INSTALLATION.md) and [deployment status](DEPLOYMENT_STATUS.md). The [examples](../examples/) contain local configurations and demonstration workflows; replace example bindings with explicit operator policy.

## A: native tool workflow

Private `chat.json` binds principal, projects file, state directory, surface and session. Start a fresh capability context for a new Chat conversation. The project registry binds resource, connector, account, actions and optional exact arguments.

```bash
chat-operations --config /operator/chat.json projects
chat-operations --config /operator/chat.json catalog
chat-operations --config /operator/chat.json observe --project PROJECT --resource RESOURCE --action ACTION --evidence /operator/actual-observation.json
chat-operations --config /operator/chat.json submit --workflow /operator/workflow.json
chat-operations --config /operator/chat.json next --project PROJECT --run RUN
```

`next` returns one exact native invocation and a token. The driver must call the real connector once, save the actual return and record it. A plan or guessed output is not evidence.

```bash
chat-operations --config /operator/chat.json record --project PROJECT --run RUN --step STEP --token TOKEN --result /operator/actual-tool-return.json
chat-operations --config /operator/chat.json approve --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json reconcile --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json cancel --project PROJECT --run RUN
chat-operations --config /operator/chat.json events --project PROJECT --run RUN
```

Approval applies to resolved inputs the owner authorized; it does not bypass connector permissions. Every write needs read-back. A timeout may occur after an effect: reconcile by reading instead of repeating the send or publication. Cancellation stops future effects, not already completed ones.

For MCP, call `chat_begin_session` in each conversation and pass its session ID to observation/next/record/reconcile. Results from another session/surface are refused. A verification's `recover_output` can map a recovered response to a lost output without replaying the mutation.

Optional direct HTTP adapters bind connector/account/tool mappings in private policy. Credentials stay in a private header file. This does not extract Chat browser tokens or turn native connectors into freely reusable URLs. Discover real schemas; examples are not account permissions.

## B: ordinary process lifecycle

Node policy fixes identity, principal, state directory, projects and named profiles. Executables, paths and repository bindings are configuration, not job inputs.

```bash
fleet-jobs --config /operator/node.json profiles --project PROJECT
fleet-jobs --config /operator/node.json submit --request /operator/request.json --start
fleet-jobs --config /operator/node.json status --project PROJECT --run RUN
fleet-jobs --config /operator/node.json logs --project PROJECT --run RUN --stream stdout --offset 0
fleet-jobs --config /operator/node.json result --project PROJECT --run RUN
fleet-jobs --config /operator/node.json artifact --project PROJECT --run RUN --name answer.txt
fleet-jobs --config /operator/node.json cancel --project PROJECT --run RUN
fleet-jobs --config /operator/node.json reconcile --project PROJECT --run RUN
fleet-jobs --config /operator/node.json health
```

Use `serve-queue` only for an authorized node queue. Idempotency keys identify immutable requests; an uncertain result is not permission to start again. Retrieve and reconcile actual receipts before deciding on new work.

Artifacts return `data_base64`, full-file `sha256`, `verified`, offsets, `next_offset` and `eof`. Continue to EOF and check assembled size/hash. A changed file is refused. Do not publish private artifact bytes through GitHub.

A profile reads structured input from `FLEET_INPUT_FILE`, remains a foreground process and can emit `FLEET_PROGRESS {"current":1,"total":2}`. `trusted-local` is not an OS sandbox; container profiles require real-engine validation.

## Versioned enrollment

`fleet-enroll --help` and each subcommand's `--help` describe staging an exact Git SHA, verifying it, planning activation, rendering services and applying enrollment. Operations address the selected installation, not the whole fleet automatically.

Activation requires an idle journal with no queued/running/cancelling/uncertain jobs. Without `--apply` it is a plan; with it, the active record changes but services are not reloaded. An older staged revision uses the same rollback checks. Keep the virtualenv interpreter path, not its resolved system-Python target.

Enrollment checks release integrity, node policy and gateway drift. A configuration plan is not reachability evidence; a rendered service is not a started service. See the [relay protocol](FLEET_OPERATOR_RELAY.md) for native Chat fleet access.
