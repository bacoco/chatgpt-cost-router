# T28B — distinct multi-account Codex workers

Status: `PASS`

Two isolated Codex worker homes coexist on the same Mac:

- `openai-A`: default `CODEX_HOME`, ChatGPT-authenticated;
- `openai-B`: `~/codex-worker-homes/openai-B`, separately ChatGPT-authenticated.

The owner locally inspected non-secret identity claims without exposing any token. The local comparison proved that worker A and worker B have **different OpenAI user identities and different account/workspace identities**. Both accounts report plan class `pro`. No email address, token, credential, raw identifier or auth-derived hash is stored in this repository.

Worker B then executed one bounded read-only `codex exec` call successfully with model `gpt-6-astra`, exit code `0`, `4,432` reported tokens, and no work file created. Worker A remained logged in afterwards, and worker B remained logged in under its isolated home.

This proves two distinct authorized ChatGPT accounts can be addressed as separate Codex CLI workers on one Mac without manual account swapping. It does not yet prove concurrent execution, remote dispatch, quota decrement telemetry, or broker scheduling.

Paid API used: no.
