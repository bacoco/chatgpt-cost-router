# Cloud execution lane — Scheduled Chat + interactive Chat + GitHub MCP

**Scope:** ChatGPT cloud only. The Codex desktop/CLI lane is intentionally deferred to a separate phase.

**Goal:** complete as much useful engineering work as possible inside the already-paid ChatGPT experience, using Developer MCPs and the ChatGPT execution environment before consuming Codex or paid API capacity.

## 1. Why this lane exists

The repository's original 4 September design already contained three useful ideas:

1. standard Chat should be the default execution surface;
2. Scheduled Chat should be the automation engine;
3. a targeted coding task can follow a `Chat -> GitHub -> CI` loop instead of automatically going to Codex.

It also proposed compact handoffs so another execution context would not rediscover an entire conversation.

The 10 September experiments added the missing empirical evidence:

- a custom GitHub Developer MCP can read and write repositories from Chat;
- Scheduled Tasks can call that same GitHub Developer MCP;
- a Scheduled Task can perform a controlled GitHub write and deduplicate the same write on a second run;
- normal Chat can make a bounded repository change, run local verification, create a PR and review it without Codex;
- a separate GitHub Actions Developer MCP can inspect workflow runs and request reruns;
- GitHub Actions execution remains subject to GitHub's own runner/quota/billing availability.

The result is one merged cloud technique rather than separate "scheduler" and "chat" techniques.

## 2. The merged model

```text
                     CHATGPT CLOUD LANE

                  Scheduled Task trigger
                           |
                           v
                  fresh capability check
                           |
                  GitHub Developer MCP
                           |
               read state / write checkpoint
                           |
                           v
                 scheduler-result chat
                           |
             user can continue interactively
                           |
                           v
                    normal Chat work
                  /          |          \
                 /           |           \
                v            v            v
          GitHub MCP     Python/shell   Web/other MCP
                |            |            |
                +------------+------------+
                             |
                  persist evidence/state
                             |
                 optional verification
                             |
              +--------------+--------------+
              |                             |
              v                             v
     GitHub Actions MCP              local Chat tests
     if GitHub quota exists          if sufficient
              |
       status / logs / rerun
              |
              +-------------> Chat correction loop

Codex is an escalation only after a real capability boundary is observed.
```

## 3. Technique A — use the scheduler as a bootstrap, not as the whole worker

A Scheduled Task is especially useful for work that must start automatically or at a known time. It should normally do four things first:

1. resolve current state freshly;
2. verify that the required Developer MCP is callable;
3. perform the smallest useful bounded action or create a durable checkpoint;
4. return a concise status with the exact next action.

Do not force every long task into one scheduled invocation merely because the scheduler started it.

A robust scheduler prompt should point to versioned repository instructions rather than copy a huge operating manual into the task definition.

Preferred shape:

```text
Scheduled Task
  -> resolve repo/main freshly
  -> read canonical instructions at one SHA
  -> load T-1/checkpoint
  -> perform one safe bounded stage
  -> persist receipt/checkpoint in GitHub
  -> report exact state and next action
```

This reduces repeated prompt/context cost and makes interruptions recoverable.

## 4. Technique B — continue inside the scheduler's chat

The user has observed a useful ChatGPT UI workflow: after a Scheduled Task has produced a result, the associated task/run chat can be opened and used for interactive follow-up work.

This is potentially valuable because the scheduled run becomes a **bootstrap into an ordinary interactive work session** instead of the only opportunity to perform work.

Use the follow-up chat like this:

```text
Continue from the exact persisted checkpoint from the last scheduled run.
Re-read current GitHub state before any mutation.
Do not repeat completed external effects.
Use ChatGPT + the selected Developer MCPs first.
Escalate to Codex only if a concrete capability boundary is reached.
```

### Important evidence status

This continuation pattern is **user-observed and operationally useful**, but it has not yet been reproduced as a formal clean-profile test with an explicit receipt proving which context/tool state carries from the scheduled invocation into the manual follow-up.

Therefore do not assume:

- a hidden persistent VM is shared;
- a filesystem survives between scheduled and manual turns;
- connector availability is inherited forever;
- an old capability result remains valid;
- opening the chat grants extra quota or unlimited context.

The durable state is GitHub/checkpoints, not the chat transcript or VM.

## 5. Why the scheduler-chat continuation can save expensive execution

The useful economic pattern is not "a scheduler creates free compute". It is:

```text
scheduler does only what must be scheduled
        +
interactive Chat does reasoning/editing already possible there
        +
Developer MCP provides authenticated external effects
        +
GitHub stores durable state
        +
Codex is not invoked unless needed
```

This can avoid unnecessary Codex launches for tasks that need many reasoning/edit/review turns but do not require a persistent development machine.

The same approach also avoids repeatedly rediscovering repository context if the scheduler persisted a compact receipt containing the exact repo, SHA, files, issue/PR IDs, completed work and next action.

## 6. The cloud coding loop without GitHub Actions

When GitHub Actions quota is unavailable, the preferred lane is:

```text
Chat / scheduler chat
   -> GitHub MCP: read exact files
   -> Chat: reason and create bounded patch
   -> Chat Python/shell: run feasible local tests
   -> GitHub MCP: branch + commit + PR
   -> GitHub MCP: re-read diff
   -> persist verification receipt
```

This lane was exercised on `bacoco/chatgpt-cost-router` without Codex and without a paid OpenAI API key.

A local ChatGPT test result must record its environment and limitations. It must not be mislabeled as an exact GitHub-hosted CI reproduction.

## 7. The cloud coding loop with GitHub Actions available

When the GitHub account has Actions capacity and the repository permits runners:

```text
Chat
 -> GitHub MCP: patch/PR
 -> GitHub Actions MCP: inspect or trigger CI
 -> GitHub runner: execute tests
 -> GitHub Actions MCP: read status/logs
 -> Chat: analyze failures
 -> GitHub MCP: patch again
 -> rerun
```

This is stronger verification than an ephemeral local Chat environment when the hosted workflow accurately models production.

### GitHub Actions is not made free by ChatGPT

The Developer MCP only controls GitHub Actions. Runner execution is governed by GitHub's own allowance, billing, repository policy and runner availability.

Observed 10 September failure mode:

```text
workflow accepted by GitHub
job created
runner_id = 0
runner_name = empty
Ubuntu billable duration = 0 ms
usable execution logs = absent / unavailable
```

The account owner confirmed that the free GitHub Actions allowance had reached zero. The same no-runner pattern existed on the repository's first workflow run, before the later documentation and CI-fix PRs.

Therefore the router must treat:

```text
Actions MCP callable != GitHub runner available
```

as separate capabilities.

## 8. Optional GitHub Actions Developer MCP setup

For a profile that wants GitHub Actions control from ChatGPT, create a second Developer MCP app:

```text
Name:
GitHub Actions — <github-username> TEST

Server URL:
https://api.githubcopilot.com/mcp/x/actions

Authentication:
OAuth
```

Then use the currently observed ChatGPT UI sequence:

```text
Create
-> complete GitHub OAuth
-> open plugin details
-> Actualiser / Refresh
-> verify Actions tools are listed
```

Observed tool surface included:

```text
actions_get
actions_list
actions_run_trigger
get_job_logs
```

Representative capabilities include listing workflows/runs/jobs, reading run/job metadata, retrieving job logs when GitHub produced them, rerunning failed jobs and cancelling runs.

Do not trigger a workflow merely to prove tool visibility when the GitHub Actions allowance is already exhausted.

## 9. Durable-state rule

The chat is a workbench. GitHub is the durable ledger/source of truth.

After each meaningful chunk, persist enough state to recover in another turn, another scheduler invocation or a fresh chat:

```text
run/task ID
repository
base branch
base SHA
working branch
current HEAD SHA
issue / PR IDs
files inspected
files modified
tests executed
test environment
external effects already completed
next safe action
Codex used: yes/no
paid API used: yes/no
GitHub Actions used: yes/no
GitHub runner actually allocated: yes/no
```

A long scheduler chat may become slower or unwieldy. That is not a reason to lose state. Start a fresh chat when useful and reconstruct from the compact GitHub receipt rather than from the entire old conversation.

## 10. Recovery after interruption

Preferred recovery prompt:

```text
Read the current durable checkpoint for <task-id> from <repo>.
Re-read the referenced branch/PR/issue and verify the exact current SHA.
Treat the checkpoint as a claim about prior work, not as proof by itself.
Reconcile any external effect whose outcome could be ambiguous.
Continue only the remaining work.
Do not repeat an already verified effect.
```

This merges the repository's original handoff idea with the later scheduler/checkpoint experiments.

## 11. What the scheduler should not do

Avoid using Scheduled Tasks as pseudo-subagents when true synchronous isolated workers are required.

Avoid giant repeated prompts when the same instructions can live versioned in GitHub.

Avoid assuming a successful connection yesterday is valid today. Preflight at each run and before consequential writes.

Avoid using GitHub Actions as a default verifier when the account has no runner allowance. A failed no-runner workflow adds noise but no evidence.

Avoid pushing a task to Codex solely because it contains code.

## 12. Cost-aware cloud routes

### Route C0 — Chat only

Use for reasoning, architecture, review, static analysis and code generation that requires no external mutation.

### Route C1 — Chat + GitHub MCP

Use for repository reads, issues, bounded edits, branches, commits, PRs and reviews.

### Route C2 — Scheduler + GitHub MCP

Use when the work must start automatically, monitor state, create/update bounded GitHub artifacts or maintain durable checkpoints.

### Route C3 — Scheduler bootstrap + interactive scheduler chat + GitHub MCP

Use when automatic start matters but substantial follow-up can be done interactively in Chat without a persistent coding worker.

This is the key merged technique to validate more rigorously on a clean profile.

### Route C4 — Chat/Scheduler + GitHub MCP + local Python/shell

Use when bounded executable verification fits the ephemeral Chat environment.

### Route C5 — add GitHub Actions MCP

Use only when GitHub runner capacity is currently available and hosted CI adds useful verification.

### Route C6 — Codex escalation

Use only after a concrete remaining requirement cannot be completed efficiently/safely by C0-C5.

### Route C7 — paid API

Explicit exception only.

## 13. New clean-profile tests

### T15 — scheduler-chat continuation

Goal: prove the user's observed "open the scheduler chat and keep working" technique reproducibly.

Procedure:

1. create a one-shot Scheduled Task that reads a safe repo and persists one checkpoint;
2. let it finish;
3. open the resulting scheduler chat from the ChatGPT UI;
4. manually ask it to continue from that exact checkpoint;
5. have the manual follow-up read current GitHub state and perform one harmless bounded action;
6. verify the GitHub artifact and record whether the same Developer MCP was callable;
7. confirm no second scheduled invocation, Codex or paid OpenAI API was used.

PASS requires observable evidence, not merely a long conversation.

### T16 — fresh-chat recovery from GitHub checkpoint

Goal: prove that the long scheduler chat is not required for persistence.

1. persist a checkpoint from a scheduler/manual run;
2. open a completely fresh Chat;
3. select the GitHub Developer MCP;
4. give only the repo + checkpoint identity;
5. reconstruct exact state and continue safely.

PASS means the repo checkpoint is sufficient to resume without copying the old transcript.

### T17 — scheduler -> GitHub Actions MCP read-only

Goal: prove Scheduled Task access to the separate Actions Developer MCP.

A one-shot test has been scheduled/executed in the 10 September experiment, but its detailed returned payload must be captured before declaring this test PASS in the canonical status file.

### T18 — no-runner cost gate

Goal: prevent useless CI triggers when GitHub Actions capacity is zero/unavailable.

The router should obtain current Actions/running capability evidence before choosing the hosted-CI route. If runner capacity is unavailable, select local verification or mark hosted CI blocked rather than repeatedly triggering doomed runs.

## 14. Current cloud-first decision rule

```text
Need work now?
  -> Chat first.

Need automatic start/repetition?
  -> Scheduler triggers it.

Need GitHub state/effects?
  -> GitHub Developer MCP.

Scheduled run produced useful state and more work remains?
  -> persist checkpoint.
  -> continue in scheduler chat when convenient,
     or recover in a fresh chat from the checkpoint.

Need bounded executable verification?
  -> Chat Python/shell if sufficient.

Need hosted CI and GitHub has runner capacity?
  -> GitHub Actions MCP.

Need persistent iterative dev environment / large autonomous loop?
  -> Codex later.

Would any route use a paid API?
  -> stop for explicit authorization.
```

## 15. What is proven vs still only a hypothesis

### Proven in the 10 September experiment

- Chat -> custom GitHub Developer MCP authenticated read.
- Chat -> custom GitHub Developer MCP write.
- Scheduled Task -> custom GitHub Developer MCP read.
- Scheduled Task -> GitHub issue write with second-run deduplication.
- Chat -> bounded change -> local tests -> GitHub PR without Codex.
- Chat -> GitHub Actions Developer MCP can inspect workflow state and request a failed-job rerun.
- GitHub runner unavailability can be distinguished from a project test failure using runner metadata/usage.

### User-observed, useful, but still needs a clean-profile proof

- opening the scheduler's associated chat and using manual follow-ups as a prolonged cloud work session;
- the exact relationship between scheduled-turn context and later interactive-turn context;
- whether all selected Developer MCPs remain callable in that follow-up without reselection.

### Not claimed

- unlimited ChatGPT compute;
- a persistent VM behind scheduler chats;
- zero GitHub Actions cost;
- zero technical token usage;
- automatic Codex entitlement inside GitHub runners;
- persistence of secrets or local files across scheduled/manual sessions.

## 16. Next phase

Finish the cloud lane first:

1. T15 scheduler-chat continuation on a safe repo;
2. T16 fresh-chat recovery from durable GitHub checkpoint;
3. capture T17 Scheduled Task -> Actions MCP result;
4. add a no-runner/Actions-budget gate to router capability evidence;
5. measure representative tasks and actual Codex displacement.

Only then design the equivalent **Codex desktop/CLI lane on macOS** and compare both routes using the same evidence and cost model.
