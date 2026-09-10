# T30 — two-worker broker prototype

Status: `PASS — LIVE TWO-WORKER BROKER PATH VALIDATED`

The first useful broker layer is implemented as:

- `cost_router/workers.py` — registry, safe environment isolation, readiness probe, worker selection, `codex exec` invocation and telemetry parsing;
- `scripts/worker_broker.py` — controller CLI with `list`, `probe`, zero-model `select`, and `run`;
- `examples/workers.json` — non-secret descriptors for `openai-A` and `openai-B`;
- `tests/test_workers.py` — fake-process tests that consume no Codex allowance.

Safety properties:

- each child receives only its selected `CODEX_HOME`;
- known paid API key environment variables are removed before Codex is spawned;
- execution is fixed to `--ephemeral --sandbox read-only`;
- explicit worker selection does not probe unrelated workers;
- `auto` ranks enabled workers by cost class, priority and id, probing until one is ChatGPT-authenticated and ready;
- no credentials, email addresses or auth-derived identifiers are stored in the registry.

Telemetry returned per task: selected worker, provider, model, reported tokens, elapsed seconds, exit code, stdout/stderr, sandbox/ephemeral flags and selection probes.

## Live validation

A real checkout pinned to `d4da83ada93df28bfdc80064c41f532827567880` ran **45/45 repository tests PASS**. Live broker `probe` saw both `openai-A` and `openai-B` ready. Zero-model `select` chose `openai-A`. A real explicit dispatch through the broker to `openai-B` returned `BROKER_OK`, model `gpt-6-astra`, `4,607` reported tokens, `5.527 s`, and exit code `0`. The child had paid-API environment variables stripped, used `read-only` + `ephemeral`, and left the bounded workspace empty.

Durable receipt: `.chatgpt/test-receipts/T30_TWO_WORKER_BROKER_LIVE_2026-09-10.md`.

This proves alias-based local dispatch across two isolated ChatGPT-authenticated Codex workers without manual account swapping. It does **not** yet prove remote transport, concurrent execution, or automatic provider-quota discovery.

T29 standalone parallel smoke remains `DEFERRED_NOT_JUSTIFIED`; useful concurrency can be exercised later through the broker when it serves an operational need.
