# A/B operator guide

## Core install and local verification

Use Python 3.11+ and an operator-controlled virtual environment. `pip install .`
installs the core; `pip install '.[mcp]'` additionally installs the pinned MCP SDK.
No private credentials are read by setup and no service is started.

```bash
python scripts/ab_demo.py --directory /tmp/ab-demo-unique
python scripts/validate_ab.py --output /tmp/ab-validation
```

The demo generates a small project registry, A config, B config and requests using
the current Python path. A uses simulation-only capability records and connectors.
Never copy those records into a real Chat session. B runs an ordinary real process
in the demo directory and records its artifact. The directory must not already exist.

`examples/ab/` contains schema-valid illustrative project/workflow/request documents.
Argument shapes are illustrative: real Gmail/GitHub/Cowboy schemas and read-back
queries must be mapped from actual exposed tools, not guessed from these fixtures.
`schemas/ab-contracts.schema.json` checks interchange shape. Runtime validation,
grants, deadlines, capability expiry and approval checks are still mandatory.

## A native Chat tool loop

The operator creates a private `chat.json` with `version:1`, principal, projects_file,
state_dir, surface and current session. Supported surface names are listed in
`chat_ops/capability_store.py`. Use a new session ID for a new Chat capability context.
The project registry binds connector/resource/account/action and optional exact args.

```bash
chat-operations --config /operator/chat.json projects
chat-operations --config /operator/chat.json catalog
chat-operations --config /operator/chat.json observe --project PROJECT --resource RESOURCE --action ACTION --evidence /operator/actual-observation.json
chat-operations --config /operator/chat.json submit --workflow /operator/workflow.json
chat-operations --config /operator/chat.json next --project PROJECT --run RUN
```

The native driver invokes the exact returned tool/arguments once, using the actual
connector available in that session. Persist its actual return locally, then record:

```bash
chat-operations --config /operator/chat.json record --project PROJECT --run RUN --step STEP --token TOKEN --result /operator/actual-tool-return.json
chat-operations --config /operator/chat.json approve --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json reconcile --project PROJECT --run RUN --step STEP
chat-operations --config /operator/chat.json cancel --project PROJECT --run RUN
chat-operations --config /operator/chat.json events --project PROJECT --run RUN
```

Approval means the user authorized those resolved inputs; it is not a way to
bypass missing connector permissions. Approval and `record` must not be fabricated
from plan text. A mutating timeout must be recorded as an uncertain/error return,
then reconciled by read—not replayed. Cancellation does not undo external effects.

For direct HTTP adapters, `mcp_endpoints` maps operator aliases to HTTPS endpoints
(or loopback HTTP), connector/account and action-to-tool mappings. Optional resource
bindings disambiguate accounts. Credentials live only in a private 0600 header file;
redirects, URL credentials and ambiguous bindings are refused. This adapter does not
obtain Chat's browser tokens or automatically convert native connectors into URLs.

For the A MCP interface, call `chat_begin_session` once in each conversation and
pass its `session_id` to capability observations, `next`, `record` and `reconcile`.
Pending results from another session/surface are rejected. `verify.recover_output`
can explicitly map fields from `verification` into a lost step output after a
successful read-back; this does not repeat the original mutation.

## B independent process lifecycle

The generated demo `node.json` is a working minimal example. Real configuration
fixes node identity, principal, state root, project registry and named profiles.
Executable paths and repository bindings are operator configuration, not job inputs.

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

Use `serve-queue` only when explicitly authorized to start that node's queued jobs.
An idempotency key identifies one immutable request; changing inputs under that key
is rejected. An uncertain job cannot simply be restarted. Retrieve the receipt,
reconcile actual evidence and decide explicitly what new work is authorized.

Artifacts return base64 `data`, full-file SHA256 and a chunk SHA256. Continue at
`next_offset` until `eof`; any changed file is refused. A profile's command must
read structured inputs from `FLEET_INPUT_FILE`. It must not daemonize outside the
owned supervisor. Standard output can contain `FLEET_PROGRESS {"current":1,"total":2}`.

## Exact runtime release and enrollment

These commands operate locally on a chosen target; they do not copy files to or
provision a remote machine. Target paths and an authenticated private gateway are
operator prerequisites. No scheduled workflow or paid model is involved.

```bash
fleet-enroll stage --repo /operator/source --root /operator/runtimes --revision FULL_SHA
fleet-enroll verify --release /operator/runtimes/releases/FULL_SHA
fleet-enroll activate --root /operator/runtimes --revision FULL_SHA --node-config /operator/node.json --python /operator/venv/bin/python
```

The last command plans only. Adding `--apply` explicitly switches `active.json` when
there are no queued/running/cancelling/uncertain jobs. It does not reload any service.
Activating an older staged SHA is the same checked rollback path. Planning may create
an empty node journal if absent; it never starts a job or changes the active record.

```bash
fleet-runtime --config /operator/runtimes/active.json health
fleet-enroll plan-enrollment --gateway /operator/gateway.json --host HOST_ALIAS --release /operator/runtimes/releases/FULL_SHA --node-config /operator/pinned-node.json --python /operator/venv/bin/python --output /operator/enrollment.json
fleet-enroll apply-enrollment --plan /operator/enrollment.json
```

Use the pinned config written by bootstrap (under `runtimes/configs/`) for enrollment,
and the real target paths. The host alias must already exist. Plans recheck release,
node policy and gateway drift; they are not a live reachability proof. Existing
services must be stopped/reloaded through a separate authorized operation.

`fleet-enroll render-service --help` renders a user launchd or systemd definition
using the verified runtime bootstrap. It does not install, enable, load or restart
that definition. Configure log directories, service ownership and authentication
before manual OS installation. Never expose the raw private gateway publicly.
