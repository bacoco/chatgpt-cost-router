# T30 — two-worker broker prototype

Status: `IMPLEMENTING`

Implementation branch: `feature/t30-two-worker-broker`

Build the smallest useful local broker around the already validated `codex exec` primitive and the two isolated authorized worker homes from T28B.

Requirements:

- registry contains non-secret worker descriptors only;
- explicit addressing of `openai-A` or `openai-B`;
- `auto` selection probes configured workers and prefers the cheapest enabled ready worker by cost class / priority;
- every Codex process receives only its own `CODEX_HOME`;
- known paid API key environment variables are removed from the child process environment;
- initial prototype runs Codex only with `--ephemeral --sandbox read-only`;
- capture exit code, selected worker, model, provider, reported tokens and elapsed time;
- no daemon, remote listener, credential copying, quota circumvention or GitHub mutation is required;
- unit tests must fake the Codex process and must not consume Codex allowance.

T29 standalone parallel smoke is deferred. Useful concurrency will be tested later through the broker when there is real routing/collision value.
