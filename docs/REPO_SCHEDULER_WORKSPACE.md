# One project-repository scheduler as a ChatGPT workspace launcher

**Question:** should an active GitHub project have its own Scheduled Task so the user can open that scheduler's chat and immediately work in the corresponding project context?

**Answer:** yes, for active repositories, with strict limits. Treat it as a **project launcher / UI anchor / automatic refresher**, not as a persistent VM or the only project memory.

## 1. Why this is useful

A dedicated scheduler gives each active repository a recognizable place in ChatGPT:

```text
Scheduler: Loriq workspace
  -> bacoco/Loriq
  -> current GitHub checkpoint
  -> scheduler-result chat
  -> interactive Loriq work

Scheduler: ARGH workspace
  -> bacoco/harness-intelligence
  -> current GitHub checkpoint
  -> scheduler-result chat
  -> interactive ARGH work
```

The user can go to Scheduled Tasks, select the project, open its associated chat and continue from the project's durable checkpoint instead of searching a large general chat history.

## 2. What the scheduler is — and is not

It **is**:

- a stable project-labelled entry point in the ChatGPT UI;
- an automatic trigger when the project has a real cadence;
- a way to refresh GitHub state before the user starts working;
- a way to write/read a compact project checkpoint;
- a bootstrap into an interactive scheduler-result chat.

It is **not** proof of:

- a persistent VM;
- a persistent local checkout;
- unlimited context;
- permanent connector availability;
- free GitHub Actions minutes;
- automatic Codex execution.

GitHub remains the durable source of truth.

## 3. Do not create one for every repository

Create a project scheduler only when at least one of these is true:

- the repo has recurring work;
- the repo is actively developed and the user frequently returns to it;
- a scheduled health/status/triage refresh is useful;
- the scheduler-result chat is materially useful as a project entry point.

Do not create dozens of idle schedulers merely to mirror every GitHub repository. That would recreate the navigation problem inside Scheduled Tasks.

A practical rule is **one scheduler per active project, not one scheduler per repository forever**.

## 4. Recommended project files

For repos that use this pattern, keep a small durable workspace descriptor:

```text
.chatgpt/
  PROJECT.md      # stable purpose, key paths, constraints
  CURRENT.md      # current branch/SHA, active task, blockers, next action
  handoffs/       # transfers to Codex or another execution context
```

The scheduler prompt should stay short and point to these files. Do not paste the whole project manual into the Scheduled Task.

## 5. Recommended scheduler prompt

```text
This Scheduled Task is the ChatGPT workspace launcher for repository `<owner>/<repo>`.

Use only the authorized Developer MCPs for this project. Resolve the repository's
default branch freshly. Read `.chatgpt/PROJECT.md` and `.chatgpt/CURRENT.md` if they
exist, then verify all referenced branch/commit/PR/issue state against GitHub.

If this invocation corresponds to real scheduled project work, execute only the
bounded work authorized by the repository instructions and persist a fresh checkpoint.
If no project work is due, do not invent work; return a concise current-state summary
with the exact next safe action.

Never treat this chat or its local filesystem as the durable project state. Do not
repeat an already verified external effect. Prefer ChatGPT + Developer MCPs. Escalate
to Codex only through a persisted GitHub handoff when a concrete capability boundary
is reached. Never use a paid API silently.
```

Adapt the cadence and authorized effects to the project. A scheduler that only exists as a launcher should not perform expensive work on every recurrence.

## 6. Cadence choices

### Repository with real recurring work

Use the actual business cadence: daily, weekly, etc. The same task can both perform the scheduled stage and act as the project's UI anchor.

### Active repository without meaningful recurrence

Do **not** invent an hourly/daily compute loop solely to keep a chat alive. Prefer either:

- a very light periodic state refresh at a sensible cadence; or
- a one-shot initialization task, if the UI continues to expose its result chat in the target account.

The second behavior should be tested because task/chat retention and UI behavior can change.

### Inactive repository

No dedicated scheduler. Recover in a fresh Chat from `.chatgpt/CURRENT.md` when work resumes.

## 7. What happens when the user opens the scheduler chat

Use a short continuation command:

```text
Continue this project from the current GitHub checkpoint.
Re-read `.chatgpt/PROJECT.md` and `.chatgpt/CURRENT.md`, verify current branch/SHA,
and continue only the remaining work. Use ChatGPT + project Developer MCPs first.
```

This is intentionally different from saying "remember everything from earlier". GitHub state is revalidated each time.

## 8. When the scheduler chat becomes too large

Do not preserve an enormous chat just because it is the named project workspace.

1. write/update `.chatgpt/CURRENT.md`;
2. ensure active issues/PRs and exact SHAs are referenced;
3. open a fresh Chat or replace the workspace chat when useful;
4. recover from GitHub.

The project identity survives because it lives in the repo, not because the conversation is immortal.

## 9. Escalating the project to Codex

When Chat reaches a real capability boundary, the project scheduler/chat should not paste the entire conversation into Codex.

Instead:

```text
scheduler/project chat
  -> update .chatgpt/CURRENT.md
  -> write .chatgpt/handoffs/<task-id>/TO_CODEX.md
  -> commit handoff to GitHub
  -> give Codex the short takeover prompt
```

See `CHATGPT_TO_CODEX_HANDOFF.md`.

When Codex returns, it writes a durable result/commit and the same scheduler chat or a fresh Chat can re-read and verify it.

## 10. Suggested naming convention

Use names that sort naturally:

```text
Repo — Loriq workspace
Repo — ARGH workspace
Repo — Vente aux enchères workspace
Repo — Tech Watch workspace
```

If a project already has a meaningful scheduled task, avoid creating a redundant second scheduler solely for naming. Rename or document the existing task as the project's primary launcher when that does not obscure its business purpose.

## 11. Validation — T19 repo scheduler workspace

For one safe active repository:

1. create/choose the project scheduler;
2. scheduler reads `.chatgpt/PROJECT.md` / `CURRENT.md` and exact main SHA;
3. let it finish;
4. open its associated chat;
5. request one harmless bounded follow-up through GitHub MCP;
6. persist the updated checkpoint;
7. close the chat and later re-open/recover;
8. confirm no hidden local persistence was required.

PASS means the scheduler is a useful reproducible project launcher, not that it creates a special persistent compute environment.

## 12. Decision

Recommended pattern:

```text
one active project
      -> one primary scheduler/workspace entry point when useful
      -> one canonical GitHub project state
      -> many bounded Chat sessions if needed
      -> Codex handoff only for specialist remaining work
```

This gives the organizational benefit the user wants without turning Scheduled Tasks into a second source of project truth.
