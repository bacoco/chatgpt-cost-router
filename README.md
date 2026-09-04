# ChatGPT Cost & Capability Router

A routing layer whose goal is simple: **do as much work as possible in standard ChatGPT and Scheduled Chat, and use Work / Codex / paid APIs only when they are actually necessary.**

The project exists because the same task can often be completed on several ChatGPT surfaces with very different cost and capability profiles. Without a router, it is easy to send research, GitHub work, monitoring, data processing, or small coding tasks to Codex/Work even when standard Chat could already do them.

The target is to reduce Work/Codex usage substantially — initial working estimate: **~50–80%**, with a central target around **65–70%** — while keeping quality, verification and safety intact. This is a hypothesis to measure, not a billing guarantee.

## The idea in one diagram

```text
                         USER TASK
                             |
                             v
                  +---------------------+
                  | CAPABILITY ROUTER   |
                  | What does the task  |
                  | really need?        |
                  +----------+----------+
                             |
          +------------------+-------------------+
          |                  |                   |
          v                  v                   v
  +---------------+  +----------------+  +----------------+
  | STANDARD CHAT |  | SCHEDULED CHAT |  | LOCAL / MCP    |
  |               |  |                |  |                |
  | research      |  | monitoring     |  | DGX Spark      |
  | GitHub        |  | newsletters    |  | Mac Studio     |
  | small coding  |  | delta T-1 -> T |  | RTX 4090       |
  | review        |  | periodic jobs  |  | ComfyUI        |
  | Python/data   |  | state updates  |  | VPS / APIs     |
  +-------+-------+  +--------+-------+  +--------+-------+
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                     Is something missing?
                              |
                       +------+------+
                       |             |
                      NO            YES
                       |             |
                       v             v
                     DONE    +------------------+
                             | SPECIALIST       |
                             | FALLBACK         |
                             |                  |
                             | CODEX / WORK     |
                             | paid API         |
                             +--------+---------+
                                      |
                                      v
                          Return to Chat when the
                          expensive capability is
                          no longer needed
```

## Core rule

> **Code does not automatically mean Codex.**

The router first asks whether standard Chat already has the required capabilities. For example, if Chat can read/write the repository, create a branch, change a few files, open a PR and let GitHub Actions validate it, there may be no reason to start with Codex.

Likewise:

- research does not automatically mean Work;
- monitoring does not automatically mean an agent;
- image/video/inference does not automatically mean a paid model if owned hardware can do it;
- an authenticated API does not automatically require Python Internet access if an app/MCP can provide the I/O layer.

## What each surface is for

### 1. Standard Chat — default

Use first for:

- research and synthesis;
- Web search;
- GitHub issues, PRs, review and targeted edits;
- small/medium coding tasks;
- reading CI results;
- Python/data analysis;
- Gmail and connected apps;
- planning, architecture and documentation.

The philosophy is: **push Chat until a real capability boundary is reached.**

### 2. Scheduled Chat — automation engine

Use for work that must run automatically:

- hourly/daily monitoring;
- research pipelines;
- changelog/release tracking;
- newsletters;
- delta analysis between T-1 and T;
- periodic GitHub state updates;
- recurring Gmail/report workflows.

Our capability audits observed Scheduled Chat using Web, Python, shell, GitHub read/write, Gmail, Contacts and Files/Library. The router must still check what is actually exposed at runtime instead of assuming every environment has the same tools.

### 3. Local compute / MCP — cheap specialist execution

Before escalating to Work/Codex, prefer owned resources when they fit the task:

```text
Chat / Scheduled Chat
         |
         v
       MCP / App
         |
   +-----+-----------------------------+
   |            |          |           |
   v            v          v           v
DGX Spark   Mac Studio   RTX 4090   VPS / APIs
   |
   v
local LLM / inference / ComfyUI / benchmarks
```

Planned gateways include:

- `machines-mcp` — DGX Spark, Mac Studio, RTX 4090;
- `media-mcp` — Sparky / ComfyUI workflows;
- `vps-mcp` — safe SSH/VPS operations;
- `universal-api-mcp` — authenticated APIs;
- `llm-router-mcp` — delegate only specialist slices to Codex CLI, Claude or local models.

Calling Codex or Claude through MCP does **not** make their usage free. The saving comes from asking them to do only the part that truly needs them.

### 4. Codex — specialist coding fallback

Escalate when coding requires capabilities that become inefficient or unavailable in Chat, for example:

- deep traversal of a large repository;
- a large refactor touching many dependent files;
- long autonomous edit → build → test → debug loops;
- persistent development environment;
- local integration testing that GitHub Actions cannot replace efficiently.

When the implementation/testing phase is complete, the router should send the task back to Chat for research, documentation, release notes, communication, review or follow-up.

### 5. Work — browser/computer/agentic fallback

Use when the task genuinely requires:

- interactive browser/computer use;
- UI-only workflows with no API/app/MCP route;
- complex desktop/local-app interaction;
- long-running agentic execution;
- true multi-agent delegation where that surface provides it.

Work is not the default just because a task is complicated.

### 6. External API — last resort

Use a metered API when a real programmable backend is required, for example:

- a product serving end users;
- SLA/high-frequency programmatic calls;
- an external service that cannot be reached through Chat apps/MCP;
- automation that must run independently of ChatGPT surfaces.

## How the router works

The `capability-router` skill performs five steps:

```text
1. CLASSIFY
   What kind of task is this?

2. PREFLIGHT
   Which capabilities are actually available here?

3. SCORE
   Which surface can complete it safely with the lowest agentic cost?

4. ROUTE
   Chat / Scheduler / Local-MCP / Codex / Work / API

5. RE-EVALUATE
   As soon as the expensive capability is no longer needed,
   return the task to Chat.
```

A future executable implementation can emit something like:

```json
{
  "chat": 82,
  "scheduled_chat": 10,
  "local_tool": 35,
  "codex": 18,
  "work": 5,
  "api": 0,
  "decision": "CHAT",
  "reason": "GitHub read/write and CI are sufficient for this targeted change"
}
```

## Skills and hooks

The canonical skills live in this GitHub repository instead of depending only on native ChatGPT skills.

```text
skills/
  capability-router/
    SKILL.md
  surface-handoff/
    SKILL.md
```

This makes them:

- versioned;
- auditable;
- testable;
- reusable from Chat/Scheduled Chat when GitHub is accessible;
- easy to update without rewriting every scheduled prompt.

The intended evolution is to add hooks such as:

```text
pre       -> inspect capabilities / load state
validate  -> verify evidence and output contract
post      -> persist state / produce next action
on_error  -> record failure / prevent false success
```

## Handoff instead of copying entire conversations

When escalation is required, the router creates a compact structured handoff rather than copying tens of thousands of tokens of chat history.

```text
CHAT
  |
  | compact handoff.json
  v
CODEX / WORK / LOCAL TOOL
  |
  | specialist result + evidence
  v
CHAT
```

Typical handoff content:

- goal;
- work already completed;
- remaining work;
- repository/branch/files;
- constraints;
- evidence;
- tests;
- success criteria;
- why escalation is required;
- condition for returning to Chat.

See [`docs/HANDOFF_SPEC.md`](docs/HANDOFF_SPEC.md).

## Example: coding task

Request:

> Fix a bug in Loriq, update four files, add tests and open a PR.

Router reasoning:

```text
GitHub read/write available?       YES
Number of files small?             YES
Can GitHub Actions run the tests?  YES
Need local interactive tooling?    NO
Need long autonomous loop?         NO

=> ROUTE: CHAT
```

If CI then reveals a deep platform-specific issue requiring many iterative local builds:

```text
=> ESCALATE: CODEX
```

After Codex fixes/tests it:

```text
=> RETURN: CHAT
   review diff, explain change, update docs, communicate result
```

## Example: daily intelligence workflow

```text
Scheduled Chat
      |
      +--> Web / GitHub / apps
      |
      v
Python / shell
normalize + deduplicate + delta
      |
      v
ChatGPT reasoning
analysis + red team + synthesis
      |
      +--> GitHub state
      +--> Library snapshots
      +--> Gmail
      +--> WordPress/app
```

No Work/Codex is required unless a source/action becomes UI-only or another hard capability is missing.

## Example: Sparky / ComfyUI

Instead of using a browser/desktop agent to click through ComfyUI every time:

```text
Chat
 |
 v
media-mcp
 |
 +--> list_workflows
 +--> run_workflow
 +--> job_status
 +--> get_outputs
 |
 v
Sparky / ComfyUI
```

The expensive LLM orchestrates; the owned GPU performs the heavy media workload.

## Measuring whether it works

Do not rely only on intuition. Track:

- route selected;
- task class;
- whether escalation occurred;
- false/unnecessary escalations;
- handoff size;
- files touched;
- CI iterations;
- retries;
- completion quality;
- observable Work/Codex usage before/after.

Initial hypothesis:

| Scenario | Expected reduction of Work/Codex usage |
|---|---:|
| Conservative | ~50% |
| Target | ~65–70% |
| Strong-fit workloads | ~80%+ |

These figures are estimates to validate with telemetry, **not promises about OpenAI billing or quotas**.

## Repository map

```text
README.md                         this overview
SPEC.md                           product specification
docs/ARCHITECTURE.md              architecture details
docs/ROUTING_SPEC.md              routing policy
docs/USE_CASES.md                 use-case matrix
docs/TOKEN_ECONOMICS.md           savings assumptions/measurement
docs/HANDOFF_SPEC.md              surface handoff format
docs/MCP_PLAN.md                  planned gateways
docs/ROADMAP.md                   development plan
skills/capability-router/SKILL.md routing skill
skills/surface-handoff/SKILL.md   handoff skill
schemas/handoff.schema.json       machine-readable handoff contract
tests/routing_cases.md            canonical routing fixtures
```

## Development plan

1. Make the router executable and test its scoring.
2. Add runtime capability preflight.
3. Add GitHub/Scheduler hooks and run manifests.
4. Standardize the Chat → GitHub → CI coding lane.
5. Build `machines-mcp` and `media-mcp`.
6. Build safe VPS/API gateways.
7. Add optional Codex/Claude/local-LLM delegation.
8. Measure real savings and tune thresholds.

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Design principle

**Use the cheapest sufficient capability, not the most powerful available surface.**

The router should make escalation explicit, evidence-based, reversible and temporary.