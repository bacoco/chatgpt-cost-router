# T36 — live two-node mesh selection receipt — 2026-09-10

Status: `PASS`

## Objective

Prove, without further user terminal intervention, that the supervised/private mesh can have at least two simultaneously live worker-bearing physical machines and that `--worker auto` makes a real routing choice between them.

## Autonomous control path

All T36 host inspection, installation/start, diagnosis and final verification were issued by ChatGPT through the already-validated Fleet Operator GitHub relay. The user did not execute T36 terminal commands.

## Candidate-node diagnosis

- MacBook remained live as `macbook-pro-de-loic/openai-B`, `included`, priority 20.
- DGX Spark was reachable over Fleet Operator/SSH and had Codex plus a `.codex` home.
- Sparky successfully registered as `spark-lolo/openai-A`, but a real Codex attempt failed with HTTP 401 `refresh_token_reused`. Upgrading Codex from 0.124.0 to 0.154.0 did not repair the stale ChatGPT credential. Sparky was therefore stopped as an active worker node.
- Mac Studio development host had Codex 0.153.2 and `login status` reported ChatGPT authentication. A private worker endpoint and mesh heartbeat were started there as `macstudio-worker/openai-A`.

No credential, refresh token, account email, or auth-derived fingerprint is stored in this receipt.

## Final live inventory

The Mac Studio control plane returned two live ready workers:

- `macstudio-worker/openai-A`: provider `openai`, `included`, priority 10, auth `chatgpt`, quota observations `unknown`.
- `macbook-pro-de-loic/openai-B`: provider `openai`, `included`, priority 20, auth `chatgpt`, quota observations `unknown`.

## Final automatic dispatch

Request: mesh `run --worker auto`, bounded prompt `Return exactly MULTINODE_OK`.

Observed result:

- selected mesh worker: `macstudio-worker/openai-A`
- selected node: `macstudio-worker`
- provider: `openai`
- model: `gpt-6-astra`
- reported tokens: `4,896`
- worker elapsed: `14.644 s`
- exit code: `0`
- output: `MULTINODE_OK`
- sandbox: `read-only`
- ephemeral: `true`
- paid API environment removed: `true`

## Exact claim

T36 proves automatic routing among two simultaneously live worker-bearing physical Macs. The deterministic ranking chose the priority-10 Mac Studio worker over the priority-20 MacBook worker when cost class and quota knowledge were equal.

It does **not** prove:
- concurrent load balancing or throughput scaling;
- reliable live 5-hour/weekly quota ingestion;
- that `codex login status` alone is a sufficient health probe;
- direct ChatGPT custom-MCP write invocation.

Paid OpenAI API used: `NO`.
