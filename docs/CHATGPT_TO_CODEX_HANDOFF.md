# ChatGPT Cloud → Codex handoff through GitHub

**Purpose:** let ChatGPT Cloud do as much work as it can, then hand only the remaining work to Codex without copying a giant conversation or forcing Codex to rediscover the project.

**Core rule:** GitHub is the durable transfer bus. The ChatGPT conversation is a workbench, not the only project memory.

## 1. When to hand off

Do not send work to Codex just because the task contains code. Stay in ChatGPT Cloud while Chat + Developer MCPs + bounded local verification are sufficient.

Hand off when a concrete remaining requirement benefits from Codex, for example:

- a persistent checkout is needed;
- repeated edit/test/fix loops are becoming cumbersome in Chat;
- dependency installation or a project-specific toolchain is required;
- the change is broad enough that a durable local workspace materially reduces risk;
- long-running builds/tests are required;
- repository exploration is too large for an efficient bounded Chat session.

The handoff is a change of executor, not a reset of the task.

## 2. Prepare the repository before giving Codex the task

Before handoff, ChatGPT should persist a compact state packet in the target repository.

Recommended project convention:

```text
.chatgpt/
  PROJECT.md
  CURRENT.md
  handoffs/
    <task-id>/
      TO_CODEX.md
      handoff.json        # optional machine-valid v2 packet
      RETURN_FROM_CODEX.md
```

A repository may choose another path, but use one canonical location consistently.

`CURRENT.md` is the latest concise project state. `TO_CODEX.md` is the human-readable handoff for a specific task. `handoff.json` is optional when the project wants to use the repository's formal Surface Handoff v2 contract.

Never put passwords, PATs, API keys, OAuth tokens, SSH private keys or unrelated conversation history in these files.

## 3. Minimum contents of TO_CODEX.md

The handoff must contain enough information for Codex to start from evidence rather than rediscovering the conversation:

```text
Task ID
Goal / definition of done
Repository owner/name
Base branch + exact base SHA
Working branch + exact current SHA
Issue / PR numbers if any
What ChatGPT already did
Files already inspected
Files already modified
Tests already executed + exact results
Known environment limitations
External effects already completed
Remaining work only
Required tests before completion
Constraints / forbidden actions
Authorized scope
Expected return artifact
```

The exact SHA is mandatory for repository work. A branch name alone is not enough because the branch may advance between ChatGPT and Codex.

## 4. Canonical takeover prompt for Codex

For Codex Desktop/CLI, the user should be able to paste a short prompt like this:

```text
You are taking over an existing task from ChatGPT Cloud.

Repository: <owner>/<repo>
Handoff: .chatgpt/handoffs/<task-id>/TO_CODEX.md
Expected handoff commit: <40-character SHA>

Start by fetching the repository and verifying that the handoff file and referenced
working branch/commit still match the repository state. Read `.chatgpt/PROJECT.md`,
`.chatgpt/CURRENT.md`, the handoff, and only the referenced project files needed for
the remaining work.

Do not redo work already marked completed unless its evidence is stale or invalid.
Do not broaden scope or permissions. Complete only the remaining work, run the
required tests, and preserve the user's constraints.

When finished, write `.chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md` containing:
- resulting branch and exact commit SHA;
- files changed;
- tests actually run and their results;
- remaining work, if any;
- blockers/uncertainties;
- whether any external effect was performed.

Commit the return artifact with the code changes. Do not merge unless explicitly
authorized.
```

For a local Codex checkout that already exists, replace "fetching the repository" with "fetch and reconcile the existing checkout". Still verify the exact SHA.

## 5. Why the prompt is intentionally short

The full project history belongs in GitHub, not in a giant handoff prompt.

The prompt should tell Codex **where the authoritative state is**, what to verify, and what remains. This avoids re-sending a long ChatGPT transcript and reduces the chance that Codex acts on stale prose.

Preferred transfer:

```text
ChatGPT conversation
   -> compact GitHub checkpoint/handoff
   -> short Codex takeover prompt
   -> Codex reads exact repo state
```

Not:

```text
copy entire ChatGPT conversation
   -> paste thousands of lines into Codex
   -> hope it reconstructs the current repo
```

## 6. Return from Codex to ChatGPT

Codex should leave a durable return artifact and a resulting commit/PR. ChatGPT can then resume with:

```text
Continue task <task-id> from repository <owner>/<repo>.
Read `.chatgpt/handoffs/<task-id>/RETURN_FROM_CODEX.md` and verify the referenced
branch and commit against current GitHub state. Re-read the actual diff/tests before
accepting the return. Continue only the remaining work.
```

ChatGPT must treat `RETURN_FROM_CODEX.md` as a claim to verify, not proof by itself.

The loop can therefore be bidirectional:

```text
ChatGPT Cloud
   -> GitHub handoff
   -> Codex
   -> GitHub return + commit/PR
   -> ChatGPT Cloud review / publication / next step
```

## 7. Relation to Surface Handoff v2

This repository already defines a formal handoff contract in `HANDOFF_SPEC.md` and `handoff.schema.json`.

For automation, `handoff.json` should follow that v2 contract and preserve task/operation identity, repository/commit, authorization, required tests, evidence and completion criteria.

For a non-technical user, `TO_CODEX.md` is the friendly entry point. The Markdown and JSON should reference the same task, repo, branch and commit; do not maintain contradictory parallel truths.

## 8. Safety and idempotency

Before Codex mutates the repository:

1. fetch/re-read current state;
2. verify the handoff commit and working branch;
3. detect whether a requested issue/branch/PR already exists;
4. reconcile ambiguous prior external effects;
5. stop rather than blindly repeat an effect whose outcome is unknown.

A handoff grants no new permission. If ChatGPT was authorized only to review, the Codex handoff cannot silently upgrade that to merge/deploy/release.

## 9. Cost-routing implication

The preferred route becomes:

```text
ChatGPT Cloud
  -> GitHub Developer MCP
  -> Scheduler / scheduler-result chat when useful
  -> ChatGPT local verification when sufficient
  -> persistent GitHub handoff
  -> Codex only for the remaining specialist work
  -> GitHub return
  -> ChatGPT again when sufficient
  -> paid API only by explicit exception
```

This is more efficient than choosing one surface for the whole project. Route **the remaining action**, not the project identity.

## 10. Validation test — T20 Cloud → Codex → Cloud

Run this after the Codex macOS lane is configured:

1. ChatGPT performs a bounded first part of a safe repository task.
2. ChatGPT writes `TO_CODEX.md` with exact branch/SHA and remaining work.
3. Start Codex with only the short takeover prompt above.
4. Codex verifies the repository, completes the remaining work and writes `RETURN_FROM_CODEX.md`.
5. ChatGPT reads the return through GitHub, verifies branch/SHA/diff/tests and reports acceptance or discrepancy.
6. Confirm no transcript copy and no paid API key was needed.

PASS requires a verifiable round-trip, not merely a generated handoff file.
