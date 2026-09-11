# ChatGPT project workspace

Project: `bacoco/chatgpt-cost-router`

Purpose: develop two independent products in the existing repository:
- **A — Chat-first Operations:** complete authorized work from normal Chat through
  Gmail, GitHub, WordPress/Cowboy and all other available plugins/connectors;
  read, reason, edit, send, publish, coordinate and verify, not only create issues.
- **B — Fleet Operator:** machine access, process execution/management, supervision,
  monitoring and results, usable without Chat; distribution and model workers optional.

The historical cost/capability router remains a decision-support component, not the
entire product definition. A does not require B for connector-only work.
A can invoke B as a tool without requiring another LLM.

Canonical source kit: this repository itself.
Source-kit revision used for this bootstrap: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`.
That SHA is historical bootstrap provenance, not the current `main` revision.

Durable-state rule: GitHub is the source of truth for project instructions, code,
checkpoints and delivery evidence. Chat/scheduler-local files are workspaces only.
B also has machine-local runtime state; GitHub receipts are not live fleet telemetry.
Credentials and private runtime configuration must not be committed.

## Current entry points and authority

Read `README.md`, `.chatgpt/CURRENT.md`, `docs/ARCHITECTURE.md` and
`docs/ROADMAP.md`. The product boundary is recorded in
`docs/TWO_PROJECTS_AND_PAIR_2026-09-11.md`; historical verification is recorded in
`docs/VALIDATION_STATUS_2026-09-11.md` and the exact test receipts.

The A/B code split and core runtimes are committed on `feat/ab-products-20260911`.
Read docs/AB_USAGE.md and docs/AB_VALIDATION.md for actual entry points and evidence.
No main merge or deployment was performed. T38, installations and new fleet jobs
remain paused unless the owner explicitly resumes them. Code validation and a
feature-branch commit are not deployment instructions.

## Preferred execution, subject to the current task and pause

1. Stay in normal Chat and use the authorized tools that can complete the request.
2. Act directly through Gmail, GitHub, Cowboy or other available connectors and
   verify the result; an issue/handoff is not the default substitute for completion.
3. Use a Scheduled Task only when available and needed for launching/repetition;
   it is not required for ordinary connector work.
4. Use local deterministic tools or B for machine work when necessary and authorized.
5. Invoke Codex/Claude/Work only for an explicit, useful capability boundary.
6. Use a paid model API only by explicit exception. CI/compute costs also have gates.

Never silently switch surface or hide another model call behind an app.
Preserve the user's stopped quota experiment. Check capabilities by exact action,
resource/account, surface and session; yesterday's proof is not a universal entitlement.

The historical GitHub-project reference profile uses `GitHub — bacoco TEST`;
`GitHub Actions — bacoco TEST` is optional with a separate runner-capacity gate.
Other apps are selected for the actual task; this list does not restrict A to GitHub.
For WordPress use Cowboy, not WPVibe.

Bind every operation to its project or authorized task context. Keep GitHub identity,
OS identity and provider account separate. Do not broaden repository, merge,
release, mail, publication, deployment, secret or paid-API permissions.
