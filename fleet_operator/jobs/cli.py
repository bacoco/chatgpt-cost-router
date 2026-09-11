"""Independent B terminal interface: ordinary jobs without Chat or a model."""
import argparse
import json
import sys
import time
from operation_contracts.common import ContractError, load, loads
from .config import NodeConfig
from .service import Jobs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fleet Operator process runtime")
    parser.add_argument("--config",required=True)
    sub = parser.add_subparsers(dest="command",required=True)
    submit = sub.add_parser("submit")
    request = submit.add_mutually_exclusive_group(required=True)
    request.add_argument("--request")
    request.add_argument("--request-json")
    submit.add_argument("--start",action="store_true")
    for name in ("start","status","cancel","result","reconcile","logs","events","artifact"):
        action = sub.add_parser(name)
        action.add_argument("--project",required=True)
        action.add_argument("--run",required=True)
        if name == "logs":
            action.add_argument("--stream",choices=("stdout","stderr"),default="stdout")
            action.add_argument("--offset",type=int,default=0)
            action.add_argument("--limit",type=int,default=32768)
        if name == "artifact":
            action.add_argument("--name",required=True)
            action.add_argument("--offset",type=int,default=0)
            action.add_argument("--limit",type=int,default=65536)
        if name == "events":
            action.add_argument("--after",type=int,default=0)
    for name in ("profiles","list"):
        sub.add_parser(name).add_argument("--project",required=True)
    sub.add_parser("health")
    queue = sub.add_parser("serve-queue")
    queue.add_argument("--once",action="store_true")
    args = parser.parse_args(argv)
    try:
        config = NodeConfig.from_file(args.config)
        service = Jobs(config)
        if args.command == "submit":
            req = load(args.request) if args.request else loads(args.request_json)
            output = service.submit(req)
            if args.start:
                output = service.start(req["project_id"],output["run_id"])
        elif args.command == "health":
            output = service.health()
        elif args.command == "serve-queue":
            while True:
                service.recover_stale()
                service.start_pending()
                if args.once:
                    break
                time.sleep(1)
            output = {"ok":True}
        elif args.command == "profiles":
            output = {"profiles":service.profiles(args.project)}
        elif args.command == "list":
            config.projects.project(config.principal,args.project)
            output = {"jobs":[service.status(args.project,row["id"]) for row in service.journal.list(config.principal,args.project,"process")]}
        elif args.command == "events":
            service.row(args.project,args.run)
            output = {"events":service.journal.events(config.principal,args.project,args.run,args.after)}
        elif args.command == "artifact":
            output = service.artifact(args.project,args.run,args.name,args.offset,args.limit)
        elif args.command == "logs":
            output = service.logs(args.project,args.run,args.stream,args.offset,args.limit)
        else:
            output = getattr(service,args.command)(args.project,args.run)
        output["_node"] = {"node_id":config.node_id,"runtime_revision":config.document.get("runtime_revision"),
                           "policy_revision":config.revision}
        print(json.dumps(output,indent=2,ensure_ascii=False,allow_nan=False))
        return 0
    except (ContractError,OSError,ValueError) as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        return 2
