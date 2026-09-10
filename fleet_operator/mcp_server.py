"""MCP surface for the Fleet Operator SSH gateway.

Run this only on loopback and place OpenAI Secure MCP Tunnel in front of it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .core import FleetConfig, FleetError, FleetRunner

DEFAULT_CONFIG = "~/.config/chatgpt-cost-router/fleet-operator.json"


def build_server(config_path: str | None = None) -> MCPServer:
    config_path = config_path or os.environ.get("FLEET_OPERATOR_CONFIG", DEFAULT_CONFIG)
    mcp = MCPServer(
        "Fleet Operator",
        instructions=(
            "Private SSH fleet gateway. Always address hosts by configured alias, never by a raw "
            "network destination. Prefer read-only tools for inspection. Use write tools only when "
            "the requested task requires a remote state change. Destructive commands additionally "
            "require allow_destructive=true and root/admin commands are blocked server-side."
        ),
    )

    def runner() -> FleetRunner:
        return FleetRunner(FleetConfig.load(config_path))

    @mcp.tool(title="List fleet hosts", description="List configured host aliases and their non-secret execution policy. Never returns SSH targets or credentials.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_list_hosts() -> list[dict]:
        return runner().inventory()

    @mcp.tool(title="Check one host", description="Run a bounded read-only uname probe on a configured host alias over SSH.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_host_status(host: str) -> dict:
        return runner().host_status(host)

    @mcp.tool(title="Read remote file", description="Read the beginning of a remote text file only when its path is under a locally configured allowed root.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_read_file(host: str, path: str, max_bytes: int = 131072) -> dict:
        return runner().read_file(host, path, max_bytes=max_bytes)

    @mcp.tool(title="Run read-only remote command", description="Execute argv without shell interpolation on one host. The executable must be in that host's local read allow-list.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_exec_read(host: str, argv: list[str], cwd: str | None = None, timeout_seconds: int | None = None) -> dict:
        return runner().execute(host, argv, cwd=cwd, timeout_seconds=timeout_seconds, mode="read").as_dict()

    @mcp.tool(title="Run remote command", description="Execute allowlisted argv on one host over SSH. This can modify the host. Root/admin commands are blocked. Commands classified as destructive require allow_destructive=true.", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=False, open_world_hint=False))
    def fleet_exec_write(host: str, argv: list[str], cwd: str | None = None, timeout_seconds: int | None = None, allow_destructive: bool = False) -> dict:
        return runner().execute(host, argv, cwd=cwd, timeout_seconds=timeout_seconds, mode="write", allow_destructive=allow_destructive).as_dict()

    @mcp.tool(title="Run read-only command on several hosts", description="Fan one read-allowlisted argv command out concurrently to configured host aliases.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_exec_many_read(hosts: list[str], argv: list[str], timeout_seconds: int | None = None, max_parallel: int = 8) -> list[dict]:
        return runner().execute_many(hosts, argv, timeout_seconds=timeout_seconds, mode="read", max_parallel=max_parallel)

    @mcp.tool(title="Run command on several hosts", description="Fan one allowlisted command out concurrently to several hosts. This can modify remote hosts; destructive commands require allow_destructive=true.", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=False, open_world_hint=False))
    def fleet_exec_many_write(hosts: list[str], argv: list[str], timeout_seconds: int | None = None, allow_destructive: bool = False, max_parallel: int = 8) -> list[dict]:
        return runner().execute_many(hosts, argv, timeout_seconds=timeout_seconds, mode="write", allow_destructive=allow_destructive, max_parallel=max_parallel)

    @mcp.tool(title="Read Fleet Relay result", description="Read one already-produced local relay result by job id. This never executes a command.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_relay_result(job_id: str) -> dict:
        from .relay import JOB_RE
        if not JOB_RE.fullmatch(job_id):
            raise FleetError("invalid job id")
        state = Path(os.environ.get("FLEET_RELAY_STATE_DIR", "~/.local/state/chatgpt-cost-router/fleet-relay")).expanduser()
        path = state / "results" / f"{job_id}.json"
        if not path.is_file():
            raise FleetError(f"relay result not found: {job_id}")
        return json.loads(path.read_text())

    @mcp.tool(title="Git status on remote repository", description="Run git status --short --branch in an allowed repository path on one host.", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    def fleet_git_status(host: str, repo_path: str) -> dict:
        return runner().execute(host, ["git", "status", "--short", "--branch"], cwd=repo_path, mode="read", timeout_seconds=30).as_dict()

    @mcp.tool(title="Fast-forward remote repository", description="Run git pull --ff-only in an allowed repository path on one host.", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True))
    def fleet_git_pull(host: str, repo_path: str) -> dict:
        return runner().execute(host, ["git", "pull", "--ff-only"], cwd=repo_path, mode="write", timeout_seconds=120).as_dict()

    return mcp


def main() -> None:
    host = os.environ.get("FLEET_OPERATOR_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise SystemExit("Fleet Operator must bind to loopback; use OpenAI Secure MCP Tunnel in front")
    port = int(os.environ.get("FLEET_OPERATOR_PORT", "8810"))
    build_server().run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
