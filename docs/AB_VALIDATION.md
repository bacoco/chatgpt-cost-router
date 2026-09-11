# Validation and evidence

The current result and scope are recorded in [deployment status](DEPLOYMENT_STATUS.md). Historical counts certify their own source trees only; do not add counts across revisions or equate local tests with CI/live fleet acceptance.

## Reproduce source validation

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_ab.py --output /tmp/ab-validation
```

The validator produces JSON cases, source hashes and an unfiltered test log. Full source must include the tracked skill metadata. Installing the optional MCP dependency enables the official-SDK smoke test; an unavailable dependency must remain an explicit skip, not a fabricated pass.

The owner's `scripts/ab_validate_snapshot.py` validates an exact Git snapshot with the installed interpreter without switching the working checkout. It also checks relative file links in the current guides. Link-path checks do not certify every external URL or prose assertion.

## Live acceptance

Record exact runtime/policy revisions, service state, completed process, verified artifact, cancellation and transport read-back. For GitHub relay tests, retrieve a terminal process_result separately from submission. For MCP, check initialize, tools/list and an actual tool call directly on loopback, without ambient proxies.

The September 11 MacBook installation passed all 209 tests at runtime revision `10b3ee3e438d57b210b1155e2dbaf19aac9b00db`, including the official SDK. Its initial archive omitted two skill documents; those were restored from that exact commit and recorded as supplemental assets without changing runtime code. Later source/helper tests are reported separately until a full new snapshot result is available.

Real A workflows on Gmail/Cowboy, authenticated Chat attachment, inaccessible hosts, actual container isolation and reboot/rollback drills must not be marked validated by the local demo. The demo intentionally simulates A connectors and executes a real local B process.
