# Beginner cloud workflow — turn a Scheduled Task into a longer ChatGPT work session

**Audience:** a person who does not know GitHub, MCP, schedulers, Codex or terminals.

**Purpose:** combine the GitHub Developer MCP setup from `BEGINNER_GITHUB_MCP_SETUP.md` with the user's scheduler-chat technique, while keeping all durable state in GitHub and avoiding Codex/API use unless necessary.

## 1. First complete the GitHub MCP setup

Follow `BEGINNER_GITHUB_MCP_SETUP.md` first.

The essential working setup is:

```text
GitHub — <your-username> TEST
https://api.githubcopilot.com/mcp
OAuth
```

After creation, open the plugin details and click **Actualiser / Refresh** until real GitHub actions appear.

Do not continue merely because OAuth says connected. The reference experiment proved that connected OAuth and discovered tools are separate states.

## 2. Understand the two ChatGPT roles

Use **normal Chat** when you want to work now.

Use a **Scheduled Task** when you need ChatGPT to start automatically later or repeatedly.

The useful combined pattern is:

```text
Scheduled Task starts the work
          |
          v
reads current GitHub state
          |
          v
persists a checkpoint/result
          |
          v
its result appears in a ChatGPT chat
          |
          v
open that chat and continue interactively
```

The scheduler is the trigger. It does not have to be the entire worker.

## 3. Create a safe first Scheduled Task

For a first test, use a repository where a harmless read is acceptable.

Prompt:

```text
Use only the Developer MCP app `GitHub — <username> TEST`.

Repository: <owner>/<repo>

Read the repository root and current main SHA.
Do not modify anything.
Return PASS only if the information is actually retrieved through the Developer MCP.
```

Schedule it once a few minutes in the future.

The reference experiment proved this route works with the custom GitHub Developer MCP.

## 4. Open the scheduler's result chat

After the Scheduled Task finishes, find its result in ChatGPT and open the associated chat.

The user has observed that substantial interactive follow-up work can then be done in that scheduler-related chat.

Use a continuation prompt like:

```text
Continue from the result of the scheduled run.
Re-read current GitHub state before changing anything.
Use GitHub as the durable source of truth.
Do not repeat an external effect that already succeeded.
Use normal ChatGPT + Developer MCPs first.
Do not use Codex or a paid API unless a concrete capability boundary requires it.
```

This technique still needs a formal clean-profile validation, so do not interpret it as a guarantee of hidden persistent compute or unlimited quota.

## 5. Persist a checkpoint before doing a lot of work

Do not rely on the chat transcript as the only state.

For substantial work, ask ChatGPT to persist a compact checkpoint in GitHub containing:

```text
task ID
repository
base branch
base SHA
working branch/current SHA
issue/PR numbers
files already read
files already changed
tests already run
external effects already completed
next safe action
Codex used: yes/no
paid API used: yes/no
```

This lets a later scheduler run or a completely fresh Chat recover safely.

## 6. Do coding directly in ChatGPT before Codex

For a bounded coding task, use:

```text
ChatGPT
 -> GitHub MCP: read code
 -> ChatGPT: reason about the fix
 -> Python/shell in ChatGPT: run feasible tests
 -> GitHub MCP: create branch/commit/PR
 -> GitHub MCP: read the diff back
```

The reference test T09 completed this pattern without Codex and without a paid OpenAI API key.

## 7. Add GitHub Actions control only if useful

Optional Developer MCP:

```text
Name: GitHub Actions — <username> TEST
URL: https://api.githubcopilot.com/mcp/x/actions
Authentication: OAuth
```

After OAuth, open plugin details and click **Actualiser / Refresh**.

Expected tools include:

```text
actions_get
actions_list
actions_run_trigger
get_job_logs
```

These tools can inspect workflows/runs/jobs and request reruns.

## 8. GitHub Actions is a separate budget

ChatGPT does not make GitHub Actions runner time free.

In the reference account, the free GitHub Actions allowance was exhausted. GitHub accepted the workflow objects but never allocated a runner:

```text
runner_id = 0
runner_name = empty
Ubuntu execution = 0 ms
```

The account owner confirmed that remaining free Actions capacity was zero.

Therefore, when Actions capacity is zero, do **not** repeatedly trigger CI. Prefer local ChatGPT verification when it is sufficient.

## 9. Cheapest cloud-first route

Use this order:

```text
1. normal ChatGPT
2. ChatGPT + GitHub Developer MCP
3. Scheduled Task + GitHub Developer MCP when automatic start is needed
4. continue manually in the scheduler-result chat when useful
5. ChatGPT Python/shell for bounded verification
6. GitHub Actions MCP only if GitHub runner capacity exists
7. Codex only after a real capability boundary
8. paid API only by explicit exception
```

The target is not technically zero tokens. The target is to avoid additional metered API spend and unnecessary Codex usage.

## 10. If the scheduler chat gets too long

A very long conversation can become cumbersome. Do not keep it alive only because it contains history.

Instead:

1. persist the latest checkpoint in GitHub;
2. open a fresh Chat;
3. select `GitHub — <username> TEST`;
4. tell ChatGPT only the repo and checkpoint identity;
5. ask it to re-read current state and continue the remaining work.

This is the purpose of the compact checkpoint/handoff pattern.

## 11. Clean-profile test for the scheduler-chat trick

This is T15.

1. create a safe one-shot Scheduled Task;
2. make it read a repository and persist a harmless checkpoint;
3. let it finish;
4. open the scheduler's result chat;
5. manually ask it to continue;
6. make the manual follow-up perform one harmless GitHub write, such as a temporary issue;
7. read the artifact back;
8. close/clean it;
9. record whether the Developer MCP remained callable;
10. verify that no second scheduled run, Codex or paid API was used.

Only then label scheduler-chat continuation **formally verified** for that profile.

## 12. Fresh-chat recovery test

This is T16.

1. persist a checkpoint from a scheduler/manual session;
2. create a brand-new Chat;
3. select the GitHub Developer MCP;
4. provide only the repository and checkpoint path/ID;
5. ask ChatGPT to reconstruct the current state;
6. verify branch/SHA/issues/PRs before continuing.

PASS means the system is not dependent on a giant old chat transcript.

## 13. Things a beginner must not assume

Do not assume:

```text
plugin visible = callable
OAuth connected = tools discovered
scheduler worked once = it will work forever
chat history = durable application state
GitHub Actions MCP = free GitHub runner time
red GitHub workflow = code is broken
GitHub runner quota zero = workflow file deleted
code task = Codex required
```

Each of these assumptions failed or was shown to be unsafe during the reference experiments.

## 14. Where to go next

Finish and measure this cloud lane first.

Only after that should the project build the equivalent **Codex desktop/CLI workflow on macOS** and compare it against the cloud route using the same task, evidence, elapsed time and marginal-cost metrics.
