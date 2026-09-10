# T25 — Codex Mac Work capability characterization

- surface: Codex desktop on Mac
- mode: Work, user-declared; UI mode label not independently inspected
- model: exact variant UNKNOWN
- result: PASS characterization
- paid_API_used: NO
- forbidden_effects_performed: NO

## Executed capabilities

- GitHub direct connector read: PASS at pinned commit `67964111f6267763b2418bb035b40efd6b9da022`
- Gmail search `newer_than:1d`: PASS, result count 1
- local filesystem/task directory: observed at `/Users/loic/Documents/Codex/2026-09-10/this-is-t25-codex-mac-work`
- shell: PASS for `pwd`, `uname -a`, `git --version`, `python3 --version` only
- OS: Darwin 25.3.0 arm64
- git: 2.50.1 (Apple Git-155)
- python3: 3.9.6
- browser/Mac computer tooling: exposed, not invoked
- cloud computer: UNKNOWN
- plugin catalog: visible in Work UI; potential plugins are VISIBLE/INSTALLABLE only unless individually connected and executed

## Handoff finding

The requested T20 handoff read failed at `main`/pinned T25 commit because `.chatgpt/handoffs/T20/TO_CODEX.md` is not present there. Independent GitHub verification from ChatGPT confirmed the file exists on branch `test/t20-cloud-to-codex-handoff-20260910`. This is a test-target error, not evidence of a Work GitHub-read limitation.

## Not yet proven

- Work workspace persistence across independent sessions
- Gmail message read in Work
- Gmail draft/send in Work
- effective GitHub write/commit/push from Work
- cloud-computer execution

Next: T26 should target the actual T20 branch and prove one bounded Work return commit/push on a dedicated test branch, followed by independent ChatGPT GitHub verification.
