# T28B — distinct multi-account Codex workers

Date: 2026-09-10
Status: PASS

Two isolated Codex worker homes on the same Mac were verified as two different authorized ChatGPT accounts.

Evidence retained without sensitive identity data:
- `openai-A` uses the default Codex home.
- `openai-B` uses a separate `CODEX_HOME`.
- both workers report `Logged in using ChatGPT`.
- a local-only identity comparison verified that both the user identity and account identity differ between A and B; the underlying values, email addresses and authentication material are intentionally not stored in GitHub.
- both accounts reported plan class `pro`.
- worker B executed a bounded read-only `codex exec` successfully with model `gpt-6-astra`, exit 0, 4,432 reported tokens, and no work file created.
- worker A remained authenticated after worker B execution.
- paid API used: NO.

This proves two distinct authorized OpenAI account identities can coexist as separately addressable Codex workers on one Mac without manual account swapping.

Not yet proven: concurrent execution, independent 5-hour/weekly quota decrement, automatic quota-aware routing, or remote dispatch.
