"""Explicit local operator commands. Plans and service rendering do not deploy."""
import argparse
import json
import os
import sys
from pathlib import Path
from operation_contracts.common import ContractError, load
from operation_contracts.files import atomic_json
from . import bindings, releases, services


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fleet Operator enrollment and versioned releases")
    sub = parser.add_subparsers(dest="command", required=True)
    stage = sub.add_parser("stage")
    for name in ("repo", "root", "revision"):
        stage.add_argument("--"+name, required=True)
    sub.add_parser("verify").add_argument("--release", required=True)
    activate = sub.add_parser("activate")
    for name in ("root", "revision", "node-config", "python"):
        activate.add_argument("--"+name, required=True)
    activate.add_argument("--apply", action="store_true")
    enroll = sub.add_parser("plan-enrollment")
    for name in ("gateway", "host", "release", "node-config", "python", "output"):
        enroll.add_argument("--"+name, required=True)
    apply = sub.add_parser("apply-enrollment")
    apply.add_argument("--plan", required=True)
    service = sub.add_parser("render-service")
    for name in ("active", "python", "bootstrap", "label", "log-dir", "output"):
        service.add_argument("--"+name, required=True)
    service.add_argument("--platform", choices=("launchd", "systemd"), required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "stage":
            out = releases.stage(args.repo, args.root, args.revision)
        elif args.command == "verify":
            out = releases.verify(args.release)
        elif args.command == "activate":
            out = releases.activation(args.root,args.revision,args.node_config,args.python,apply=args.apply)
        elif args.command == "plan-enrollment":
            out = bindings.plan(args.gateway,args.host,args.release,args.node_config,args.python)
            atomic_json(args.output,out)
        elif args.command == "apply-enrollment":
            out = bindings.apply(load(args.plan))
        else:
            command = [args.python, str(Path(args.bootstrap).resolve()), "--config", str(Path(args.active).resolve()), "serve-queue"]
            text = services.render(command,args.label,platform=args.platform,log_dir=args.log_dir)
            out = services.write_definition(args.output,text)
        print(json.dumps(out,indent=2))
        return 0
    except (ContractError,OSError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        return 2


def active_main(argv=None):
    parser = argparse.ArgumentParser(description="Verified active Fleet Jobs runtime")
    parser.add_argument("--config",required=True,help="local active.json activation record")
    parser.add_argument("arguments",nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        command = releases.prepare_active(args.config)+args.arguments
        from ..host_io import safe_environment
        environment = {**safe_environment(os.environ),"PYTHONDONTWRITEBYTECODE":"1"}
        os.execve(command[0],command,environment)
    except (ContractError,OSError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
