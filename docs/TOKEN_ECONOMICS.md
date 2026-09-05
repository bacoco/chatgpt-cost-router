# Cost, quota and measurement

Initial usage-reduction hypotheses remain roughly 50% conservative, 65–70% central,
and 80% in favorable workloads. The previously proposed 20–50% delegated-context
reduction is also a hypothesis. None is billing telemetry or a measured benefit.

## Routing estimates

The evaluator compares integer USD micro-units: 1 USD = 1,000,000 units.
For every step include execution (provider/API/local compute), transfer, expected
retry and CI costs. Include queue/active duration when it affects the user's limit.
Use null for unknown cost; never encode ignorance as free execution. The fixed
surface order is only a tie-break. Calling a paid model through MCP is still paid.

The router trusts supplied estimates and cannot guarantee invoices or quotas. It
does not estimate costs from model names or hardcoded provider prices. An adapter
must obtain current estimates relevant to the user's account and workload.

## Baseline before changing routes

Capture a baseline first, then compare matched task classes and equivalent required
quality. Record task/run/policy identity, task class, required capabilities, selected
plan, completion status, actual costs by provider/local/CI/transfer/retry category,
active duration, handoff bytes, quality outcome and observable Work/Codex usage.
Unknown measurements remain unknown; do not report them as zero.

Keep unsuccessful, blocked and retried tasks visible. Report completion rate and
quality regression alongside usage/cost. Compare matched successful workloads for
unit-cost savings and disclose all exclusions and sample counts. Raw usage falling
because fewer tasks were attempted is not a routing gain. Compare monetary savings,
quota displacement and time separately; do not add unlike units.

Unnecessary escalation needs a human-labeled sufficient alternative under the same
capabilities and constraints. Label by policy version, report denominator/confidence,
and separate this evaluation from deterministic fixture agreement.

A typical handoff target is <5 KiB; report byte distribution and outliers. Retain
essential scope/evidence through references rather than silently truncating it.
