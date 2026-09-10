# T35B — Fleet Operator live autonomous control — 2026-09-10

Status: `PASS` for the GitHub-relay no-copy/paste control path.

## Scope

Validate that ChatGPT can create bounded machine jobs in GitHub, have the supervised Fleet Operator execute them on configured hosts, and read machine-produced result branches back without asking the user to run terminal commands.

## Live evidence

1. The initial bootstrap installed the relay LaunchAgent before the optional MCP-server dependency step failed on the system Xcode Python 3.9.6.
2. ChatGPT independently read `fleet/results/job-t35-live-20260910-2120` and verified a real `status` execution on alias `macbook` returned `PASS`.
3. ChatGPT then created `job-fleet-macstudio-status-20260910-2125`; the relay executed it on alias `macstudio` and returned `PASS`, proving the remote SSH/Tailscale path.
4. ChatGPT created a Python-runtime inspection job and verified the gateway's default `python3` was 3.9.6.
5. ChatGPT used an absolute Homebrew command probe and verified Python 3.11.14 was installed.
6. Commit `14ea8c5bc0e0d39d7b04577dec7994e3939471fd` changed Fleet Operator macOS packaging to select Python >=3.10 automatically.
7. ChatGPT created a relay `git_pull` job; the gateway pulled that fix successfully.
8. ChatGPT created a Fleet Operator regression-test job. Result: 23 tests PASS in 0.092 s.
9. ChatGPT created an `exec_write` job to install the MCP server. `mcp==2.2.0` installed successfully into the Python 3.11 virtualenv and the LaunchAgent installation returned exit 0.
10. ChatGPT created a final status job. It returned:
    - Fleet Operator server: installed=true, loaded=true
    - Fleet relay: installed=true, loaded=true
    - MCP loopback port 8810: open
    - Secure MCP Tunnel: not installed

## Boundary

This proves autonomous bounded machine control through the GitHub relay for the gateway MacBook and one remote Mac Studio, with results read back by ChatGPT. It does not yet prove a direct ChatGPT custom-MCP invocation. Secure MCP Tunnel / custom-app attachment remains a distinct pending step and full MCP write support depends on the ChatGPT plan/workspace.

No paid OpenAI API or model call was used by these Fleet Operator control-path tests.
