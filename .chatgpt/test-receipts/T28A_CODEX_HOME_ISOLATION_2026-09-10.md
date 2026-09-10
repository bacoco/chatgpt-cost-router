# T28A — CODEX_HOME identity isolation

Date: 2026-09-10
Status: `PASS`

## Purpose

Verify that an alternate `CODEX_HOME` does not inherit the default Codex CLI authentication state, so multiple explicitly addressed worker identities can coexist on one machine without manual login swapping.

## Observed result

```text
default_before: Logged in using ChatGPT
alternate_home: ~/codex-worker-homes/openai-B
alternate_before: empty
alternate_login_status: Not logged in
alternate_status_exit: 1
default_after: Logged in using ChatGPT
alternate_after: tmp/ only
```

No credential, `auth.json`, cookie, token, or configuration was copied from the default Codex home. The isolated status check created only a `tmp` entry in the alternate home.

## Conclusion

`T28A PASS`: `CODEX_HOME` is an effective authentication/state boundary for the tested Codex CLI 0.153.4 environment. The default worker remained authenticated while the alternate worker home remained unauthenticated.

This proves identity/state isolation only. It does **not** prove a second account is authenticated, independent account quotas, concurrent execution, remote execution, or broker routing. Those require later tests.

Paid API used: no.
