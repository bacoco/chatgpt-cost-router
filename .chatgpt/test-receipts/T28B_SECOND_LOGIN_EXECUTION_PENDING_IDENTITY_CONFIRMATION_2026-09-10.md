# T28B second-login execution — identity confirmation pending

Date: 2026-09-10

Status: `TECHNICAL_PASS_IDENTITY_UNVERIFIED`

Observed from the owner's macOS terminal:

- default worker A: `Logged in using ChatGPT` before/after the B flow;
- isolated `CODEX_HOME=~/codex-worker-homes/openai-B`: initially logged out, then authenticated successfully through `codex login --device-auth`;
- after authentication, both A and B separately report `Logged in using ChatGPT`;
- one bounded `codex exec` under B executed successfully;
- Codex CLI: 0.153.4;
- model: `gpt-6-astra`;
- provider: `openai`;
- sandbox: `read-only`;
- approval: `never`;
- returned `WORKER_OK`, `worker_alias=openai-B`, `surface=codex-exec`, `paid_api_used=NO`;
- reported tokens used: `4,432`;
- exit code: `0`;
- default worker A remained logged in after B execution;
- worker B remained logged in after execution;
- B smoke workspace remained empty;
- no paid API used.

Important boundary: `codex login status` exposes only `Logged in using ChatGPT`; it does not expose a non-secret account identity that lets this test independently distinguish whether A and B are different ChatGPT accounts. Therefore the multi-account claim remains unverified until the owner explicitly confirms that the successful B device-auth flow used a different authorized ChatGPT account than A.

This is not a T28B multi-account PASS yet. It does prove that independently isolated `CODEX_HOME` instances can stay authenticated and callable without overwriting the default worker state.
