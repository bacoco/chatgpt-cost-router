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

## Multi-account / multi-provider portability to test

The final map must not assume one OpenAI account or one model provider. Treat account identity, execution surface and provider as independent routing dimensions.

Scenarios to validate later include:

- **ChatGPT account A -> GitHub -> Codex account B** for specialist terminal work;
- **ChatGPT account A -> GitHub -> Codex account B + Codex account C** on separate bounded branches/tasks when parallel work is safe;
- **one Codex account in Mac Chat + another Codex account in CLI/terminal** without assuming shared local/session state;
- **ChatGPT/Codex -> GitHub -> Claude Code / Claude terminal** for a bounded continuation;
- **Claude -> GitHub -> ChatGPT/Codex** return and verification;
- **provider-neutral handoff** where the receiving worker is selected from verified capabilities/quota rather than hard-coded as Codex;
- **fallback on quota exhaustion**: switch account/surface/provider only through an explicit GitHub handoff, never by copying opaque chat state;
- **concurrent multi-worker execution** only on independent branches/operations with explicit ownership, conflict detection and merge/reconciliation rules.

For every multi-account/provider test record:

- source provider + product + mode + account alias (non-secret label only);
- destination provider + product + mode + account alias;
- repository, branch and exact SHA;
- handoff artifact/skill version consumed;
- permissions actually available on each account;
- model/allowance/quota state when observable;
- files/actions authorized and forbidden;
- whether GitHub identity differs from model-account identity;
- tests/results and return artifact;
- collisions/conflicts if another worker moves the branch;
- which allowance or paid-credit pool was consumed.

Never store credentials, session cookies, OAuth tokens or account secrets in GitHub. Account aliases such as `openai-A`, `openai-B`, `anthropic-A` are sufficient for receipts.

### Skill/handoff portability

Do not make `TO_CODEX.md` the only conceptual transfer protocol. Preserve the existing proven Codex path, but design a provider-neutral envelope/skill layer able to instantiate receiver-specific instructions such as:

```text
TO_WORKER.md / handoff.json
  receiver = codex | claude-code | other-verified-worker
  repo + branch + exact SHA
  completed work
  remaining work only
  tests
  authorization / forbidden actions
  expected RETURN_FROM_WORKER.md
```

Receiver-specific skills may adapt tool syntax, but must preserve the same task identity, SHA, scope, evidence and authorization. A return from Claude/Codex/another worker is always a claim that the originating surface re-verifies against GitHub.

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

- **ChatGPT normal-chat plan allowance** — ordinary ChatGPT.com usage;
- **OpenAI agentic allowance / credit pool** — Codex, ChatGPT Work and other eligible agentic features that OpenAI currently documents as sharing a pool on supported plans;
- **per-account allowance** — keep account A/B/C separately measurable; never assume quotas are shared across different accounts;
- **Anthropic/Claude allowance or billing** — separate provider/account pool; measure rather than infer;
- **GitHub Actions runner allowance/cost** — independent of ChatGPT/Codex;
- **paid OpenAI API usage** — separate explicit billing path, never inferred from MCP use;
- **other paid API/provider usage** — e.g. Anthropic API if explicitly enabled;
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

- top: execution surfaces grouped by provider/account/mode;
- middle: **GitHub repo = durable state / transfer bus**;
- arrows: only empirically validated flows;
- dashed arrows: not tested / blocked;
- bottom: compact cost/allowance legend with separate account/provider pools;
- side matrix: capabilities by surface with PASS / PARTIAL / BLOCKED / NOT TESTED.

Keep it synthetic enough that a non-technical user can immediately answer: **“Where should I do this task, what can that surface really do, where is the state stored, which account/provider can take over, and what allowance/cost does it consume?”**
