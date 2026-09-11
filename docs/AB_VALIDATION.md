# Validation boundaries and reproducibility

## Source provenance

The documentation base was `6a5b72c490b319f04d90c97ecd47dcb331ce19bd`.
The implementation branch was reread at
`9a24054bd9ad392a2b16f158fb326cb5e1367b4d` (newer than the pasted `e389cee` checkpoint).
A later upstream commit `cd897ddf3856ffdabef68ba1a71b43dd99efad46` changed six A files; those exact
files were fetched and their session/account/recovery corrections preserved before
final validation. The delivered patch applies against that newer commit.
Source was reconstructed from a SHA256-verified historical export and exact GitHub
file reads. Runtime/test/schema/example/script trees were checked against Git tree
hashes before modifications. The delivery contains a change patch, not fabricated
remote Git history and not a claim to include every historical repository document.

## GitHub delivery correction

The original ZIP-only response incorrectly claimed that GitHub write actions were
unavailable. The connector was rediscovered, `push_files` was executed successfully,
and the implementation was committed on `feat/ab-products-20260911` starting from
`cd897ddf3856ffdabef68ba1a71b43dd99efad46`. No main merge, service reload, workflow
dispatch, scheduler modification or job on the owner's fleet was performed.

A fresh local execution of `scripts/validate_ab.py` ran 201 tests: 200 passed,
zero failures, zero errors, one optional official SDK test skipped. This final run
includes the 18 tests from the three interleaved commits identified in the delivery
receipt; their security fixes were integrated without discarding lifecycle/recovery
features. The verified code snapshot is `93944d8f6b7a973946d54cc6d0d4bdb77d4e1870`.
The test receipt
and publication evidence under `../audits/ab-implementation-20260911/` distinguish
local validation from source delivery and from unperformed live acceptance.

## Evidence produced by this delivery

`scripts/validate_ab.py` writes a test-by-test JSON receipt and a raw unittest log.
It records runtime/dependency versions, source hashes, duration, failures and skips.
The earlier bundle included local demo, wheel-install and patch round-trip checks.
It is historical and is superseded by the verified GitHub source; those packaging
receipts are not presented as tests of the final combined code. A checksum is integrity evidence, not
proof that the tested machine matches a user's production fleet.

Baseline/regression unit tests include mocked legacy providers/SSH and pure policy
logic. New tests additionally run ordinary local subprocesses, loopback HTTP,
concurrent SQLite operations, failure injection, exact Git staging/rollback, bootstrap,
symlink/FIFO checks and typed local gateway-to-node CLI calls.

A's four-step demonstration uses SIMULATED_CONNECTORS. B's demo and lifecycle tests
use REAL_LOCAL_PROCESS. The tests do not send real email, modify a connected website,
invoke a provider/model, launch user-machine jobs or reload a real service.

## Mandatory distinctions

| Check | Meaning |
| --- | --- |
| Unit/regression suite | Executed against the delivered local source, not inferred from old test counts. |
| Loopback MCP HTTP | Actual HTTP discovery/call/SSE exchanges with a local fixture server. |
| MCP registration recorder | Checks public wiring and typed callable behavior; not execution of the official SDK. |
| Official MCP SDK | A separate optional in-process test. SKIPPED when the pinned package is unavailable; never reported as PASS by the recorder test. |
| Packaging | Historical pre-integration wheel smoke only; not claimed as validation of the final combined source. |
| Live connector workflow | NOT RUN. Requires actual tool bindings, account permission, authorization and read-back. |
| Real remote fleet / macOS | NOT RUN. No assertion about current services, connectivity or deployments. |
| Container engine isolation | NOT RUN on an actual engine. Command/policy/owned-ID cleanup unit tests are not an OS containment certificate. |
| GitHub feature-branch commits | PERFORMED through the connected `push_files` action; see the delivery receipt. |
| Main merge / deployment | NOT PERFORMED. The operational pause remains in force. |

## Dependencies and protocol

The delivery pins the optional official MCP package to 2.2.0; it was not installed
in the revalidation environment. The small built-in HTTP client intentionally uses
the legacy `initialize` protocol exchange (up to 2025-11-25), not
the newer discovery-first exchange. SDK server compatibility and real attachment
must be checked with the actual installed SDK and host client.

Official references:
- https://pypi.org/project/mcp/2.2.0/
- https://py.sdk.modelcontextprotocol.io/

## Operational security

Operator configuration, local binaries, Git repository metadata and the OS user are
trusted. Workspace separation is not hostile-code containment. Journals and receipts
are private local files; do not publish their private contents as relay logs.
A records caller-observed evidence; it cannot independently prove a driver actually
called an external connector. Authentication and user consent must exist at that boundary.

Nothing in a passing local suite resumes T38 or authorizes deployment.
