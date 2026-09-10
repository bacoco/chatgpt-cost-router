# Local verification limitations — 10 September 2026

This record prevents the local ChatGPT execution evidence from being overstated.

## What was successfully executed

A working tree was reconstructed locally from exact repository files retrieved through `GitHub — bacoco TEST`. The available ChatGPT container reported:

```text
Python 3.13.5
PyYAML 6.0.3
jsonschema 4.26.0
```

Using that environment:

```text
python -m unittest discover -s tests -v    PASS — 39/39
python scripts/build_schemas.py            PASS — generated files identical
synthetic CLI routing replay               PASS
```

This is valid executable evidence for the fetched code under the available ChatGPT runtime.

## What could not be reproduced exactly

The repository pins:

```text
jsonschema==4.25.1
PyYAML==6.0.2
```

GitHub CI targets Python 3.11 and Python 3.12.

The ChatGPT container did not expose `python3.11` or `python3.12`. An attempt to create a clean venv and install the exact pinned dependencies failed because outbound package resolution was unavailable:

```text
Temporary failure in name resolution
ERROR: Could not find a version that satisfies the requirement jsonschema==4.25.1
```

The latter pip message is a consequence of the failed network/index lookup in this environment; it is **not evidence that jsonschema 4.25.1 does not exist**.

Therefore do not claim:

```text
exact GitHub Actions Python 3.11 reproduction   PASS
exact GitHub Actions Python 3.12 reproduction   PASS
exact pinned-dependency clean install           PASS
```

Those remain unverified locally.

## Hosted CI remains a separate observation

PR #5 currently reports one matrix workflow with:

```text
contracts (3.11)  failure
contracts (3.12)  cancelled
```

The jobs terminate in roughly two seconds. The current default GitHub MCP toolset exposes check-run state but not job-log contents, so the exact failing hosted step has not yet been observed.

Do not guess whether the failure is repository policy, runner/account state, checkout, setup-python, cache, dependency installation, or a project command.

## Required next capability

GitHub's official MCP server has a separate `actions` toolset. For a managed ChatGPT Developer MCP, a bounded remote endpoint can be created at:

```text
https://api.githubcopilot.com/mcp/x/actions
```

The `actions` toolset includes `actions_get`, with methods for workflow runs/jobs and workflow-run log URLs. Use this separate connector for diagnosis rather than expanding the main repository connector to all GitHub toolsets.

Once available, inspect the exact failed job ID before changing CI again.
