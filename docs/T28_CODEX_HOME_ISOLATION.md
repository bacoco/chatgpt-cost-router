# T28 — isolated Codex worker identity with CODEX_HOME

Status: `READY`

## Goal

Prove that multiple Codex worker identities can coexist on one machine without manual login swapping by isolating each worker's Codex state under a separate `CODEX_HOME`. This test must not copy credentials between homes or expose tokens.

## T28A — isolation without a second login

From a normal macOS shell:

1. Confirm the default worker still reports `Logged in using ChatGPT`.
2. Create a fresh empty directory `~/codex-worker-homes/openai-B` with owner-only permissions.
3. Run `CODEX_HOME=~/codex-worker-homes/openai-B codex login status`.
4. PASS requires the alternate home to be unauthenticated/not logged in while the default home remains authenticated.
5. Do not copy `auth.json`, cookies, config, tokens, or any credential from the default home.

This proves state/auth isolation, not a second account.

## T28B — optional second authorized account

Only if the owner intentionally has another authorized ChatGPT account to use as a separate worker:

1. Authenticate that account interactively with `CODEX_HOME=~/codex-worker-homes/openai-B codex login`.
2. Do not expose credentials or account identifiers in the receipt; use alias `openai-B`.
3. Confirm both default `openai-A` and isolated `openai-B` report logged-in status when queried with their own homes.
4. Run one bounded read-only `codex exec` under `openai-B` and record model, exit code, reported tokens, and exact worker alias returned.
5. Re-check `openai-A` afterwards to show its auth remains intact.

## Safety / policy

Use only accounts the owner is authorized to use and only within the provider's normal terms and limits. The worker pool is for capability/cost routing and avoiding manual account swapping; it must not be used to evade a suspension, safety enforcement, account restriction, or provider-imposed prohibition. Never store credentials in GitHub.

## PASS rules

- `T28A PASS`: alternate `CODEX_HOME` is demonstrably isolated from the default login.
- `T28B PASS`: two separately authenticated authorized worker homes can each be addressed explicitly and execute independently without overwriting each other's auth state.

T28B is optional until a second account is intentionally supplied.
