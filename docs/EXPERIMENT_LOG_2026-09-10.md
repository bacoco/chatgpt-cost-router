# Experiment and failure log — 10 September 2026

**Project:** ChatGPT Cost Router  
**Purpose:** preserve failures, wrong assumptions, ambiguous results and recoveries as first-class evidence.  
**Rule:** never rewrite history to make the path look cleaner than it was.

## 1. State model

The project distinguishes:

```text
VISIBLE
CONNECTED
TOOLS_DISCOVERED
CALLABLE
READ_VERIFIED
WRITE_VERIFIED
SCHEDULER_VERIFIED
IDEMPOTENCY_VERIFIED
```

These are not equivalent.

## 2. Chronological result table

| ID | Experiment | Result | Lesson |
|---|---|---|---|
| E01 | Existing `Cowboy — ARGH` | PASS | Developer MCP can expose authenticated external actions |
| E02 | Confisuite MCP endpoint opened unauthenticated | EXPECTED 401 | Clean 401 proves route/auth layer reachability |
| E03 | Confisuite custom MCP creation before external OAuth consistency | FAIL | ChatGPT said “does not implement OAuth” |
| E04 | `.well-known` metadata visible in admin browser | PASS locally | Admin browser view alone was insufficient |
| E05 | External `.well-known` check | FAIL/STALE 404 | LiteSpeed served old cached 404 |
| E06 | LiteSpeed purge | PASS | Cache can break OAuth discovery |
| E07 | `Cowboy — Confisuite` after purge | PASS | OAuth/DCR path worked |
| E08 | Standard Gmail in restricted execution | FAIL | Developer-MCP restriction blocked built-in Gmail |
| E09 | Built-in OpenAI GitHub connector | FAIL in this context | Same restriction despite OAuth/actions visible |
| E10 | First custom `GitHub — bacoco` | FAIL tool discovery | Namespace existed but zero tools |
| E11 | Look for “Scan Tools” button | WRONG UI ASSUMPTION | Current UI had no such creation button |
| E12 | Create `GitHub — bacoco TEST` at `/mcp` | CONNECTED, initially zero actions | OAuth success did not equal tool discovery |
| E13 | Click `Actualiser` on plugin detail page | PASS | 44 GitHub tools appeared |
| E14 | `get_me` | PASS | Authenticated as `bacoco` |
| E15 | Read `bacoco/chatgpt-cost-router` | PASS | Root/branches/files/SHA retrieved |
| E16 | Temporary issue create/read/close | PASS | Low-risk write verified |
| E17 | Branch + doc commit + PR | PASS | Bounded GitHub write without Codex |
| E18 | PR #2 CI | FAIL/CANCELLED | PR creation is not merge readiness |
| E19 | Scheduled Task → GitHub Developer MCP read-only | PASS | Scheduler can invoke custom GitHub MCP |
| E20 | Scheduled write idempotency | NOT TESTED | Required before recurring writes |
| E21 | Direct code patch + Python/shell tests | NOT TESTED | Needed to measure no-Codex coding ceiling |
| E22 | Codex Worker | NOT TESTED | Escalation only |
| E23 | Gmail Developer MCP | NOT TESTED | Candidate path for scheduled mail |

## 3. Cowboy/Confisuite OAuth failure and recovery

Direct access to:

```text
https://confisuite.cloud/wp-json/cowboy-mcp/v1/endpoint
```

returned a clean unauthenticated 401:

```json
{
  "code": "mcp_unauthorized",
  "message": "Missing or invalid Authorization header.",
  "data": {"status": 401}
}
```

That was expected and proved route/auth-layer reachability.

ChatGPT nevertheless reported:

```text
MCP server ... does not implement OAuth
```

Cowboy MCP 1.6.5 showed both MCP Server and Desktop Connector/OAuth enabled.

The user could retrieve valid metadata from:

```text
https://confisuite.cloud/.well-known/oauth-protected-resource
https://confisuite.cloud/.well-known/oauth-authorization-server
```

but an external diagnostic still received an old WordPress 404 with LiteSpeed cache evidence.

**Fix:** purge LiteSpeed cache.

**Outcome:** OAuth discovery became externally consistent and `Cowboy — Confisuite` worked.

**Lesson:** if the admin browser sees correct OAuth metadata while ChatGPT does not, test CDN/cache behavior before changing OAuth configuration repeatedly.

## 4. Standard Gmail connector failure

During EnergySignal completion, standard Gmail returned:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

This does **not** prove Gmail is universally unavailable in Scheduled Tasks.

It proves only that the standard connector was forbidden in the tested execution context.

A Gmail Developer MCP remains a candidate and is not yet tested.

## 5. Built-in GitHub connector failure

The built-in OpenAI GitHub plugin was:

```text
installed
OAuth-connected
showing actions in Settings
```

A real invocation still returned:

```text
FORBIDDEN: This conversation is restricted to developer MCPs
```

Lesson:

```text
connected in account
≠ callable in current chat
≠ callable in Scheduled Task
```

## 6. First custom GitHub app: visible, zero tools

The first custom app `GitHub — bacoco` existed, but no GitHub functions were callable.

It had been configured with:

```text
https://api.githubcopilot.com/mcp/
```

State:

```text
app visible            YES
tools discovered       NO
repository read        NO
write                   NO
```

This is why capability states must be recorded separately.

## 7. “Scan Tools” UI assumption was wrong

Troubleshooting initially referred to a **Scan Tools / Analyser les outils** button.

The actual 10 September `Nouveau plugin` dialog did not contain such a button.

The working UI sequence became:

```text
Créer
→ OAuth
→ plugin detail page
→ Actualiser
```

The future zero-knowledge installation kit must preserve this failed assumption so a novice is not sent searching for a nonexistent control.

## 8. Second GitHub Developer MCP: connected but initially zero actions

A second app was created:

```text
GitHub — bacoco TEST
https://api.githubcopilot.com/mcp
OAuth
```

Immediately after creation its detail page still said:

```text
Aucune action de l'application n'est disponible pour le moment.
```

So OAuth connection still did not prove usable tools.

After clicking **Actualiser**, **44 tools** appeared.

Representative tools included:

```text
get_me
get_file_contents
search_code
list_branches
create_branch
create_or_update_file
push_files
issue_read
issue_write
pull_request_read
create_pull_request
pull_request_review_write
merge_pull_request
```

### Trailing slash caution

The first app used `/mcp/`; the working app used `/mcp`.

Do **not** claim that the slash alone caused the failure. The refresh/app state also differed.

Use the known-good `/mcp` form for the installation recipe until equivalence is tested.

## 9. Interactive GitHub read — PASS

`get_me` returned:

```text
bacoco
```

`bacoco/chatgpt-cost-router` was read successfully.

Observed `main` SHA:

```text
6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

T01/T02 passed.

## 10. Issue round-trip — PASS

Temporary issue:

```text
[MCP TEST] Validate ChatGPT Developer MCP issue round-trip
```

was created as issue #1, read back, verified and closed.

T03 passed.

## 11. Branch/file/PR round-trip — PASS

Created branch:

```text
docs/chatgpt-cloud-cost-router-analysis-2026-09-10
```

from:

```text
6273cb87b98e94a1e04d9d439dfa400bbbb321cc
```

Committed the analysis document:

```text
ab5f66a556eab82bb7d80fcff71341f2dbbe7d13
```

Created PR:

```text
#2
```

and read its diff back through the same MCP.

T04 passed without Codex.

## 12. PR CI was not green

PR #2 showed failed/cancelled check runs.

No automatic merge occurred.

This proves why the system must keep:

```text
PR_CREATED
DIFF_VERIFIED
CI_PASS
MERGE_READY
MERGED
```

as distinct claims.

## 13. Scheduled Task → GitHub Developer MCP — PASS

A one-shot scheduler was instructed to use **only**:

```text
GitHub — bacoco TEST
```

and perform read-only validation on:

```text
bacoco/chatgpt-cost-router
```

It returned **PASS** with:

```text
authenticated login: bacoco

repository root: read successfully
branches: listed successfully

main SHA:
6273cb87b98e94a1e04d9d439dfa400bbbb321cc

other visible branch:
docs/chatgpt-cloud-cost-router-analysis-2026-09-10
at ab5f66a556eab82bb7d80fcff71341f2dbbe7d13

repository mutations: none
```

T07 passed.

This is a central project result:

> A ChatGPT Scheduled Task can invoke the custom GitHub Developer MCP and read authenticated GitHub state without Codex and without a paid OpenAI API key.

## 14. Unproven tests

Still explicitly unproven:

### T08 — scheduled write idempotency

Need two runs where the first creates one controlled artifact and the second creates no duplicate.

### T09 — direct coding + local executable verification

Need a bounded real code bug:

```text
read code
→ patch
→ Python/shell test
→ react to result
→ PR
```

without Codex.

### Codex Worker

Not yet tested and not yet needed for the proven GitHub workflows.

### Gmail Developer MCP

Not yet tested.

## 15. Wrong assumptions not to repeat

1. `plugin installed → callable` — false.
2. `OAuth connected → tools discovered` — false.
3. `actions visible in Settings → callable in current context` — false for built-in GitHub in the tested context.
4. `admin browser sees OAuth → ChatGPT sees OAuth` — false under stale cache.
5. `docs say Scan Tools → button exists` — false in tested UI.
6. `PR exists → safe to merge` — false.
7. `interactive success → scheduler success` — false until T07; now proven only for this custom GitHub MCP.
8. `one successful scheduler write → recurring write safe` — still false until T08.

## 16. Evidence format for future tests

Every meaningful test should record:

```text
test_id
date/time
execution context
Developer MCP name
authenticated identity
repository
base branch
base SHA
operation attempted
artifact created
commit SHA / issue / PR
result: NOT_TESTED | FAIL | PARTIAL | PASS
Codex used: yes/no
paid API used: yes/no
repository mutated: yes/no
notes / exact error
```

## 17. Current empirical capability matrix

```text
Normal ChatGPT reasoning/coding                    AVAILABLE
Python/shell in ChatGPT                            AVAILABLE, ephemeral
Cowboy — ARGH                                      PASS
Cowboy — Confisuite                                PASS
Built-in GitHub in tested restricted context       FAIL/FORBIDDEN
Standard Gmail in tested restricted context        FAIL/FORBIDDEN
Custom GitHub Developer MCP interactive read       PASS
Custom GitHub Developer MCP interactive write      PASS
Custom GitHub Developer MCP Scheduled Task read    PASS
Scheduled GitHub write idempotency                  NOT TESTED
Direct bounded code + local tests                  NOT TESTED
Codex Worker                                       NOT TESTED
Paid OpenAI API                                    NOT USED
```

This log is intentionally append-oriented: future failures should be added, not erased.
