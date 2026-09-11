# Deployment status — 11 September 2026

Live acceptance is in progress on the feature branch. This file will be finalized with read-back evidence before the main delivery is declared complete.

Runtime under test: `10b3ee3e438d57b210b1155e2dbaf19aac9b00db`. Supplemental skill documents came from the same revision; later source commits improve deployment helpers/documentation without silently replacing installed runtime code.

| Host / surface | Observed state |
| --- | --- |
| MacBook | A and B node services started; 209 tests passed including official MCP; real completion, artifact and cancellation verified. |
| macstudioprod | B node service active with observed PID; real completion, artifact and cancellation verified. |
| macstudio | Installed but not accepted: first smoke is UNCERTAIN with PermissionError; not replayed. |
| Sparky | SSH became unavailable during rollout; not deployed. |
| Omen | SSH connection timed out; not deployed. |
| New relay | Installed; native GitHub queue health check reached the MacBook node. End-to-end terminal read-back is being checked. |
| MCP | Direct loopback initialize passed for A and gateway; complete tools/list/node health receipt is being finalized. |

New services are separate from legacy services. T38 remains paused. Chat account attachment, real multi-connector application workflows, untrusted-container isolation and reboot/rollback acceptance remain separate gates. See [roadmap](ROADMAP.md).
