# One-prompt project bootstrap

Replace only `TARGET_REPO` for the simplest use.

```text
TARGET_REPO=<owner>/<repo>

Bootstrap this GitHub repository for the ChatGPT cloud-first project workflow using
the current `main` of `bacoco/chatgpt-cost-router` as the installation source.

Resolve and pin the source repo SHA first. Read and apply
`skills/project-workspace-bootstrap/SKILL.md` and
`docs/PROJECT_BOOTSTRAP_PROTOCOL.md` from that exact SHA.

In TARGET_REPO, inspect existing instructions/state before writing. Install or
reconcile the canonical `.chatgpt/` workspace without deleting or blindly
overwriting project-specific information. Also copy the exact pinned
`cloud-to-codex-handoff` and `codex-to-cloud-return` skills into
`.agents/skills/` in TARGET_REPO, preserving unrelated existing skills. Use a
bootstrap branch/PR for an existing repo unless direct initialization is clearly
safer and authorized.

Create or reuse one primary repo-specific ChatGPT Scheduled Task/workspace launcher
when useful. Its prompt must re-read the target repo and `.chatgpt/` checkpoint
freshly on every run. Do not create a pointless frequent schedule only to keep a chat
alive.

After bootstrap, if there is already active project work, start with normal ChatGPT +
the authorized Developer MCPs and persist progress in `.chatgpt/CURRENT.md`.

If a real capability boundary is reached, use the source repo's
`cloud-to-codex-handoff` skill to write a GitHub handoff and give me the short prompt
for Codex. When Codex returns, use `codex-to-cloud-return` evidence and verify the
actual branch/SHA/diff/tests before continuing.

Do not use Codex merely because code is involved. Do not silently use paid APIs.
Treat GitHub Actions runner capacity as a separate budget/capability.

At the end, report exactly what was installed, the source and target SHAs,
branch/commit/PR, scheduler created or reused, current checkpoint, tests actually
performed, and remaining validation gaps.
```

Optional inputs may be added below `TARGET_REPO`:

```text
PROJECT_GOAL=<optional goal>
SCHEDULER_CADENCE=<optional real cadence>
CONSTRAINTS=<optional constraints>
```

If cadence is omitted, the bootstrap must not invent expensive recurring work.
