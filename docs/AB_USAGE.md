# A/B operator guide

Start with [installation](INSTALLATION.md) and [current deployment status](DEPLOYMENT_STATUS.md).

## A: native tool workflow

Private `chat.json` binds principal, projects file, state directory, surface and session. Start a new capability context for a new Chat session. The project registry binds resource, connector, account, allowed actions and optional exact arguments.

```bash
chat-operations --config /operator/chat.json projects
chat-operations --config /operator/chat.json catalog
chat-operations --config /operator/chat.json observe --project PROJECT --resource RESOURCE --action ACTION --evidence /operator/actual-observation.json
chat-operations --config /operator/chat.json submit --workflow /operator/workflow.json
chat-operations --config /operator/chat.json next --project PROJECT --run RUN
```

`next` returns one exact native tool invocation and a token. The driver must invoke the actual tool once, save its actual return, and record it. Neither a plan nor a guessed result is evidence.

```bash
chat-operations --config /operator/chat.json record --project PROJECT --run RUN --step STEP --token TOKEN --result /operator/actual-tool-return.json
chat-operations --config /operator/chat.json approve --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json reconcile --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json cancel --project PROJECT --run RUN
chat-operations --config /operator/chat.json events --project PROJECT --run RUN
```

Approval applies to resolved inputs that the owner authorized; it does not bypass connector permissions. Every write needs read-back verification. Record an uncertain timeout as such, then reconcile by reading; never assume it means a send or publication did not occur. Cancellation stops future effects, not effects already completed.

For MCP, call `chat_begin_session` in each conversation and pass its session ID to observation/next/record/reconcile. Pending results from another surface/session are refused. `verify.recover_output` can map a verification response to a lost output, without replaying the mutation.

Optional direct HTTP endpoints bind connector/account/tool mappings in operator policy. Credentials stay in a private header file. This adapter does not extract Chat browser tokens or turn native connectors into freely reusable URLs. Example connector schemas are illustrative; discover real ones.

## B: ordinary process lifecycle

Node policy fixes node identity, principal, state directory, projects and named profiles. Executables, paths and repository bindings are configuration, not job inputs.

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

Use `serve-queue` only for an explicitly authorized node queue. Idempotency keys identify immutable requests. An uncertain job is not permission to restart it. Retrieve and reconcile actual evidence before deciding on new work.

Artifacts return `data_base64`, full-file `sha256`, `verified`, offsets, `next_offset` and `eof`. Continue until EOF, then check the assembled file's size and hash. A changed file is refused. Private artifact bytes must not be published through the GitHub relay.

The profile reads structured input from `FLEET_INPUT_FILE`. It must remain a foreground process. It can emit `FLEET_PROGRESS {"current":1,"total":2}`. `trusted-local` is not an OS sandbox; container profiles need real-engine validation.

## Versioned enrollment

These commands operate on the selected machine, not automatically on the whole fleet:

```bash
fleet-enroll stage --repo /operator/source --root /operator/runtimes --revision FULL_SHA
fleet-enroll verify --release /operator/runtimes/releases/FULL_SHA
fleet-enroll activate --root /operator/runtimes --revision FULL_SHA --node-config /operator/node.json --python /operator/venv/bin/python
```

Activation without `--apply` is a plan. With `--apply`, it switches the active record only when no queued/running/cancelling/uncertain jobs remain; it does not reload services. Activating an older staged revision is the same checked rollback path. Keep the virtualenv interpreter path, not its resolved system-Python symlink target.

```bash
fleet-runtime --config /operator/runtimes/active.json health
fleet-enroll plan-enrollment --gateway /operator/gateway.json --host HOST_ALIAS --release /operator/runtimes/releases/FULL_SHA --node-config /operator/pinned-node.json --python /operator/venv/bin/python --output /operator/enrollment.json
fleet-enroll apply-enrollment --plan /operator/enrollment.json
```

Enrollment rechecks release integrity, node policy and gateway drift. A plan is not live reachability evidence. `render-service` only renders a definition; the owner-operated installer is a separate explicit action. See [relay protocol](FLEET_OPERATOR_RELAY.md) for native Chat fleet access.
