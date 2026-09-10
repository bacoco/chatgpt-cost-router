# T30 — live two-worker broker validation

Date: 2026-09-10

Result: `PASS`

A real checkout at pinned commit `d4da83ada93df28bfdc80064c41f532827567880` ran the full repository suite: **45 tests PASS**.

Live broker observations:

- `probe` reported both `openai-A` and `openai-B` ready with ChatGPT authentication;
- zero-model `select` chose `openai-A` and only used `codex login status`;
- an explicit broker dispatch to `openai-B` invoked Codex successfully;
- provider: `openai`;
- model: `gpt-6-astra`;
- reported tokens: `4,607`;
- elapsed time: `5.527 s`;
- exit code: `0`;
- stdout contained the requested `BROKER_OK` / `worker_alias=openai-B` / `paid_api_used=NO` result;
- paid-API environment variables were stripped before invocation;
- sandbox: `read-only`;
- session mode: `ephemeral`;
- the bounded workspace remained empty after execution.

This proves a controller can address a specific isolated ChatGPT-authenticated Codex worker by alias through the broker without manual account swapping. It does not prove remote dispatch, concurrent execution, or live provider-quota discovery.

No email address, token, raw account/user identifier, auth-derived fingerprint, or paid API credential is stored here.
