# Zero-assumption setup guide — ChatGPT → GitHub Developer MCP

**Audience:** someone who has never used MCP, OAuth, GitHub integrations, Codex, a terminal, or a scheduler.  
**Goal:** connect ChatGPT to the user's own GitHub repositories, prove read and write access safely, and then prove that a ChatGPT Scheduled Task can use the same GitHub Developer MCP.  
**Reference validation date:** 10 September 2026.

> The goal of this project is to use the already-paid ChatGPT cloud environment for as much engineering work as possible, while minimizing Codex use and avoiding paid OpenAI API calls unless explicitly approved.

## 1. What this setup gives you

After this guide succeeds, normal ChatGPT can work directly with GitHub:

```text
ChatGPT
   │
   ▼
GitHub Developer MCP
   │
   ▼
your GitHub account
   │
   ├── read repositories and files
   ├── search code
   ├── read/create issues
   ├── create branches
   ├── create/update files
   ├── create pull requests
   └── review pull requests
```

This is **not Codex CLI** and does **not require an OpenAI API key**.

The intended cost-routing order is:

```text
ChatGPT first
→ GitHub Developer MCP
→ Python/shell verification when useful
→ Codex only if truly necessary
→ paid API only by explicit exception
```

## 2. What you need

You need:

- a ChatGPT account that shows **Settings → Plugins** and allows a custom MCP/plugin to be added;
- a GitHub account;
- at least one repository you may read;
- for write tests, a repository you may modify.

For a first installation, use a safe repository where a temporary issue and test branch are acceptable.

You do **not** need Codex CLI, GitHub CLI, a local clone, Docker, Python, an OpenAI API key, or a GitHub PAT for the OAuth path documented here.

## 3. Built-in GitHub vs custom Developer MCP

You may already see a built-in plugin named simply `GitHub`. That is different from the custom Developer MCP created here.

Use a clear name such as:

```text
GitHub — <your-github-username> TEST
```

In the 10 September 2026 experiment, the built-in OpenAI GitHub connector was OAuth-connected and showed actions in Settings, yet a real invocation in the tested developer-MCP-restricted context failed with:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

Do **not** conclude that the built-in GitHub connector never works. The proven lesson is narrower:

> Connected to the account does not guarantee callable from a particular chat or Scheduled Task.

## 4. Create the GitHub Developer MCP

In ChatGPT:

1. open **Settings / Réglages**;
2. open **Plugins**;
3. click the **+** button;
4. name the app `GitHub — <username> TEST`;
5. set the server URL to:

```text
https://api.githubcopilot.com/mcp
```

6. choose **OAuth**;
7. leave advanced OAuth client fields alone;
8. read and accept the custom-MCP warning;
9. click **Créer**;
10. complete GitHub OAuth using the GitHub account that owns/has access to your repositories.

The known-good reference setup used the URL **without a trailing slash**.

An earlier app had used `https://api.githubcopilot.com/mcp/` and ended up with zero callable tools. Other variables changed too, so **the experiment did not prove the slash was the cause**. Use the empirically verified no-slash form unless later tests prove equivalence.

## 5. Critical step: make the actions appear

After creation, open:

```text
Settings → Plugins → GitHub — <username> TEST
```

If you see:

```text
Actions
Aucune action de l'application n'est disponible pour le moment.
```

the setup is **not ready**.

Click:

```text
Actualiser
```

In the successful reference setup, 44 GitHub tools then appeared, including:

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

### UI drift lesson

Some documentation may mention **Scan Tools / Analyser les outils** during creation.

In the actual 10 September UI, there was **no such button** in the creation dialog.

The working sequence was:

```text
Créer
→ OAuth
→ open plugin details
→ Actualiser
→ actions appear
```

Follow the interface you actually see and validate observable tool availability.

## 6. Select the custom MCP in a chat

Use the custom Developer MCP, not the built-in GitHub entry.

Depending on the UI, select it from the plugin picker or explicitly mention it:

```text
@GitHub — <username> TEST
```

If it is visible in Settings but not in the picker, verify first that its detail page actually shows actions.

## 7. T01 — read-only identity + repository test

Paste:

```text
Use GitHub — <username> TEST only.
Do not modify anything.

1. Tell me the authenticated GitHub login.
2. Read repository <owner>/<repo>.
3. List the repository root.
4. Identify the default branch.
5. Return the exact current SHA of that branch.

Return PASS only if each item is actually retrieved through the Developer MCP.
```

PASS requires the exact login, actual repository entries, branch, and commit SHA.

Reference result:

```text
login: bacoco
repo: bacoco/chatgpt-cost-router
default branch: main
main SHA: 6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

“Plugin connected” is not a PASS.

## 8. T02 — files, issues and PRs

Paste:

```text
Use GitHub — <username> TEST only.
Do not modify anything.

Repository: <owner>/<repo>

1. Read README.md.
2. Read one source/specification file.
3. List issues.
4. List pull requests.
5. List branches.

Return PASS/FAIL for each operation.
```

This proves ChatGPT can already act as a repository auditor/reviewer without Codex.

## 9. T03 — first controlled write: temporary issue

Paste:

```text
Use GitHub — <username> TEST only.

Repository: <owner>/<repo>

Create one temporary issue titled:
[MCP TEST] Validate ChatGPT Developer MCP issue round-trip

State clearly that it is temporary.

Then:
1. read the issue back;
2. verify title/body;
3. close it as completed.

Do not modify code, branches, workflows or pull requests.
```

PASS is:

```text
create
→ read back
→ verify
→ close
```

Reference result: `bacoco/chatgpt-cost-router#1` was created, verified and closed.

## 10. T04 — branch + harmless file + PR

Only after T01–T03 pass.

Never make the first file-write test directly on `main`.

Paste:

```text
Use GitHub — <username> TEST only.

Repository: <owner>/<repo>

1. Read exact current main SHA.
2. Create a test branch from main.
3. Add one harmless documentation file only.
4. Commit it to the branch.
5. Create a pull request to main.
6. Read the PR back.
7. Read the PR diff back.
8. Verify only the intended file changed.
9. Do NOT merge.
```

Reference result:

```text
branch:
docs/chatgpt-cloud-cost-router-analysis-2026-09-10

base SHA:
6273cb87b98e94a1e04d9d439dfa400bbbb321cc

commit:
ab5f66a556eab82bb7d80fcff71341f2dbbe7d13

PR:
#2
```

## 11. Do not equate PR creation with merge readiness

After a PR exists:

1. read its diff;
2. inspect CI/check runs;
3. inspect reviews/comments;
4. distinguish failures introduced by the PR from pre-existing failures;
5. merge only when policy explicitly permits it.

In the reference experiment, PR #2 existed but CI showed failure/cancellation. It was **not auto-merged**.

Keep these states separate:

```text
PR_CREATED
DIFF_VERIFIED
CI_PASS
MERGE_READY
MERGED
```

## 12. T07 — Scheduled Task read-only proof

Interactive success does not prove scheduled success.

Create a one-shot Scheduled Task with:

```text
Use the Developer MCP app `GitHub — <username> TEST` only.

Perform a read-only validation against repository `<owner>/<repo>`:
1. get the authenticated GitHub identity;
2. read the repository root;
3. list branches;
4. report the exact current SHA of `main`.

Do not create or modify issues, files, branches, pull requests, workflows, or any repository state.

Return PASS only if all reads succeed through the Developer MCP and include the authenticated login plus exact main SHA; otherwise return FAIL with the precise blocker.
```

### Reference T07 — PASS

The 10 September scheduler returned:

```text
Authenticated GitHub login: bacoco
Repository root read: PASS
Branches listed: PASS
main SHA: 6273cb87b98e94a1e04d9d439dfa400bbbb321cc
other branch:
docs/chatgpt-cloud-cost-router-analysis-2026-09-10
at ab5f66a556eab82bb7d80fcff71341f2dbbe7d13
No repository state was modified.
```

This proves a Scheduled Task can use the custom GitHub Developer MCP for authenticated GitHub reads without Codex or a paid OpenAI API key.

## 13. T08 — idempotency before recurring writes

Do not enable recurring GitHub writes until this is proven.

For a first scheduled write, use a temporary issue with logic:

```text
search for equivalent test issue
if equivalent exists:
    create nothing
else:
    create exactly one
```

Run the same task twice.

PASS:

```text
run 1 → one intended artifact
run 2 → zero duplicate artifacts
```

## 14. Test direct ChatGPT coding before Codex

Start with bounded tasks:

- documentation fix;
- test fixture fix;
- small Python bug;
- small TypeScript bug;
- configuration correction;
- bounded multi-file change.

Desired route:

```text
ChatGPT
→ read issue/code via GitHub MCP
→ reason
→ patch
→ inspect diff
→ optionally test with Python/shell
→ PR
```

Escalate to Codex only for long iterative loops, persistent checkout, complex builds, large refactors, or long-running tests.

## 15. Security rules

Never paste into ChatGPT messages or repositories:

- GitHub PATs;
- OpenAI API keys;
- passwords;
- SSH private keys;
- OAuth refresh tokens.

Prefer OAuth.

Increase capability gradually:

```text
READ
→ ISSUE_WRITE
→ BRANCH_WRITE
→ PR_WRITE
→ REVIEW
→ MERGE later
```

A visible `merge_pull_request` tool is not authorization to merge automatically.

## 16. Troubleshooting

### Built-in GitHub says FORBIDDEN

Observed:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

Use the custom Developer MCP in that context.

### Custom MCP shows zero actions

Open its detail page and click **Actualiser**.

### No “Scan Tools” button exists

That matched the real reference UI. Use:

```text
Créer → OAuth → plugin details → Actualiser
```

### Plugin is in Settings but not visible in the chat picker

Verify actions exist, then explicitly mention:

```text
@GitHub — <username> TEST
```

### OAuth succeeds but repo read fails

First verify `get_me` returns the expected GitHub account. Then verify that account has repository access. Do not paste a PAT into chat as a shortcut.

## 17. Completion checklist

```text
[ ] custom GitHub Developer MCP exists
[ ] OAuth identity is correct
[ ] real actions appear after refresh
[ ] get_me succeeds
[ ] repository root read succeeds
[ ] exact main SHA returned
[ ] README/source read succeeds
[ ] issues and PRs list succeeds
[ ] temporary issue create/read/close succeeds
[ ] test branch creation succeeds
[ ] harmless file commit succeeds
[ ] PR creation and diff read-back succeeds
[ ] no automatic merge occurred
[ ] read-only Scheduled Task test succeeds
[ ] duplicate-prevention test succeeds before recurring writes
[ ] no paid OpenAI API key was used
```

## 18. Reference state on 10 September 2026

```text
T01 identity + repo read                         PASS
T02 files/issues/PR/branch reads                PASS
T03 temporary issue create/read/close           PASS
T04 branch + bounded documentation + PR         PASS
T07 Scheduled Task → GitHub Developer MCP       PASS
T08 scheduled write idempotency                 NOT YET TESTED
T09 direct ChatGPT code + local tests           NOT YET TESTED
Codex Worker                                    NOT YET NEEDED/TESTED
Gmail Developer MCP                            NOT YET TESTED
```

No Codex and no paid OpenAI API key were needed for T01–T07.
