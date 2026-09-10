# ChatGPT Cloud Cost Router — analysis, experiments, tests and global plan

**Date:** 2026-09-10  
**Repository:** `bacoco/chatgpt-cost-router`  
**Status:** empirical working record from the ChatGPT / Scheduler / MCP / Cowboy / GitHub experiments carried out on 10 September 2026.

## 1. Objective

The primary objective is economic and operational, not architectural elegance:

> **Maximize useful engineering work performed inside the already-paid ChatGPT cloud environment while minimizing marginal API/token cost, ideally to €0 of additional API spend.**

For coding and software maintenance, the routing principle is:

> **ChatGPT first → Developer MCP second → local verification when useful → Codex only when necessary → paid API only by explicit exception.**

The system should exploit, in priority order:

1. normal ChatGPT cloud reasoning and coding;
2. ChatGPT Scheduled Tasks;
3. Developer MCP connectors for external systems such as GitHub and WordPress;
4. Python / shell / git available to ChatGPT when useful;
5. Codex CLI authenticated with the ChatGPT account only for tasks that truly need a stronger iterative coding loop;
6. paid API tokens only as a last-resort, explicitly approved fallback.

The key metric is therefore not simply “tokens consumed”. The useful metric is:

> **How much useful engineering work can be completed inside ChatGPT/Codex allowances already paid for before any incremental API spend is required?**

Do not claim “zero tokens” technically. The intended target is **zero additional API billing** for the normal path.

## 2. Important insight: ChatGPT itself can code

The project must not assume that all code work belongs in Codex.

Normal ChatGPT can already:

- inspect code supplied through tools or files;
- reason about bugs;
- design fixes;
- write bounded patches;
- review diffs;
- create issues and PR descriptions;
- use Python and shell for verification when available.

Therefore Codex should be treated as an **escalation worker**, not the default engine.

A large fraction of software maintenance may be handled by:

```text
ChatGPT
   ↓
GitHub Developer MCP
   ↓
read / inspect / issue / branch / file update / PR / review
```

without consuming a separate Codex workflow.

## 3. Developer MCP proof with WordPress

The experiments established that a Developer MCP can turn ChatGPT into an orchestrator capable of taking real actions in an external system.

Working pattern:

```text
ChatGPT / Scheduled Task
        │
        ▼
Developer MCP
        │
        ▼
Cowboy MCP
        │
        ▼
WordPress
```

Two working Developer MCP applications were established:

- `Cowboy — ARGH` → `https://argh.pro`
- `Cowboy — Confisuite` → `https://confisuite.cloud`

For Confisuite the connection used Cowboy MCP 1.6.5 and OAuth discovery / Dynamic Client Registration.

Relevant endpoints:

```text
https://confisuite.cloud/wp-json/cowboy-mcp/v1/endpoint
https://confisuite.cloud/.well-known/oauth-protected-resource
https://confisuite.cloud/.well-known/oauth-authorization-server
https://confisuite.cloud/wp-json/cowboy-mcp/v1/oauth/register
https://confisuite.cloud/wp-json/cowboy-mcp/v1/oauth/token
https://confisuite.cloud/cowboy-mcp-oauth/authorize
```

Observed protected-resource metadata:

```json
{
  "resource": "https://confisuite.cloud/wp-json/cowboy-mcp/v1/endpoint",
  "authorization_servers": ["https://confisuite.cloud"],
  "bearer_methods_supported": ["header"],
  "scopes_supported": ["mcp"],
  "resource_documentation": "https://cowboymcp.com"
}
```

Observed authorization-server metadata exposed:

- `authorization_endpoint`;
- `token_endpoint`;
- `registration_endpoint`;
- authorization-code grant;
- refresh-token grant;
- PKCE `S256`;
- token endpoint auth method `none`;
- scope `mcp`.

### 3.1 Important troubleshooting lesson: cache can break OAuth discovery

Confisuite initially appeared to “not implement OAuth” even though Cowboy was correctly configured.

The root cause was stale LiteSpeed cache serving an old 404 for a `.well-known` OAuth endpoint to external callers while the administrator browser could see the correct response.

The fix was to purge LiteSpeed cache. After purge, external OAuth discovery became consistent and ChatGPT could create `Cowboy — Confisuite`.

This failure mode must be part of the future non-technical installation kit.

## 4. Important empirical observation about Scheduled Tasks

During the EnergySignal test:

- a developer-MCP execution could use `Cowboy — Confisuite`;
- invocation of the standard Gmail connector failed with:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

The same restriction was later observed when trying to use the built-in OpenAI GitHub connector from this conversation.

This is an **empirical observation from this account/context**, not a universal product rule.

It means the project must explicitly test whether a given connector is usable from:

- normal chat;
- developer-MCP-restricted chat;
- Scheduled Tasks.

The safest integration boundary for reliable scheduled automation may be Developer MCPs.

## 5. Current capability inventory

Confirmed in the ChatGPT environment during this experiment:

| Capability | State | Notes |
|---|---|---|
| ChatGPT reasoning / coding | ✅ | Can analyze and write code directly |
| Scheduled Tasks | ✅ | Recurring and one-shot tasks available |
| Python | ✅ | Available in ChatGPT environment |
| Shell / container | ✅ | Available, but treat as ephemeral |
| `git` | ✅ | Installed in the ChatGPT container |
| `gh` GitHub CLI | ❌ in current container | Not installed at time of test |
| Persistent working tree | Not guaranteed | Chat VM/container must be considered ephemeral |
| Persistent credentials | Not guaranteed | Do not rely on chat VM as credential store |
| Cowboy — ARGH | ✅ | Developer MCP; WordPress read/write |
| Cowboy — Confisuite | ✅ | Developer MCP; WordPress read/write |
| Built-in GitHub connector | ⚠️ | Connected, but direct invocation returned `FORBIDDEN` in this developer-MCP-restricted context |
| Standard Gmail connector | ⚠️ | Connected in account, but returned `FORBIDDEN` in this developer-MCP-restricted context |
| GitHub — bacoco TEST | ✅ | Developer MCP using GitHub official remote MCP; 44 tools discovered and successfully invoked |

The following must never be conflated:

```text
ChatGPT can generate code
        ≠
ChatGPT has GitHub write access
        ≠
ChatGPT has a persistent checkout
        ≠
ChatGPT can run Codex CLI
```

These are separate capabilities and should be routed independently.

## 6. GitHub Developer MCP experiment

### 6.1 Built-in GitHub connector

The OpenAI-provided GitHub connector was already connected by OAuth and displayed developer actions in the ChatGPT plugin settings.

However, when invoked in this developer-MCP-restricted conversation, a repository call failed with:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

Conclusion: the built-in connector is not sufficient for this specific execution context.

### 6.2 Custom Developer MCP pointing to GitHub’s official remote MCP

A custom ChatGPT Developer MCP was created with:

```text
Name: GitHub — bacoco TEST
Server URL: https://api.githubcopilot.com/mcp
Authentication: OAuth
```

Important UI lesson: in the current ChatGPT UI there was no separate “Scan Tools” button during creation. The app was created first, then its plugin detail page showed an **Actualiser** button. Initially the page said no actions were available. After clicking **Actualiser**, the GitHub tool schemas appeared.

This means the installation kit must describe the UI that actually exists, not assume older documentation wording.

### 6.3 Successful tool discovery

After refresh, ChatGPT discovered **44 GitHub tools** from the Developer MCP.

Representative available tools include:

```text
get_me
get_file_contents
search_code
list_branches
list_commits
create_branch
create_or_update_file
push_files
issue_read
issue_write
list_issues
pull_request_read
list_pull_requests
create_pull_request
update_pull_request
pull_request_review_write
merge_pull_request
request_copilot_review
run_secret_scanning
```

This proves that the hosted GitHub MCP can provide both read and write operations to ChatGPT without building a custom GitHub server.

### 6.4 T01 — authenticated identity and repository read: PASS

`get_me` returned authenticated GitHub user `bacoco`.

Repository `bacoco/chatgpt-cost-router` was read successfully through the Developer MCP.

The repository root contained, among other entries:

```text
.agents/
.github/
README.md
SPEC.md
audits/
cost_router/
docs/
examples/
policy/
requirements-dev.txt
requirements.txt
schemas/
scripts/
skills/
tests/
```

Default branch observed:

```text
main
```

HEAD SHA at the time of the test:

```text
6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

### 6.5 T02 — issues and PR read: PASS

At test time:

- repository issues: 0 before the test issue;
- repository pull requests: 0.

README and SPEC were retrieved successfully.

The repository itself already implements a deterministic recommendation engine with structured routing policy, schemas, skills, a durable local operation ledger and tests. It currently evaluates caller-supplied plans; live discovery and remote execution remain integration work.

### 6.6 T03 — issue create/read/close round-trip: PASS

A temporary issue was created:

```text
[MCP TEST] Validate ChatGPT Developer MCP issue round-trip
```

Issue number:

```text
#1
```

It was read back successfully through the MCP and then closed with state reason `completed`.

This proves authenticated low-risk GitHub write capability from normal ChatGPT through the Developer MCP.

### 6.7 T04 — branch creation: PASS (in progress for full PR round-trip)

A branch was successfully created from `main`:

```text
docs/chatgpt-cloud-cost-router-analysis-2026-09-10
```

Base SHA:

```text
6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

The next T04 steps are:

1. add this analysis document to the branch;
2. inspect the resulting commit/diff;
3. create a PR against `main`;
4. read the PR back;
5. do not merge automatically until explicitly authorized.

## 7. Existing repository context discovered

The repository already has a clear deterministic cost/capability-routing core.

README states that code does not automatically require Codex and complexity alone does not automatically require Work. The current engine evaluates caller-supplied plans and does not yet discover host tools or implement remote MCP gateways.

The current economic target documented in the repo is explicitly treated as an **unvalidated hypothesis**, not a claim. That is consistent with this new empirical test plan.

This 10 September document should therefore be treated as an **integration experiment / empirical architecture record**, not as a replacement for the normative `SPEC.md` or routing policy.

## 8. Target architecture

```text
                         CHATGPT CLOUD
                              │
                ┌─────────────┴─────────────┐
                │                           │
             CHAT                       SCHEDULER
                │                           │
                └─────────────┬─────────────┘
                              │
                       COST ROUTER LOGIC
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        GitHub MCP       Cowboy MCP       Other MCPs
             │                │
             ▼                ▼
          GitHub           WordPress
             │
             │ escalation only
             ▼
      Codex Worker MCP
             │
             ▼
      Persistent VM
      ├─ Codex CLI
      ├─ git
      ├─ GitHub CLI
      ├─ Python
      ├─ test runtimes
      └─ persistent workspaces
```

Central design goal:

> **Do not send a task to Codex if normal ChatGPT plus MCP can complete it safely and verifiably.**

## 9. Routing levels

### Level 0 — ChatGPT only

Use normal ChatGPT for:

- code explanation;
- design;
- architecture review;
- bug hypotheses;
- issue drafting;
- PR review text;
- test-plan generation;
- static reasoning over code supplied in context.

Desired marginal API cost: **€0**.

### Level 1 — ChatGPT + GitHub Developer MCP

This should become the default engineering path where external GitHub state/action is needed.

Expected tasks:

- inspect repository;
- search code;
- read files;
- read issues;
- read pull requests;
- compare diffs;
- find likely bugs;
- create/update issues;
- create branches;
- make bounded file changes;
- commit changes;
- create pull requests;
- review pull requests;
- optionally merge only when explicitly permitted and gates pass.

Typical flow:

```text
ChatGPT
   ↓
read issue
   ↓
inspect relevant files
   ↓
reason about fix
   ↓
modify bounded files
   ↓
review diff
   ↓
branch / commit
   ↓
PR
```

For many maintenance tasks Codex is not necessary.

### Level 2 — ChatGPT + GitHub MCP + Python/shell

Use when the change is understandable by ChatGPT but needs executable verification.

Examples:

- JSON/YAML validation;
- unit tests;
- lint;
- deterministic scripts;
- reproducing a small bug;
- checking generated output.

Potential flow:

```text
GitHub MCP → retrieve code
      ↓
ChatGPT local workspace
      ↓
edit
      ↓
Python / shell / tests
      ↓
verified diff
      ↓
GitHub MCP → branch + commit + PR
```

Important limitation: the ChatGPT execution environment must be treated as ephemeral unless persistence is explicitly demonstrated.

### Level 3 — Codex Worker on persistent VM

Escalate only when the task requires:

- long iterative edit/test loops;
- large refactoring;
- many files;
- dependency installation;
- complex build environments;
- long-running tests;
- persistent checkout;
- repeated recovery after failures;
- more autonomous software-engineering behavior.

Architecture:

```text
ChatGPT / Scheduler
        │
        │ Developer MCP
        ▼
Codex Worker MCP
        │
        ▼
Persistent VM
├── Codex CLI
├── ChatGPT-account authentication
├── git
├── gh
├── repo workspaces
└── test/build toolchain
```

The VM retains repository state, branch state, test artifacts, Codex authentication, GitHub authentication and run logs.

ChatGPT should receive **capabilities, not raw credentials**.

### Level 4 — paid API fallback

Paid OpenAI API usage should be:

- disabled by default;
- impossible to trigger silently;
- activated only by an explicit owner decision;
- separately metered.

Canonical rule:

> **No `OPENAI_API_KEY` fallback unless explicitly authorized for the specific task.**

## 10. Proposed router policy

```text
INPUT: engineering task

1. Can ChatGPT solve it without external mutation?
   YES → ChatGPT only.

2. Does it mainly require GitHub metadata/actions?
   YES → GitHub Developer MCP.

3. Is the code change bounded and understandable in context?
   YES → ChatGPT + GitHub MCP.
         Use Python/shell for verification if useful.

4. Does it require repeated edit/test/fix cycles,
   large repository exploration, persistent state,
   long execution or complex builds?
   YES → escalate to Codex Worker MCP.

5. Does the selected path require paid API access?
   STOP.
   Require explicit owner authorization.
```

## 11. Candidate tasks that should stay out of Codex when possible

Especially suitable for normal ChatGPT + GitHub MCP:

- repository inventory;
- static bug detection;
- dead-code identification;
- documentation inconsistencies;
- README corrections;
- missing-test identification;
- security-review findings;
- dependency-risk review;
- architecture drift detection;
- issue creation/deduplication;
- PR review;
- regression-risk analysis;
- changelog generation;
- release-readiness checklists;
- broken-link checks;
- schema consistency;
- configuration review;
- small patches;
- bounded test additions;
- implementation-task creation for another worker.

Even if full autonomous coding proves unreliable, this set already provides substantial engineering value at near-zero marginal API spend.

## 12. GitHub Developer MCP minimum useful surface

The hosted GitHub MCP already exposes a broad surface. For the cost router the preferred long-term configuration should use the smallest useful set.

Required read capabilities:

```text
get_file_contents
search_code
list_branches
list_commits
issue_read
list_issues
pull_request_read
list_pull_requests
```

Required write capabilities:

```text
issue_write
create_branch
create_or_update_file
push_files
create_pull_request
update_pull_request
pull_request_review_write
```

Separate/high-risk capabilities:

```text
merge_pull_request
```

Merge should remain distinct from normal patch/PR permissions.

## 13. Test plan

Execute in increasing order of consequence.

### T01 — GitHub MCP connection

**Goal:** prove Developer MCP visibility and authenticated repository read.

Status: **PASS on 2026-09-10**.

Checks completed:

- authenticated identity = `bacoco`;
- `bacoco/chatgpt-cost-router` root readable;
- default branch = `main`;
- HEAD SHA observed = `6273cb87b98e94a1e04d9d439dfa400bbbb321cc`.

### T02 — repository files/issues/PR read

**Goal:** prove normal project inspection.

Status: **PASS on 2026-09-10**.

README, SPEC, branch list, issues and PRs were retrieved through MCP.

### T03 — issue creation round-trip

**Goal:** prove low-risk write access.

Status: **PASS on 2026-09-10**.

Temporary issue #1 was created, read back and closed.

### T04 — branch + bounded file modification + PR

**Goal:** prove that normal ChatGPT can perform a complete bounded software/documentation change without Codex.

Status at time this document was written: **branch creation PASS; remaining file commit + PR steps being executed.**

Procedure:

1. create branch from exact `main` SHA;
2. add this document;
3. create commit;
4. create PR;
5. read PR and diff back;
6. do not auto-merge.

### T05 — PR review workflow

1. read a real PR;
2. inspect changed files and surrounding code;
3. identify regression/security/test concerns;
4. post a review comment or formal review.

**PASS:** review references actual changed code and evidence.

### T06 — bug detection → issue

Scheduler or chat:

```text
inspect repo
→ find one evidence-backed bug
→ verify not already tracked
→ create issue
```

No code change required.

This is a priority use case even if autonomous coding is later judged unreliable.

### T07 — Scheduler → GitHub Developer MCP

Critical test.

First scheduled invocation should be read-only:

1. read repository HEAD;
2. inspect a known file;
3. report exact SHA;
4. perform no mutation.

Second controlled scheduled test may create a clearly marked temporary issue and then a later run should deduplicate it.

**PASS:** scheduler can invoke the same Developer MCP as interactive chat.

### T08 — idempotency / duplicate prevention

Run the same scheduled task twice.

Expected:

```text
run 1 → creates issue/PR
run 2 → detects equivalent existing artifact → no duplicate
```

### T09 — ChatGPT + Python/shell verification

1. retrieve a small project or selected files;
2. apply a bounded change;
3. run tests/lint locally;
4. inspect failure if any;
5. fix once;
6. rerun;
7. create PR through GitHub MCP.

**PASS:** verified PR without Codex.

### T10 — Codex CLI persistent-VM proof of concept

Only after T01–T09.

VM requirements:

```text
Ubuntu
git
GitHub CLI
Python
runtime dependencies as needed
Codex CLI
persistent workspace
secure credential storage
```

Authentication:

- Codex with ChatGPT account;
- GitHub with scoped credentials;
- **no paid OpenAI API key**.

Test:

1. clone one test repository;
2. give Codex a small bug;
3. run tests;
4. produce diff;
5. stop before push.

### T11 — Codex Worker MCP

Expose only high-level actions initially:

```text
codex_run(repo, task)
codex_status(run_id)
codex_logs(run_id)
codex_diff(run_id)
codex_cancel(run_id)
```

Do not expose arbitrary root shell.

Add later only if proven:

```text
codex_push(run_id)
codex_create_pr(run_id)
```

### T12 — Scheduler → Codex Worker

Desired durable pattern:

```text
scheduler
   ↓
codex_run
   ↓
returns run_id
   ↓
later scheduler invocation
   ↓
codex_status
   ↓
READY_FOR_PR
   ↓
PR creation
```

This avoids forcing a long coding session into one scheduled invocation.

### T13 — cost/quota experiment

Record for every representative task:

```text
task_id
route
ChatGPT_only
GitHub_MCP_used
Python_shell_used
Codex_used
paid_API_used
elapsed_time
human_interventions
success_failure
issue_or_PR
```

Desired field:

```text
incremental_api_cost_eur = 0
```

Empirically verify quota behavior instead of assuming how ChatGPT and Codex usage pools interact.

### T14 — Gmail Developer MCP

Because standard Gmail failed in the developer-MCP-restricted execution context, test a Developer MCP form if needed.

Minimum operations:

```text
sent_search
message_read
draft_create
email_send
```

Required safety:

- exact destination allowlist;
- same-date / same-subject deduplication;
- no silent fallback;
- receipts.

## 14. Global implementation plan

### Phase A — GitHub without Codex

Priority: **highest**.

1. establish GitHub Developer MCP;
2. pass T01–T04;
3. run T05 PR review;
4. run T06 bug → issue;
5. run T07 scheduler access;
6. establish T08 idempotency.

Success criterion:

> ChatGPT can inspect repositories, create useful issues, review PRs and perform bounded changes/PRs without Codex.

### Phase B — direct ChatGPT coding

Test representative tasks:

- documentation fix;
- test fix;
- small Python bug;
- small TypeScript bug;
- configuration change;
- bounded multi-file refactor.

Measure where normal ChatGPT becomes unreliable or inefficient.

Build thresholds from evidence, not intuition.

### Phase C — router integration

Useful route classes:

```text
REVIEW_ONLY
ISSUE_ONLY
BOUNDED_PATCH
VERIFIED_PATCH
CODEX_ESCALATION
MANUAL_REVIEW
```

Each routing decision should leave a receipt describing:

- why the route was selected;
- tools used;
- whether Codex was consumed;
- whether paid API was consumed.

### Phase D — Codex Worker

Build only if Phase B demonstrates a real need.

Keep the interface minimal:

```text
run
status
logs
diff
cancel
create_pr
```

Prefer a persistent VM over installing/authenticating Codex in every ephemeral ChatGPT execution.

### Phase E — scheduled maintenance

Examples:

#### Loriq

```text
weekly scheduler
→ inspect remaining findings / PRs
→ review regressions
→ directly fix bounded findings
→ issue/PR
→ escalate complex work only to Codex
```

#### Tech Watch

```text
weekly research
→ identify actionable technical change
→ issue
→ optionally bounded PR
```

#### ARGH

```text
scheduler
→ inspect harness-intelligence
→ validate control logic
→ issue/PR for defects
→ Cowboy only for WordPress publication when required
```

#### EnergySignal

```text
scheduler
→ research
→ GitHub instructions/state
→ Cowboy Confisuite publication
→ Gmail Developer MCP delivery if standard connector remains unavailable
```

## 15. Security model

Credentials stay only in the system that needs them:

```text
GitHub auth → GitHub MCP / worker VM
Codex login  → worker VM secure store
WordPress    → Cowboy OAuth
Gmail        → Gmail OAuth/MCP
```

ChatGPT receives capabilities, not secrets.

Use explicit repository allowlists where possible.

Separate permission classes:

```text
READ
ISSUE_WRITE
BRANCH_WRITE
PR_WRITE
MERGE
RELEASE
```

`MERGE` and `RELEASE` must not be implicitly granted merely because file editing is allowed.

If a worker MCP later exposes shell, run it unprivileged, sandboxed per repo, with filesystem allowlist, audit log, timeout and network policy.

## 16. Reliability requirements

Every automated action should be verifiable.

For repository tasks record:

```text
repository
base_branch
base_SHA
task_id
files_read
files_changed
tests_run
test_results
commit_SHA
PR_number
issue_number
route_selected
Codex_used
paid_API_used
```

Never declare:

```text
fixed
tested
published
sent
merged
```

without corresponding evidence.

## 17. Scheduler design rule

A Scheduled Task should be an **orchestrator**, not necessarily the place where every long-running operation happens.

Preferred pattern:

```text
Scheduled Task
    ↓
inspect state
    ↓
perform bounded operation
OR
start durable worker
    ↓
persist run_id
    ↓
later invocation checks status
```

This is particularly important for long Codex jobs.

## 18. Core economic rule

Canonical rule:

> **Use the cheapest already-paid capability capable of safely completing and verifying the task. Escalate only when the lower-cost route is insufficient. Never silently cross into paid API usage.**

Suggested route order:

```text
1. ChatGPT
2. ChatGPT + Developer MCP
3. ChatGPT + Developer MCP + Python/shell
4. Codex via ChatGPT-account allowance
5. explicit human/manual route
6. paid API only with explicit approval
```

## 19. What not to build prematurely

Do not initially build:

- a custom IDE;
- a giant autonomous agent framework;
- a general remote-root-shell MCP;
- a custom GitHub implementation while GitHub’s hosted MCP already works;
- a complex task queue;
- a full CI replacement;
- API-token fallback logic.

First prove the cheapest route.

## 20. Installation-kit requirement

This project will later produce a **zero-assumption installation kit for a person who knows absolutely nothing about the stack**.

The kit must document every UI step, endpoint, expected result, validation test, failure mode and recovery path.

It must not assume knowledge of:

- WordPress;
- MCP;
- OAuth;
- GitHub;
- ChatGPT plugins;
- Developer Mode;
- schedulers;
- shell;
- git;
- Codex.

Important installation lessons already learned:

1. **Connected to account ≠ callable in the current chat.** A connector may exist globally yet be unavailable in a developer-MCP-restricted execution.
2. **Developer MCP tool discovery may require refresh.** In the current UI, the GitHub custom app initially showed no actions until **Actualiser** was clicked after creation.
3. **OAuth metadata can be correct but hidden by cache.** LiteSpeed served stale 404s for Cowboy OAuth discovery until cache purge.
4. **Do not debug repository permissions when zero tools are discovered.** Zero tools is a connection/tool-discovery problem before repository access.
5. **Do not paste PATs/secrets into chat or repositories.** Prefer OAuth and capability-scoped MCPs.

## 21. Immediate next actions

### P0

- [x] Connect GitHub Developer MCP to ChatGPT.
- [x] Verify it is visible and exposes tools.
- [x] T01: authenticated identity + repository read.
- [x] T02: files/issues/PR read.
- [x] T03: create/read/close temporary issue.
- [x] T04a: create bounded branch from main.
- [ ] T04b: commit this document to the branch.
- [ ] T04c: create PR and read diff back.
- [ ] T05: PR review workflow.
- [ ] T07: Scheduled Task → GitHub Developer MCP.
- [ ] T08: scheduler idempotency.

### P1

- [ ] Test bounded direct coding with Python/shell verification.
- [ ] Measure where normal ChatGPT becomes inefficient or unreliable.
- [ ] Define empirical escalation thresholds.

### P2

- [ ] Only then build the Codex Worker MCP if necessary.
- [ ] Test asynchronous scheduler → Codex execution.
- [ ] Add Gmail Developer MCP if standard Gmail remains unusable in scheduled developer-MCP contexts.

## 22. Success criteria

Stage 1:

```text
[x] ChatGPT reads bacoco repository via Developer MCP
[x] ChatGPT creates and closes a test issue
[x] ChatGPT creates a branch
[ ] ChatGPT changes/adds a bounded file
[ ] ChatGPT creates a PR
[ ] ChatGPT reviews a PR
[ ] Scheduler can invoke the same GitHub MCP
[ ] Repeated scheduler execution does not duplicate issue/PR
[x] No paid OpenAI API key was used
```

Stage 2:

```text
[ ] ChatGPT executes tests locally for a bounded change
[ ] ChatGPT fixes at least one small bug without Codex
[ ] Router correctly escalates one complex task to Codex
[ ] Codex worker authenticates through ChatGPT account, not API key
[ ] Scheduler can launch and later inspect a durable Codex run
[ ] All actions leave verifiable receipts
```

## 23. Working hypothesis

> **A substantial portion of software maintenance and even bounded coding can be performed by normal ChatGPT cloud plus Developer MCPs and local verification, without invoking Codex and without paid API tokens. Codex should be treated as an escalation worker rather than the default execution engine.**

Even if direct automated coding proves less reliable than expected, the architecture remains valuable for:

- repository inspection;
- bug discovery;
- issue generation;
- PR review;
- regression analysis;
- task decomposition;
- documentation maintenance;
- test-gap identification;
- controlled pull-request creation.

## 24. Final architecture statement

```text
                    CHATGPT COST ROUTER
                           │
              “cheapest safe verified path”
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ChatGPT            GitHub MCP         Cowboy MCP
        │                  │                  │
        │                  ▼                  ▼
        │               GitHub            WordPress
        │
        │ only when useful
        ▼
  Python / shell
        │
        │ only when still insufficient
        ▼
   Codex Worker
        │
        ▼
 Persistent VM
        │
        │ explicit exception only
        ▼
    Paid API
```

Desired default outcome:

```text
incremental_api_cost = €0
Codex_usage = minimal
ChatGPT_cloud_usage = maximal
verification = mandatory
```
