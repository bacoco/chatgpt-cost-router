# T32 — live private remote worker receipt — 2026-09-10

Status: `PASS`

## Scope

Verify that a second device can reach the loopback-only worker facade through private Tailscale Serve and execute an allowlisted Codex worker on the host Mac without exposing SSH, raw Codex, credentials, filesystem paths, or a paid API path.

## Observed transport

- remote device: second Mac on the same tailnet;
- worker host reachable through MagicDNS and Tailscale ping;
- HTTPS endpoint: Tailscale Serve on dedicated port `8443`;
- `/v1/health`: `ok=true`, `transport=tailscale-serve`;
- `/v1/workers`: only `openai-B` exposed, `ready=true`, `auth=chatgpt`;
- live caller identity was accepted by the server allowlist.

No Tailscale login/email is retained in this receipt.

## Live dispatch

A real remote client request selected `openai-B` and returned:

```text
REMOTE_OK
worker_alias=openai-B
paid_api_used=NO
```

Telemetry:

- provider: `openai`;
- model: `gpt-6-astra`;
- reported tokens: `4,610`;
- elapsed: `6.753 s`;
- exit code: `0`;
- sandbox: `read-only`;
- ephemeral: `true`;
- paid API environment removed: `true`.

## Conclusion

T32 is PASS for a private second-device remote worker call: a client on another Mac can traverse Tailscale Serve, address `openai-B` on the worker host, execute it under the host's isolated ChatGPT-authenticated `CODEX_HOME`, and receive a redacted result/telemetry response.

The live caller used the owner's existing Tailscale identity. A different external person's shared-device/ACL path (for example a partner with a separate Tailscale identity) is not yet empirically tested and remains a separate optional smoke.

Paid OpenAI API used: `NO`.
