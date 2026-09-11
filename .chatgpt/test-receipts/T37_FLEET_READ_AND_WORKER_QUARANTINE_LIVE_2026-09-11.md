# T37 — live Fleet read-policy and worker-auth quarantine proof

Date: 2026-09-11
Repository: `bacoco/chatgpt-cost-router`
Baseline before T37: `702fbd2959b894e7e61b4b5fa636d7bfd54febea`
T37 code commit: `d228bb04ead4d129392b4284c54695af8c994166`

## Result

**PASS** for both hardening properties.

## Regression proof

Fleet Operator applied T37 autonomously. The full repository test suite completed **100 tests, all PASS** before the change was committed and pushed to `main`.

## Live Fleet read-mode proof

After reloading Fleet Operator onto T37:

- an `exec_read` attempt using `python3 -c` to create a file was rejected before execution with `read execution forbids interpreter/build tool: python3`;
- `git status --short --branch` in the router checkout remained allowed and returned exit 0.

This proves the read surface is command-aware rather than merely checking the executable name.

## Live worker quarantine proof

Sparky was reused because T36 had already established its stored ChatGPT session could not refresh.

1. Sparky fast-forwarded to T37 and previous local health state was cleared.
2. Its remote worker endpoint was restarted with T37.
3. One bounded call to `spark-lolo/openai-A` failed at authentication and returned HTTP 502; there was no successful model result.
4. Sparky persisted only safe health metadata for `openai-A`: `status=quarantined`, `reason=auth_failure`, plus a timestamp.
5. A fresh mesh heartbeat advertised `spark-lolo/openai-A` with `ready=false`, `auth=unavailable`.
6. The control plane simultaneously kept the two valid workers ready: `macbook-pro-de-loic/openai-B` and `macstudio-worker/openai-A`.

No successful model call was required for T37.

## Boundary

T37 does **not** claim the write surface is fully command-safe. Shell/interpreter execution remains a separate hardening target because it can bypass executable-level classification.
