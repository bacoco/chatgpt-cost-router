# T29 — parallel two-worker smoke

Status: `DEFERRED_NOT_JUSTIFIED`

T28 already proves isolated `CODEX_HOME` state and two distinct authorized OpenAI account identities can coexist and be addressed independently. A dedicated A+B simultaneous smoke would mainly prove process concurrency on one Mac while consuming additional Codex allowance.

Defer that standalone experiment. Concurrency will be exercised later as part of a useful broker/dispatcher workflow, where collision control, separate workspaces and per-worker telemetry have operational value.
