# T13 cost / quota experiment — 10 September 2026

Status: `PARTIAL`

This records representative executed routes without inventing timing or quota evidence that was not captured. `incremental_api_cost_eur=0` below means **no paid OpenAI API was used**; it is not a claim that GitHub, ChatGPT subscription, electricity, CI, or other external costs are zero.

| task_id | route | ChatGPT_only | GitHub_MCP_used | Python_shell_used | Codex_used | paid_API_used | elapsed_time | human_interventions | success_failure | issue_or_PR | incremental_api_cost_eur |
|---|---|---:|---:|---:|---:|---:|---|---|---|---|---:|
| T07 | Scheduled Task -> GitHub Developer MCP read | no | yes | no | no | no | not captured | scheduler creation/setup | PASS | none | 0 |
| T08 | Scheduled Task -> GitHub Developer MCP idempotent write | no | yes | no | no | no | not captured | scheduler creation/setup | PASS | issue #3 marker/cleanup | 0 |
| T09 | ChatGPT -> GitHub MCP bounded patch + local verification | no | yes | yes | no | no | not captured | review/merge authorization | PASS | PR #5 | 0 |
| T16A | independent Scheduled Task -> GitHub checkpoint recovery | no | yes | no | no | no | not captured | scheduler creation/setup | PASS | receipt on main | 0 |
| T17 | Scheduled Task -> GitHub Actions Developer MCP read | no | yes | no | no | no | not captured | scheduler creation/setup | PASS | receipt on main | 0 |
| T18 | ChatGPT -> bounded regression patch -> local reconstructed tests | no | yes | yes | no | no | not captured | merge authorization | PASS | PR #10 | 0 |
| T19 | repo-specific Scheduled Task -> `.chatgpt` workspace -> receipt | no | yes | no | no | no | not captured | scheduler creation/setup | PASS | receipt on main | 0 |
| T22 | ChatGPT -> project workspace bootstrap -> PR/merge -> re-read | no | yes | no | no | no | not captured | merge authorization | PASS | PR #9 | 0 |
| T20 cloud half | ChatGPT -> exact-SHA `TO_CODEX.md` handoff | no | yes | no | no | no | not captured | none after authorization | PASS cloud half / full round trip blocked | handoff branch + receipt | 0 |

## What is not yet measurable

The original T13 also requires empirical comparison of ChatGPT and Codex quota behavior. The user reports the current Codex token allowance is exhausted, so no new Codex execution is performed in this run. Therefore no conclusion is drawn about whether ChatGPT and Codex usage pools are shared, independent, reset together, or have any particular conversion relationship.

T10/T23/T24 remain the next valid sources of Codex-side measurements once capacity returns. Until then, the only supported economic conclusion is that the cloud validations above required no paid OpenAI API key and consumed no Codex execution for the recorded runs.
