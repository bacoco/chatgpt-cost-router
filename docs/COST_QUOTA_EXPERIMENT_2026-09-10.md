# T13 cost / quota experiment — 10 September 2026

Status: `PARTIAL — MEASUREMENT ACTIVE`

This document separates **observed route execution**, **subscription/allowance behavior**, and **incremental paid API cost**. Do not collapse them into one generic “token” number.

`incremental_api_cost_eur=0` below means **no paid OpenAI API was used**. It is not a claim that ChatGPT subscription, Codex allowance, purchased credits, GitHub, electricity, CI, or other external costs are zero.

## Executed route ledger

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
| T20 cloud half | ChatGPT -> exact-SHA `TO_CODEX.md` handoff | no | yes | no | no | no | not captured | handoff authorization | PASS | handoff branch + receipt | 0 |
| T23 | real Codex execution from persisted handoff | no | indirect via GitHub handoff | yes | yes | no | not captured | Python 3 fallback authorization | PASS — 40/40 tests + schema build | return commit `16bb9c9d...` | 0 |
| T24 | ChatGPT verifies Codex return against GitHub | no | yes | no | no | no | not captured | none | PASS | receipts on main | 0 |
| T14-alt | Codex Mac Chat -> built-in Gmail read/draft/send | no | no | no | yes | no | not captured | self-send authorization | PASS | one deduplicated self-email | 0 |

## Official product baseline — not a substitute for measurement

OpenAI Help documentation checked on 2026-09-10 states that, on eligible plans, **Codex, ChatGPT Work, ChatGPT for Excel and Workspace Agents use a shared agentic allowance/credit pool**. Purchased credits can extend supported agentic usage after included limits are exhausted. The exact limits and available credit options are account/plan dependent and must be read from the current Usage dashboard.

References:

- https://help.openai.com/en/articles/11369540 — Using Codex with your ChatGPT plan
- https://help.openai.com/en/articles/12642688 — flexible credits on personal ChatGPT plans

Do **not** infer from those pages that ordinary ChatGPT.com text Chat consumes the same agentic quota. Ordinary Chat is therefore tracked separately in this experiment unless direct account evidence proves otherwise.

## Existing empirical observation

During this campaign the user reported a period where **Codex allowance was exhausted while ordinary ChatGPT conversation work continued**, followed later by Codex becoming available again. This is useful operational evidence that ordinary Chat can remain usable when Codex is unavailable, but by itself it does **not** prove the exact accounting relationship, reset mechanism, conversion rate, or whether another hidden limit was involved.

## T13 measurement model

Record these pools separately:

1. `chatgpt_normal_chat_allowance` — ordinary ChatGPT.com Chat, if a usable metric is exposed;
2. `openai_agentic_allowance` — Codex / Work shared allowance when documented/applicable;
3. `purchased_openai_credits` — explicit flexible-use credits, if present;
4. `github_actions_allowance` — independent runner capacity/cost;
5. `paid_openai_api` — explicit API-key billing only;
6. future account/provider pools (`openai-A`, `openai-B`, `anthropic-A`, etc.) — never assume cross-account sharing.

Unknown or unexposed fields must be recorded as `NOT_OBSERVABLE`, not guessed.

## T13-M1 — single-account matched read task

Purpose: obtain the first before/after empirical usage sample without making repository changes.

Pinned repository state for both surfaces:

```text
repository: bacoco/chatgpt-cost-router
commit: 0cb7ff63464258fd9484db2f1485df4dd6b2bd73
```

Matched task definition:

```text
At exact commit 0cb7ff63464258fd9484db2f1485df4dd6b2bd73 of
bacoco/chatgpt-cost-router, read README.md, .chatgpt/CURRENT.md, and
docs/VALIDATION_STATUS_2026-09-10.md.

Return exactly five facts:
1. T20 status;
2. T13 status;
3. canonical T14 status;
4. T14-alt Codex Mac Gmail status;
5. the repository's durable-state role.

Read only. No repository mutation, no Actions, no paid API.
```

Run it once in **ChatGPT.com Chat** and once in **Codex Mac Chat** using the same account first. Do not deliberately increase reasoning or repeat the task merely to burn quota.

### Required before/after capture

For each surface, record when observable:

```text
account_alias
surface
mode
model
local_timestamp
agentic_allowance_before
agentic_allowance_after
credit_balance_before
credit_balance_after
reset_time_before
reset_time_after
per_chat_usage_if_shown
normal_chat_usage_metric_if_shown
result_correct=yes/no
paid_API_used=no
```

For Codex CLI, `/status` may be used when available. For Codex/Work desktop, use the product Usage display if it exposes per-chat or allowance information. For ordinary ChatGPT.com Chat, record `NOT_OBSERVABLE` for any usage field the UI does not expose.

## T13-M2 — Work comparison

After M1, repeat the same pinned read task once in **Codex Mac Work / ChatGPT Work** if available. Because OpenAI currently documents Work and Codex as sharing the agentic allowance on eligible plans, the experiment should test whether the account Usage display changes consistently. Do not infer Work behavior from Codex behavior without this actual run.

## T13-M3 — multi-account/provider extension

Deferred to the surface-map campaign. Repeat equivalent bounded tasks with account aliases such as `openai-A`, `openai-B`, and later a Claude/Anthropic account. GitHub remains the transfer bus. Never store credentials or personal account identifiers in receipts.

## Completion rule

T13 can become `PASS` only when at least one reproducible before/after allowance measurement is captured for the relevant agentic surface and the conclusion is limited to what that measurement proves. If the product does not expose a numerical metric, T13 remains `PARTIAL` with a documented `NOT_OBSERVABLE` limitation rather than inventing token consumption.
