# Surface capability map — deferred synthesis

Status: TODO after the current validation campaign is finished.

## Goal

Produce one concise global diagram plus a small matrix that makes the execution surfaces understandable at a glance. Do not rely on product naming alone: every capability/cost statement must be tied to empirical evidence or be labelled NOT TESTED / UNAVAILABLE.

## Surfaces to distinguish

1. **ChatGPT.com — Chat**
   - normal interactive chat;
   - Developer MCP access;
   - Scheduled Task entry/continuation where relevant.
2. **Codex Mac — Chat**
   - interactive Codex Mac chat;
   - built-in connectors such as the empirically tested Gmail route;
   - local repository/shell capabilities actually observed.
3. **Codex Mac — Work**
   - keep separate from Codex Mac Chat;
   - test and record capabilities independently rather than inferring them from Chat mode.
4. **GitHub repository — centre of the diagram**
   - durable source of truth;
   - `.chatgpt/` checkpoint/workspace;
   - branch/commit/PR state;
   - Cloud -> Codex `TO_CODEX.md`;
   - Codex -> Cloud `RETURN_FROM_CODEX.md`;
   - receipts/evidence.

## For each surface show

- GitHub read/write/branch/PR capability;
- Scheduled Task access/continuation;
- local shell/Python/test capability;
- Gmail read/draft/send capability;
- ability to consume/produce GitHub handoffs;
- whether repo creation is possible;
- what is PASS, PARTIAL, BLOCKED, DEFERRED or NOT TESTED;
- what state is durable vs ephemeral/local.

## Cost / token legend

Do not collapse all usage into “tokens”. Show separately:

- **ChatGPT plan allowance** — usage inside ChatGPT.com;
- **Codex allowance** — usage in Codex surfaces;
- **GitHub Actions runner allowance/cost** — independent of ChatGPT/Codex;
- **paid API usage** — separate explicit billing path, never inferred from MCP use;
- **external service cost** — if a connector/service itself can incur cost.

Mark “no paid API used” where empirically verified, but do not claim “zero tokens” unless the metric is actually observable.

## Evidence already available

- T01-T09: ChatGPT + GitHub Developer MCP/cloud path.
- T15/T16/T16A/T19: scheduler-associated chat, fresh-chat recovery and repo-backed workspace.
- T17/T18: GitHub Actions control plane vs hosted runner-capacity distinction.
- T20/T23/T24: real ChatGPT Cloud -> GitHub -> Codex -> GitHub -> ChatGPT round trip.
- T14-alt: Codex Mac Chat + built-in Gmail read/search/Sent/draft/send, including one real deduplicated self-send.
- Canonical T14: Gmail Developer MCP in ChatGPT/Scheduled-Task context remains separate.

## Desired final output

One page maximum:

- top: three execution surfaces;
- middle: **GitHub repo = durable state / transfer bus**;
- arrows: only empirically validated flows;
- dashed arrows: not tested / blocked;
- bottom: compact cost/allowance legend;
- side matrix: capabilities by surface with PASS / PARTIAL / BLOCKED / NOT TESTED.

Keep it synthetic enough that a non-technical user can immediately answer: **“Where should I do this task, what can that surface really do, where is the state stored, and what allowance/cost does it consume?”**
