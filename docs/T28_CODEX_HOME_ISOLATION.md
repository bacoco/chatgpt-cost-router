# T28 — isolated Codex worker identity with CODEX_HOME

Status: `T28A PASS — T28B OPTIONAL/NEXT`

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

### T28A empirical result — 2026-09-10

PASS. The default Codex home reported `Logged in using ChatGPT` before and after the test. A fresh `~/codex-worker-homes/openai-B` reported `Not logged in` with exit code `1`; it did not inherit the default login. No credentials were copied. The alternate home contained only a `tmp` entry after the status check. Durable receipt: `.chatgpt/test-receipts/T28A_CODEX_HOME_ISOLATION_2026-09-10.md`.

## T28B — optional second authorized account

Only if the owner intentionally has another authorized ChatGPT account to use as a separate worker:

1. Authenticate that account interactively with `CODEX_HOME=~/codex-worker-homes/openai-B codex login`.
2. Do not expose credentials or account identifiers in the receipt; use alias `openai-B`.
3. Confirm both default `openai-A` and isolated `openai-B` report logged-in status when queried with their own homes.
4. Run one bounded read-only `codex exec` under `openai-B` and record model, exit code, reported tokens, and exact worker alias returned.
5. Re-check `openai-A` afterwards to show its auth remains intact.

### T28B attempt 1 — 2026-09-10

`INCONCLUSIVE_SAME_ACCOUNT`, not PASS. The isolated `openai-B` home was successfully authenticated and executed one bounded `codex exec` call (`gpt-6-astra`, exit 0, 4,432 reported tokens, no work file created) while the default worker remained logged in before and after. However, the owner then confirmed that the browser login used the **same ChatGPT account** as worker A. Therefore this attempt proves concurrent isolated auth state and callability of two `CODEX_HOME` instances, but **does not prove two independent OpenAI accounts or two independent quota pools**.

Before retrying T28B, log out only the isolated worker B and authenticate it deliberately with the second authorized account. Do not change or log out the default worker A.

### T28B attempt 2 — 2026-09-10

`CANCELLED_BEFORE_AUTH`, not PASS and not a failure. Worker B was successfully logged out while worker A remained `Logged in using ChatGPT`. A fresh `codex login --device-auth` flow was started for worker B, but the owner interrupted it before completing browser/device authorization. Final status was therefore: worker A still logged in; worker B `Not logged in`. No second-account claim can be made from this attempt. A new device-auth flow must be started to retry because device codes are one-time and short-lived.

## Safety / policy

Use only accounts the owner is authorized to use and only within the provider's normal terms and limits. The worker pool is for capability/cost routing and avoiding manual account swapping; it must not be used to evade a suspension, safety enforcement, account restriction, or provider-imposed prohibition. Never store credentials in GitHub.

## PASS rules

- `T28A PASS`: alternate `CODEX_HOME` is demonstrably isolated from the default login.
- `T28B PASS`: two separately authenticated authorized worker homes can each be addressed explicitly and execute independently without overwriting each other's auth state.

T28B is optional until a second account is intentionally supplied.
