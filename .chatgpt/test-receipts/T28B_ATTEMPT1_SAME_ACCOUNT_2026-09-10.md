# T28B attempt 1 — same-account correction

status: `INCONCLUSIVE_SAME_ACCOUNT`

- default worker A before: `Logged in using ChatGPT`
- isolated worker B before T28A login: separate `CODEX_HOME`, initially unauthenticated
- isolated worker B login: succeeded
- isolated worker B `codex exec`: PASS operationally
- model: `gpt-6-astra`
- sandbox: `read-only`
- exit code: `0`
- reported tokens: `4,432`
- requested alias returned: `openai-B`
- work files created: none observed
- worker A after B call: still `Logged in using ChatGPT`
- worker B after B call: `Logged in using ChatGPT`
- owner correction: worker B was authenticated with the **same ChatGPT account** as worker A
- paid API used: no

Conclusion: this attempt further supports `CODEX_HOME` state isolation and simultaneous callability, but it does **not** prove two distinct OpenAI accounts or independent quota pools. T28B must be retried after logging out only worker B and deliberately authenticating the second authorized ChatGPT account.
