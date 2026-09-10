#!/usr/bin/env python3
"""Foreground process wrapper used by per-user macOS LaunchAgents."""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_config(path: str) -> dict:
    data = json.loads(Path(path).expanduser().read_text())
    if data.get("version") != 1:
        raise ValueError("service config version must be 1")
    return data


def wait_tailscale(binary: str, seconds: int = 120) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = subprocess.run([binary, "status"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return
        time.sleep(2)
    raise RuntimeError("Tailscale did not become ready")


def wait_port(host: str, port: int, seconds: int = 60) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(1)
    raise RuntimeError(f"service did not open {host}:{port}")


def serve(binary: str, https_port: int, backend_port: int) -> None:
    result = subprocess.run([binary, "serve", "--bg", f"--https={https_port}", str(backend_port)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "tailscale serve failed").strip())


def exec_python(repo: Path, script: str, args: list[str], env: dict) -> None:
    python_bin = sys.executable
    os.execve(python_bin, [python_bin, str(repo / "scripts" / script), *args], env)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("role", choices=["control", "remote-worker", "mesh-node"])
    p.add_argument("--config", required=True)
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    repo = Path(cfg["repo"]).expanduser().resolve()
    tailscale = cfg["tailscale_bin"]
    wait_tailscale(tailscale)
    env = os.environ.copy()

    if args.role == "control":
        env["COST_ROUTER_MESH_ALLOWED_USERS"] = cfg["allowed_users"]
        serve(tailscale, int(cfg["https_port"]), int(cfg["backend_port"]))
        exec_python(repo, "mesh_control_server.py",
                    ["--host", "127.0.0.1", "--port", str(cfg["backend_port"])], env)
    elif args.role == "remote-worker":
        env["COST_ROUTER_ALLOWED_TAILSCALE_USERS"] = cfg["allowed_users"]
        env["COST_ROUTER_REMOTE_WORKERS"] = cfg["workers"]
        env["COST_ROUTER_REMOTE_WORKSPACE_ROOT"] = str(Path.home() / "codex-remote-worker-tasks")
        serve(tailscale, int(cfg["https_port"]), int(cfg["backend_port"]))
        exec_python(repo, "remote_worker_server.py",
                    ["--host", "127.0.0.1", "--port", str(cfg["backend_port"]),
                     "--codex-bin", cfg["codex_bin"]], env)
    else:
        wait_port("127.0.0.1", 8787)
        env["COST_ROUTER_REMOTE_WORKERS"] = cfg["workers"]
        exec_python(repo, "mesh_node_agent.py",
                    ["--control-url", cfg["control_url"],
                     "--workers", cfg["workers"],
                     "--worker-port", str(cfg["worker_port"]),
                     "--interval", str(cfg["heartbeat_seconds"]),
                     "--codex-bin", cfg["codex_bin"]], env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
