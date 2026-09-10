# Use cases

These are candidate plans, conditional on current scoped evidence and authorization.
The executable [fixtures](../tests/routing_cases.json) record all prerequisites.

| Task | Candidate plan | Actual deciding requirement |
|---|---|---|
| Research or repository review | CHAT | Source/repository reading and sufficient context |
| Issue, targeted edit, PR | CHAT + GitHub transport | Required write permissions and verifiable CI on the right commit |
| Refactor or iterative debugging | CODEX or another sufficient context | Local environment/test loop requirements, not a file-count threshold |
| Recurring research | SCHEDULED_CHAT trigger and executor | Scheduling plus fresh tools at each run |
| ComfyUI / inference | LOCAL_TOOL via an installed adapter | Reachable hardware/workflow, authorization and comparable cost |
| UI-only administration | WORK with a suitable browser | Actual authenticated UI access to the target |
| Hourly API + delta | Scheduled trigger plus capable API/compute executor | Composite steps, state and recovery semantics |
| Post-implementation review | Current context or verified destination | Remaining capabilities and marginal transfer benefit |
| Synchronous isolated workers | Verified WORK/CODEX/API capability | Genuine synchronous delegation; asynchronous schedules are a different requirement |
| SSH or desktop application | A context with proven target access | A surface name alone does not establish SSH or local-machine access |

The numbers 4, 20 and 120 files are examples, not routing thresholds. Some one-file
changes require complex integration; some broad mechanical changes do not.
