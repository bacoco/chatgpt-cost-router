#!/usr/bin/env python3
"""Install/status/remove per-user LaunchAgents for the private worker mesh."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fleet_operator.workers.macos_launchd import LABELS, LaunchdError, install_control, install_worker_node, remove


def status(home: Path) -> dict:
    result = {}
    uid = os.getuid()
    for role, label in LABELS.items():
        plist = home / "Library/LaunchAgents" / f"{label}.plist"
        check = subprocess.run(["launchctl", "print", f"gui/{uid}/{label}"],
                               capture_output=True, text=True)
        result[role] = {"installed": plist.exists(), "loaded": check.returncode == 0}
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description="Manage ChatGPT Cost Router mesh LaunchAgents")
    p.add_argument("--repo", default=str(ROOT))
    p.add_argument("--home", default=str(Path.home()), help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("install-control")
    c.add_argument("--allowed-users", required=True)
    n = sub.add_parser("install-worker-node")
    n.add_argument("--control-url", required=True)
    n.add_argument("--allowed-users", required=True)
    n.add_argument("--workers", default="openai-B")
    sub.add_parser("status")
    u = sub.add_parser("uninstall")
    u.add_argument("role", choices=["control", "worker-node"])
    args = p.parse_args(argv)
    home = Path(args.home).expanduser().resolve()
    try:
        if args.command == "install-control":
            files = install_control(repo=Path(args.repo), home=home,
                                    allowed_users=args.allowed_users, dry_run=args.dry_run)
            payload = {"installed": "control", "files": [str(x) for x in files]}
        elif args.command == "install-worker-node":
            files = install_worker_node(repo=Path(args.repo), home=home,
                control_url=args.control_url, allowed_users=args.allowed_users,
                workers=args.workers, dry_run=args.dry_run)
            payload = {"installed": "worker-node", "files": [str(x) for x in files]}
        elif args.command == "status":
            payload = status(home)
        else:
            files = remove(args.role, home=home, dry_run=args.dry_run)
            payload = {"uninstalled": args.role, "files": [str(x) for x in files]}
        print(json.dumps(payload, indent=2))
        return 0
    except (LaunchdError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
