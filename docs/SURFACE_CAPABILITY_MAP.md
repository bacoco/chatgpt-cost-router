# Surface capability map — validated execution lanes

This is the concise operational map for `bacoco/chatgpt-cost-router` as of 2026-09-10. GitHub is the durable source of truth and transfer bus. Solid arrows are empirically validated. Dashed arrows are not yet validated or are optional future lanes.

```text
┌──────────────────────────┐        ┌──────────────────────────┐        ┌──────────────────────────┐
│ ChatGPT.com — Chat       │        │ Codex Mac — Chat         │        │ Codex CLI — Mac terminal │
│                          │        │                          │        │                          │
│ GitHub Dev MCP   ✅      │        │ Gmail built-in   ✅      │        │ local shell       ✅      │
│ repo read/write  ✅      │        │ read/search      ✅      │        │ persistent FS     ✅      │
│ branch/PR        ✅      │        │ draft/send       ✅      │        │ git/gh/python/node✅      │
│ Scheduler        ✅      │        │ Gmail dedup      ✅      │        │ persistent repo   ✅      │
│ local verify     ✅      │        │ draft delete     ❌      │        │ codex exec worker ✅      │
│ Gmail Dev MCP    ⛔      │        │ repo lane        ?       │        │ paid API          NO      │
└────────────┬─────────────┘        └────────────┬─────────────┘        └────────────┬─────────────┘
             │ validated                         │ validated Gmail                     │ validated local/headless worker
             │                                   │                                      │
             └──────────────────────┬────────────┴──────────────────────┬───────────────┘
                                    │                                   │
                         ┌──────────▼───────────────────────────────────▼──────────┐
                         │                 GITHUB REPOSITORY                      │
                         │                                                       │
                         │ durable source of truth / transfer bus                │
                         │ main + branches + commits + PRs                       │
                         │ .chatgpt/PROJECT.md + CURRENT.md + SCHEDULER.md        │
                         │ receipts / evidence                                   │
                         │ exact-SHA handoffs + verified returns                 │
                         └──────────┬───────────────────────────────────┬──────────┘
                                    │                                   │
                         validated  │                                   │ future / dashed
                                    ▼                                   ▼
                         ┌──────────────────────┐            ┌─────────────────────────────┐
                         │ Cloud → Codex → Cloud│            │ Worker mesh                 │
                         │ T20/T23/T24 ✅       │            │ OpenAI account A/B ✅       │
                         │ exact-SHA handoff    │            │ remote Codex device ✅      │
                         │ return reverified    │            │ quota-aware logic ✅        │
                         └──────────────────────┘            │ cross-provider routing ?    │
                                                             └─────────────────────────────┘

                         ┌──────────────────────────┐
                         │ Codex Mac — Work         │
                         │ GitHub read/write ✅      │
                         │ handoff read/return ✅    │
                         │ Gmail search      ✅      │
                         │ local shell/Python✅      │
                         │ persistence       ?      │
                         └──────────────────────────┘
```

## Capability matrix

| Capability | ChatGPT.com Chat | Codex Mac Chat | Codex CLI Mac | Codex Mac Work | GitHub repo |
|---|---|---|---|---|---|
| Normal reasoning/chat | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS | — |
| GitHub read | ✅ PASS via Developer MCP | ? not separately classified | ✅ PASS via git | ✅ PASS direct connector | ✅ durable |
| GitHub write / branch / PR | ✅ PASS | ? not separately classified | toolchain available; remote write not required by T10/T27 | ✅ write/commit to dedicated branch PASS; PR not tested | ✅ durable |
| Scheduled Task | ✅ PASS | — | — | ? NOT TESTED | stores checkpoints/receipts |
| Same-chat continuation after scheduler | ✅ PASS | — | — | ? NOT TESTED | durable checkpoint supports recovery |
| Fresh-chat recovery from repo | ✅ PASS | ? | ✅ repo rediscovery/reconcile PASS | ? | ✅ source of truth |
| Local shell / Python tests | ✅ PASS for bounded verification | ? mode-specific | ✅ PASS, 40/40 | ✅ shell/Python commands PASS; full tests not part of T25 | stores code/evidence |
| Persistent local workspace | no guarantee / treat ephemeral | ? NOT TESTED | ✅ PASS across independent sessions | ? NOT TESTED | ✅ remote durable state |
| Headless/callable worker | scheduler can dispatch external tools | ? NOT TESTED | ✅ PASS via `codex exec` from normal shell; 10,215 tokens reported in T27 | Work is callable interactively; headless Work not tested | coordination bus |
| Gmail read/search/Sent | ⛔ canonical Developer-MCP path missing | ✅ PASS built-in Gmail | — | ✅ search PASS; full read not tested | — |
| Gmail draft/send | ⛔ canonical Developer-MCP path missing | ✅ PASS; one real deduplicated self-send | — | ? NOT TESTED | — |
| Cloud↔Codex handoff | ✅ produce + verify | receiver mode not separately classified | can consume repo state; provider-neutral test later | ✅ handoff read + pushed return PASS (T26) | ✅ exact-SHA transfer bus |
| Multiple isolated OpenAI workers | broker/controller can address aliases | — | ✅ PASS — two distinct `CODEX_HOME` account workers | — | stores non-secret registry/evidence |
| Remote worker dispatch | controller role possible | — | ✅ PASS — Tailscale Serve second-device dispatch to `openai-B` (T32) | — | durable receipts/state |
| Quota-aware selection logic | — | — | ✅ PASS for supplied observations; live provider ingestion unknown | — | may store non-secret observations |
| Create new GitHub repo | ⛔ Developer MCP returned 403 | ? | possible via `gh`, not part of validated T10/T27 | ? | existing repos validated |

Legend: ✅ empirically verified; ⛔ blocked/unavailable in the tested context; ❌ explicitly unavailable action; ? not independently tested/classified.

## Allowance / cost map

Do not collapse these into one “token” number.

| Pool / cost | Operational rule |
|---|---|
| ChatGPT normal-chat allowance | Track separately. S0→S1 showed no observable change in the displayed agentic counters after a ChatGPT.com + GitHub-MCP read task; UI granularity was too coarse for a useful burn test. |
| OpenAI agentic / Codex allowance | Applies to Codex/eligible agentic surfaces according to current product documentation; exact per-mode accounting is not fully empirically mapped here. |
| Codex Mac Chat | Capability validated for Gmail; allowance consumption was not measured to useful precision. |
| Codex CLI | Real ChatGPT-account-authenticated Codex CLI validated. T27 headless `codex exec` reported `10,215` tokens for one bounded call; this is useful per-invocation telemetry but is not itself a direct quota-decrement measurement. Treat it as consuming the applicable Codex/agentic allowance, not paid API, unless account evidence says otherwise. |
| Codex Mac Work | T25/T26 empirically validate GitHub read, a pushed one-file GitHub return, Gmail search, local filesystem, shell and Python. Workspace persistence remains untested. Treat usage as part of the applicable Work/Codex agentic pool, not paid API, when signed in through ChatGPT. |
| Additional OpenAI accounts A/B/C | Keep each account as a distinct worker budget/identity. Do not assume quota sharing across accounts. |
| Claude / Anthropic | Separate provider/account allowance or billing. Measure independently. |
| GitHub Actions | Independent GitHub runner capacity/cost. Control-plane MCP works; hosted runner allowance was exhausted during the observed test. |
| Paid OpenAI API | Explicit separate billing path. **Not used** in the validated campaign. |
| Other paid APIs | Explicit separate provider billing; never silently enabled. |

## Routing rule

Use the cheapest already-paid, verified surface that can safely complete and verify the remaining work. Keep GitHub as the neutral durable state. When changing surface, account, or provider, transfer only the remaining bounded work through an exact-SHA handoff; never rely on opaque chat memory.

```text
ChatGPT.com first
  → Developer MCP when external state/actions are needed
  → local ChatGPT verification when sufficient
  → Codex Mac Chat for capabilities proven there (for example Gmail)
  → Codex CLI when persistent local engineering state / shell loops are useful
  → `codex exec` when a controller needs a non-interactive callable Codex worker (T27)
  → Codex Work for verified connector/local-tool/handoff work (T25/T26)
  → isolated OpenAI worker A/B through the validated broker; remote Tailscale node is PASS (T28/T30/T32)
  → Claude/other providers only after their adapters/handoffs are independently validated
  → paid API only by explicit exception
```

## Still open

- Codex Mac Work persistence across separate Work sessions remains untested; core read/write handoff lane is PASS (T25/T26).
- Canonical Gmail Developer MCP from ChatGPT/Scheduled Tasks, only if scheduler-native Gmail is still required.
- Automatic/reliable live 5-hour/weekly allowance ingestion remains unproven; T31A only routes on trusted supplied observations.
- Remote node registration/discovery and always-on supervision remain to build; T32 proves the private transport primitive.
- A separately shared external Tailscale user has not yet been live-tested; second-device remote dispatch is PASS.
- Claude Code / other-provider adapter and provider-neutral handoff remain to validate.
- Useful concurrency remains deferred until a real workload benefits from it.
- New-repository creation through the tested GitHub Developer MCP remains blocked by the observed 403; existing-repository work is validated.
