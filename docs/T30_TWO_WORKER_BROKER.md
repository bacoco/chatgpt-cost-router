# T30 — two-worker broker prototype

Status: `CODE_COMPLETE_LOCAL_TESTS_PASS — REAL TWO-WORKER SMOKE NEXT`

The first useful broker layer is implemented as:

- `cost_router/workers.py` — registry, safe environment isolation, readiness probe, worker selection, `codex exec` invocation and telemetry parsing;
- `scripts/worker_broker.py` — human/controller CLI with `list`, `probe`, zero-token `select`, and `run`;
- `examples/workers.json` — non-secret example descriptors for `openai-A` and `openai-B`;
- `tests/test_workers.py` — fake-process tests that consume no Codex allowance.

Safety properties:

- each child receives only its selected `CODEX_HOME`;
- known paid API key environment variables are removed before Codex is spawned;
- execution is fixed to `--ephemeral --sandbox read-only`;
- explicit worker selection does not probe unrelated workers;
- `auto` ranks enabled workers by cost class, priority and id, probing until one is ChatGPT-authenticated and ready;
- no credentials, email addresses or auth-derived identifiers are stored in the registry.

Telemetry returned per task: selected worker, provider, model, reported tokens, elapsed seconds, exit code, stdout/stderr, sandbox/ephemeral flags and selection probes.

Local verification performed before repository write:

```text
python3 -m unittest discover -s isolated-tests -v
5 tests PASS
python3 -m py_compile workers.py worker_broker.py test_workers.py
PASS
zero-token select with a fake ChatGPT-authenticated Codex binary
PASS — selected openai-A
```

These tests fake the Codex process and therefore prove broker logic, not a live broker-to-worker call. The next bounded step is a live zero-token `select` against both configured homes followed by one real call through the broker to `openai-B`. The `select` command only runs `codex login status`; it does not invoke a model. Do not add concurrency, a daemon, MCP server or remote listener before that path is verified.

T29 standalone parallel smoke remains `DEFERRED_NOT_JUSTIFIED`; useful concurrency will be exercised later through the broker.
