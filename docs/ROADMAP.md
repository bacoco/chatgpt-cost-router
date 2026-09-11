# Roadmap after the implementation/publication attempt

[Delivery status](AB_DELIVERY_STATUS_2026-09-11.md) is the authoritative checkpoint.
The owner's implementation request authorized source work, not resuming T38 or services.

A/shared changes and regression tests are published. The prepared B continuation,
physical worker split and packaging are in the source artifact, not fully on this
branch because a connector safety review blocked a dependency publication batch.
No alternate publication route was used; dependent B files were restored coherently.

Source review must compare the prepared artifact's manifest with the actual branch
before any future integration. Do not simply mark this roadmap complete based on
local files or the 177-test artifact result. The published subset has its own
134-test result. A draft delivery is not merge or deployment authorization.

Live acceptance remains separate: actual native connector discovery/read-back in
the intended account/surface, authorized cross-app workflow, private MCP attachment,
reviewed node identity/SSH bindings, real container containment where needed,
ordinary process lifecycle and deliberate service drain/rollback. No unrelated
mail, publication, model call or fleet job is authorized just to produce a PASS.

Provider quota ingestion, distributed account accounting, extra model providers,
automatic placement, PAIR and Serena remain optional future extensions. Unknown
quota stays unknown; a legacy worker mesh does not become project-isolated merely
because its source is moved. Preserve historical T01-T37 receipts and the stopped
quota experiment. See CURRENT for the exact publication boundary.
