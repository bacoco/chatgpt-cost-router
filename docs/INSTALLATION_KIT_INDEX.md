# Installation kit index — start here

This is the entry point for a person who knows nothing about the project.

## What this kit is trying to achieve

Use the ChatGPT cloud environment already available to the user for as much work as possible, and avoid unnecessary Codex or paid API usage.

The preferred order is:

```text
ChatGPT
-> Developer MCPs
-> Scheduled Tasks when automatic start is needed
-> interactive continuation in Chat
-> local ChatGPT Python/shell verification when sufficient
-> GitHub Actions only when GitHub runner quota/capacity is available
-> Codex only after a real capability boundary
-> paid API only by explicit exception
```

## Read these files in this order

### 1. Connect ChatGPT to GitHub

Read:

`BEGINNER_GITHUB_MCP_SETUP.md`

This explains OAuth, the GitHub hosted MCP endpoint, the `Actualiser` step, and safe read/write tests.

Some reference-state blocks inside older documents were written while tests were still in progress. Do not use an old `NOT YET TESTED` line as the current status.

### 2. Learn the combined scheduler + chat workflow

Read:

`BEGINNER_CLOUD_WORKFLOW.md`

This explains how a Scheduled Task can bootstrap work, how to continue in its associated chat, how to persist checkpoints in GitHub, and how to avoid unnecessary Codex use.

### 3. Understand the architecture and routing rule

Read:

`CLOUD_EXECUTION_LANE.md`

This is the current merged cloud technique.

### 4. Check what has actually been proven

Read:

`VALIDATION_STATUS_2026-09-10.md`

**This is the authoritative current PASS / PARTIAL / BLOCKED / DEFERRED snapshot for the 10 September experiment.**

### 5. Read failures before troubleshooting

Read:

`EXPERIMENT_LOG_2026-09-10.md`

then the experiment addenda.

They intentionally preserve failed approaches such as:

- stale LiteSpeed OAuth discovery;
- built-in GitHub/Gmail being forbidden in the tested developer-MCP-restricted context;
- custom GitHub OAuth connected but zero tools before refresh;
- the nonexistent Scan Tools button assumption;
- GitHub secret scanning unavailable without Advanced Security;
- ChatGPT local pip/DNS limitations;
- GitHub Actions runs accepted but no runner allocated because the account's free Actions allowance was exhausted.

Do not erase these failures: they are part of the installation knowledge.

## Current GitHub MCP endpoints validated in the reference account

Main GitHub Developer MCP:

```text
https://api.githubcopilot.com/mcp
```

Optional GitHub Actions Developer MCP:

```text
https://api.githubcopilot.com/mcp/x/actions
```

Authentication used: OAuth.

Current ChatGPT UI recovery when tools are absent:

```text
Create
-> complete OAuth
-> open plugin details
-> Actualiser / Refresh
-> verify real actions appear
```

## Important cost warning

A ChatGPT Developer MCP can control GitHub Actions, but it does not provide free GitHub runner capacity.

If the GitHub Actions allowance/budget is exhausted, prefer the ChatGPT + GitHub MCP + local verification route and do not repeatedly trigger doomed workflows.

## Project workspace and Codex handoff

For an active repository, read:

`REPO_SCHEDULER_WORKSPACE.md`

This describes the optional **one active repo → one primary scheduler/workspace entry point** pattern. The scheduler is a launcher and automatic refresher; GitHub remains durable state. Do not create an idle scheduler for every repository.

When ChatGPT reaches a real capability boundary, read:

`CHATGPT_TO_CODEX_HANDOFF.md`

This makes GitHub the transfer bus from ChatGPT Cloud to Codex. ChatGPT commits a compact handoff containing the exact branch/SHA, completed work, remaining work, tests and constraints; Codex receives a short takeover prompt, verifies GitHub state, completes only the remainder and writes a durable return artifact.

The intended project flow is:

```text
project scheduler / Chat
-> GitHub checkpoint
-> ChatGPT work
-> GitHub handoff when necessary
-> Codex specialist work
-> GitHub return
-> ChatGPT review/continuation
```

## Canonical workflow skills

The repeatable workflow is encoded as repository-backed skills, not only prose prompts:

```text
project-workspace-bootstrap
  -> prepares TARGET_REPO + .chatgpt workspace + project scheduler

cloud-to-codex-handoff
  -> persists remaining work + exact SHA + short Codex prompt

codex-to-cloud-return
  -> returns result/tests/SHA to GitHub for ChatGPT verification
```

All three live under `skills/` and use the existing `surface-handoff` contract for versioned transfer semantics. The simplest human entry point remains `PROJECT_BOOTSTRAP_PROMPT.md`: replace only `TARGET_REPO`.

## Current phase boundary

The ChatGPT cloud lane is empirically validated for authenticated GitHub MCP read/write, Scheduled Task GitHub access, scheduled idempotency, repo-backed workspace consumption, scheduler-associated-chat continuation, literal fresh-chat recovery from GitHub checkpoint state, and one-prompt project self-bootstrap.

The full **ChatGPT Cloud -> Codex -> ChatGPT** handoff is also validated end to end. ChatGPT persisted `TO_CODEX.md` at exact commit `be8b29f191b877072e1def641aa3aeec51ec2ab8`. A real Codex session consumed it, preserved an initial blocked attempt where the `python` alias was absent, then used Python 3.9.6 to run 40/40 unit tests and schema generation successfully. Codex pushed `RETURN_FROM_CODEX.md` at `16bb9c9dc5d691334c57897d7145df1a16b83d00`, after which ChatGPT independently verified the branch history and that both post-handoff commits touched only the return artifact.

The remaining gaps are deliberately narrow:

- Gmail Developer MCP testing for T14 because that connector is not present in this developer-MCP-restricted context;
- T13 quota-pool measurement remains partial;
- T10's distinct persistent-VM proof is not formally tested and should be run only if still operationally relevant;
- T11/T12 remain intentionally deferred until a persistent Codex Worker is justified by measured need;
- repository creation from scratch through the tested Developer MCP remains blocked by the observed 403, while work on existing repositories is validated.

Preserve the completed T20 handoff branch and receipts as evidence. Use `VALIDATION_STATUS_2026-09-10.md` and `.chatgpt/CURRENT.md` for current state rather than historical pending lines in older experiment documents.