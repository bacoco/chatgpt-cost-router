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
│ local verify     ✅      │        │ draft delete     ❌      │        │ tests/reconcile   ✅      │
│ Gmail Dev MCP    ⛔      │        │ repo lane        ?       │        │ remote write      not needed
│ paid API         NO      │        │ paid API         NO      │        │ paid API          NO      │
└────────────┬─────────────┘        └────────────┬─────────────┘        └────────────┬─────────────┘
             │ validated                         │ validated Gmail                     │ validated local worker
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
                         │ TO_CODEX.md  → specialist handoff                     │
                         │ RETURN_FROM_CODEX.md → verified return                │
                         └──────────┬───────────────────────────────────┬──────────┘
                                    │                                   │
                         validated  │                                   │ future / dashed
                                    ▼                                   ▼
                         ┌──────────────────────┐            ┌─────────────────────────────┐
                         │ Cloud → Codex → Cloud│            │ Multi-account / providers   │
                         │ T20/T23/T24 ✅       │            │ OpenAI account B/C          │
                         │ exact-SHA handoff    │            │ Claude Code / terminal      │
                         │ return reverified    │            │ TO_WORKER / RETURN_WORKER   │
                         └──────────────────────┘            │ parallel branches/worktrees │
                                                             └─────────────────────────────┘

                         ┌──────────────────────────┐
                         │ Codex Mac — Work         │
                         │ capability matrix: ?     │
                         │ GitHub/Gmail/shell: ?    │
                         │ shared agentic pool:     │
                         │ product-documented,      │
                         │ not empirically mapped   │
                         └──────────────────────────┘
```

## Capability matrix

| Capability | ChatGPT.com Chat | Codex Mac Chat | Codex CLI Mac | Codex Mac Work | GitHub repo |
|---|---|---|---|---|---|
| Normal reasoning/chat | ✅ PASS | ✅ PASS | ✅ PASS | ? NOT TESTED | — |
| GitHub read | ✅ PASS via Developer MCP | ? not separately classified | ✅ PASS via git | ? NOT TESTED | ✅ durable |
| GitHub write / branch / PR | ✅ PASS | ? not separately classified | possible toolchain present; remote write not required by T10 | ? NOT TESTED | ✅ durable |
| Scheduled Task | ✅ PASS | — | — | ? NOT TESTED | stores checkpoints/receipts |
| Same-chat continuation after scheduler | ✅ PASS | — | — | ? NOT TESTED | durable checkpoint supports recovery |
| Fresh-chat recovery from repo | ✅ PASS | ? | ✅ repo rediscovery/reconcile PASS | ? | ✅ source of truth |
| Local shell / Python tests | ✅ PASS for bounded verification | ? mode-specific | ✅ PASS, 40/40 | ? NOT TESTED | stores code/evidence |
| Persistent local workspace | no guarantee / treat ephemeral | ? NOT TESTED | ✅ PASS across independent sessions | ? NOT TESTED | ✅ remote durable state |
| Gmail read/search/Sent | ⛔ canonical Developer-MCP path missing | ✅ PASS built-in Gmail | — | ? NOT TESTED | — |
| Gmail draft/send | ⛔ canonical Developer-MCP path missing | ✅ PASS; one real deduplicated self-send | — | ? NOT TESTED | — |
| Cloud↔Codex handoff | ✅ produce + verify | receiver mode not separately classified | can consume repo state; provider-neutral test later | ? | ✅ exact-SHA transfer bus |
| Create new GitHub repo | ⛔ Developer MCP returned 403 | ? | possible via `gh`, not part of validated T10 | ? | existing repos validated |

Legend: ✅ empirically verified; ⛔ blocked/unavailable in the tested context; ❌ explicitly unavailable action; ? not independently tested/classified.

## Allowance / cost map

Do not collapse these into one “token” number.

| Pool / cost | Operational rule |
|---|---|
| ChatGPT normal-chat allowance | Track separately. S0→S1 showed no observable change in the displayed agentic counters after a ChatGPT.com + GitHub-MCP read task; UI granularity was too coarse for a useful burn test. |
| OpenAI agentic / Codex allowance | Applies to Codex/eligible agentic surfaces according to current product documentation; exact per-mode accounting is not fully empirically mapped here. |
| Codex Mac Chat | Capability validated for Gmail; allowance consumption was not measured to useful precision. |
| Codex CLI | Real ChatGPT-account-authenticated Codex CLI validated; treat as consuming the applicable Codex/agentic allowance, not paid API, unless account evidence says otherwise. |
| Codex Mac Work | Keep separate from Mac Chat. Product documentation says eligible Work/Codex agentic usage shares an agentic allowance, but this mode still needs its own capability test. |
| Additional OpenAI accounts A/B/C | Separate account pools. Never assume quota sharing across accounts. |
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
  → Codex Work only after its own capability test
  → another OpenAI account or Claude only through an explicit GitHub handoff
  → paid API only by explicit exception
```

## Still open

- Codex Mac Work capability test.
- Canonical Gmail Developer MCP from ChatGPT/Scheduled Tasks, only if scheduler-native Gmail is still required.
- Multi-account OpenAI handoff and concurrency tests.
- Claude Code / terminal handoff and return verification.
- Provider-neutral `TO_WORKER` / `RETURN_FROM_WORKER` layer.
- Distinct Ubuntu/cloud always-on worker only if a real cross-machine requirement appears.
- New-repository creation through the tested GitHub Developer MCP remains blocked by the observed 403; existing-repository work is validated.
