"""A command interface: explicitly invoke native tools or configured MCP adapters."""
import argparse
import json
import sys
from operation_contracts.common import ContractError, load
from .config import configured


def main(argv=None):
    parser = argparse.ArgumentParser(description="Chat-first Operations — all authorized connector families")
    parser.add_argument("--config",required=True)
    sub = parser.add_subparsers(dest="command",required=True)
    sub.add_parser("projects")
    sub.add_parser("catalog")
    submit = sub.add_parser("submit")
    submit.add_argument("--workflow",required=True)
    observe = sub.add_parser("observe")
    for name in ("project","resource","action","evidence"):
        observe.add_argument("--"+name,required=True)
    for name in ("next","status","result","run","approve","record","reconcile"):
        action = sub.add_parser(name)
        action.add_argument("--project",required=True)
        action.add_argument("--run",required=True)
        if name in {"approve","record","reconcile"}:
            action.add_argument("--step",required=True)
        if name == "record":
            action.add_argument("--token",required=True)
            action.add_argument("--result",required=True)
            action.add_argument("--error",action="store_true")
    args = parser.parse_args(argv)
    try:
        engine, config = configured(args.config)
        if args.command == "projects":
            out = {"projects":engine.projects.list(engine.principal)}
        elif args.command == "catalog":
            out = {"actions":engine.catalog.list()}
        elif args.command == "submit":
            out = engine.submit(load(args.workflow))
        elif args.command == "observe":
            engine.projects.project(engine.principal,args.project)
            engine.capabilities.observe(engine.principal,args.project,args.resource,args.action,
                                        engine.surface,engine.session,load(args.evidence))
            out = {"recorded":True,"scope":"principal/project/resource/action/surface/session"}
        elif args.command == "record":
            out = engine.record(args.project,args.run,args.step,args.token,load(args.result),error=args.error)
        elif args.command in {"approve","reconcile"}:
            out = getattr(engine,args.command)(args.project,args.run,args.step)
        elif args.command == "result":
            out = {**engine.status(args.project,args.run),"outputs":engine.outputs(engine.row(args.project,args.run))}
        elif args.command == "run":
            from .mcp_transport import MCPTransport
            out = engine.run(args.project,args.run,MCPTransport(config.get("mcp_endpoints",{})))
        else:
            out = getattr(engine,args.command)(args.project,args.run)
        print(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False))
        return 0
    except (ContractError,OSError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        return 2
