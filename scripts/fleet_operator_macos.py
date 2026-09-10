#!/usr/bin/env python3
"""Initialize, install and inspect Fleet Operator on macOS."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fleet_operator.macos import (
    InstallError, init_fleet_config, install_relay, install_server, install_tunnel,
    launchd_status, port_open,
)

DEFAULT_CONFIG = "~/.config/chatgpt-cost-router/fleet-operator.json"


def add_host_args(parser):
    parser.add_argument("--local-host", nargs=2, metavar=("ALIAS", "ALLOWED_ROOT"))
    parser.add_argument("--ssh-host", nargs=3, action="append", default=[], metavar=("ALIAS", "USER@HOST", "ALLOWED_ROOT"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Manage Fleet Operator macOS services")
    p.add_argument("--repo", default=str(ROOT))
    p.add_argument("--home", default=str(Path.home()), help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init-config")
    i.add_argument("--config", default=DEFAULT_CONFIG)
    add_host_args(i)

    s = sub.add_parser("install-server")
    s.add_argument("--config", default=DEFAULT_CONFIG)
    s.add_argument("--port", type=int, default=8810)
    s.add_argument("--skip-deps", action="store_true")

    r = sub.add_parser("install-relay")
    r.add_argument("--config", default=DEFAULT_CONFIG)
    r.add_argument("--command-branch", default="fleet/commands")
    r.add_argument("--poll-seconds", type=int, default=30)

    b = sub.add_parser("bootstrap")
    b.add_argument("--config", default=DEFAULT_CONFIG)
    b.add_argument("--command-branch", default="fleet/commands")
    b.add_argument("--poll-seconds", type=int, default=30)
    b.add_argument("--port", type=int, default=8810)
    b.add_argument("--skip-mcp-server", action="store_true")
    add_host_args(b)

    t = sub.add_parser("install-tunnel")
    t.add_argument("--tunnel-id", required=True)
    t.add_argument("--runtime-key-file", required=True)
    t.add_argument("--mcp-port", type=int, default=8810)
    t.add_argument("--health-port", type=int, default=8811)

    sub.add_parser("status")
    args = p.parse_args(argv)
    home = Path(args.home).expanduser().resolve()
    try:
        if args.command == "init-config":
            path = init_fleet_config(path=Path(args.config), local_host=tuple(args.local_host) if args.local_host else None, ssh_hosts=[tuple(x) for x in args.ssh_host])
            payload = {"initialized": str(path)}
        elif args.command == "install-server":
            files = install_server(repo=Path(args.repo), home=home, config=Path(args.config), port=args.port, install_dependencies=not args.skip_deps, dry_run=args.dry_run)
            payload = {"installed": "fleet-operator", "files": [str(x) for x in files]}
        elif args.command == "install-relay":
            files = install_relay(repo=Path(args.repo), home=home, fleet_config=Path(args.config), command_branch=args.command_branch, poll_seconds=args.poll_seconds, dry_run=args.dry_run)
            payload = {"installed": "fleet-relay", "files": [str(x) for x in files]}
        elif args.command == "bootstrap":
            config = init_fleet_config(path=Path(args.config), local_host=tuple(args.local_host) if args.local_host else None, ssh_hosts=[tuple(x) for x in args.ssh_host])
            relay_files = install_relay(repo=Path(args.repo), home=home, fleet_config=config, command_branch=args.command_branch, poll_seconds=args.poll_seconds, dry_run=args.dry_run)
            server_files = []
            if not args.skip_mcp_server:
                server_files = install_server(repo=Path(args.repo), home=home, config=config, port=args.port, dry_run=args.dry_run)
            payload = {"bootstrapped": True, "config": str(config), "relay_files": [str(x) for x in relay_files], "server_files": [str(x) for x in server_files]}
        elif args.command == "install-tunnel":
            files = install_tunnel(home=home, tunnel_id=args.tunnel_id, key_file=Path(args.runtime_key_file), mcp_port=args.mcp_port, health_port=args.health_port, dry_run=args.dry_run)
            payload = {"installed": "secure-mcp-tunnel", "files": [str(x) for x in files]}
        else:
            payload = launchd_status(home)
            payload["mcp_port_8810_open"] = port_open(8810)
            payload["tunnel_health_port_8811_open"] = port_open(8811)
        print(json.dumps(payload, indent=2))
        return 0
    except (InstallError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
