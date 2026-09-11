# A/B source delivery and verification — 11 September 2026

Repository: `bacoco/chatgpt-cost-router`. Branch: `feat/ab-products-20260911`.
Validated code snapshot: `93944d8f6b7a973946d54cc6d0d4bdb77d4e1870`.

**GitHub delivery is performed, not a ZIP-only handoff.** The previous assertion that
GitHub write tools were unavailable was false. The connected `push_files` action
was invoked successfully; the code was reread by exact Git tree identifiers.

## Reproducible result

`python scripts/validate_ab.py --output /tmp/ab-validation`

201 tests executed: **200 PASS, zero failures, zero errors, one SKIPPED**.
The skipped test requires the optional official MCP SDK, absent from this environment.
See [the machine-readable receipt](validation.json) and [the losslessly compressed original test log](unittest.log.gz.b64).
Decode the log with `gzip.decompress(base64.b64decode(Path("unittest.log.gz.b64").read_bytes()))`
using Python standard-library `gzip`, `base64` and `pathlib.Path`; its SHA256 is in the receipt.
The complete trees for both products, shared contracts, decision engine, scripts,
tests, schemas, policy, examples and skills match the local validated source exactly.

## Parallel edits were integrated, not discarded

Three commits arrived while the original 78-file delivery was being published:
`65d1bea42cba65f4eda08ecbc6c34fd7eea7869e`,
`5aeee53b652a319b829b7e7a8f790ce1842602a1`, and
`54df9ff9bdad04284976dbaf75960e853accae09`.
Their 18 tests are retained unchanged and pass alongside the original suite.

The combined implementation preserves receipt-bound artifact reads, hard-link and
mid-read mutation rejection, private artifact transport, restricted raw commands,
root-SSH refusal and cleanup after monitor initialization errors. It also retains
supervisor fencing, node/runtime/policy pins, observed metrics, full lifecycle/list
interfaces and outbox publication independent of the original command file.
Both artifact payload names (`data`, `data_base64`) remain supported with chunk hashes.

## Scope and limitations

Validation used local temporary processes and loopback HTTP; native connectors were
simulated. No actual Gmail send, Cowboy publication, provider/model call, SSH job on
the owner's fleet, existing service reload or scheduler change was performed.
No main merge or deployment was performed. T38 remains paused.
Actual native Chat attachment, real connectors, remote hosts, macOS services and a
real container engine remain separate acceptance gates. Passing tests do not prove
those integrations or authorize their execution. The old ZIP/wheel is a historical
artifact: the verified GitHub source snapshot supersedes it.
