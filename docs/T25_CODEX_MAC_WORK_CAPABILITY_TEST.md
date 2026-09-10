# T25 — Codex Mac Work capability characterization

Purpose: characterize **Codex Mac Work** as its own execution surface. Do not infer any capability from ChatGPT.com Chat, Codex Mac Chat, or Codex CLI.

## Safety

Read-only test. No repository mutation, no commit, push, branch, issue, PR, Actions trigger, email send, draft creation, deployment, secret access, software install, global configuration change, or paid API.

## Required observations

From a fresh Codex Mac Work task, report:

1. exact surface/mode as observed;
2. model if observable;
3. available built-in connectors/apps relevant to GitHub, Gmail and files;
4. whether local filesystem/shell execution is actually invocable;
5. whether a local repository checkout is visible/usable;
6. whether GitHub repository content can be read without browser automation;
7. whether Gmail search/read capability is invocable without mutating mail;
8. whether browser/cloud-computer capability is present;
9. what state appears durable vs task-local;
10. whether the surface can read the project checkpoint and T20 handoff from `bacoco/chatgpt-cost-router` without mutation.

## Bounded execution

If GitHub/repository read access is available, read only:

- `.chatgpt/CURRENT.md`
- `docs/SURFACE_CAPABILITY_MAP.md`
- `.chatgpt/handoffs/T20/TO_CODEX.md`

and report current project status plus the original T20 handoff commit.

If Gmail read/search is available, run only one harmless query `newer_than:1d` with maximum 1 result and report success/count only; do not quote content.

If shell/local filesystem is available, run only harmless environment/read commands (`pwd`, OS/arch, `git --version`, `python3 --version` if installed). Do not create files.

## PASS semantics

T25 is not all-or-nothing. Each capability must be reported `PASS`, `NOT_AVAILABLE`, or `NOT_TESTED`. Overall `T25_CHARACTERIZATION=PASS` means the Work surface was independently characterized with at least one actually executed read capability and no forbidden effect. It does not imply that every capability exists.

Paid API must remain unused.