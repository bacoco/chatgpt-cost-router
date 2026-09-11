"""Typed B lifecycle calls over the existing gateway's local/SSH transports.

Runtime locations are operator-installed alias bindings, never requester inputs.
The request is data for the fixed CLI, not source for an unrestricted interpreter.
"""
import json
import os
import subprocess
from pathlib import PurePosixPath
from operation_contracts.common import ContractError, canonical, fields, identifier, integer, loads
from .host_io import safe_environment

ACTIONS = {"process_submit":"submit","process_start":"start","process_status":"status",
           "process_cancel":"cancel","process_logs":"logs","process_result":"result",
           "process_events":"events","process_reconcile":"reconcile","process_profiles":"profiles",
           "node_health":"health", "process_artifact":"artifact"}


def call(runner, alias, action, args):
    if action not in ACTIONS:
        raise ContractError("unknown process lifecycle action")
    host = runner.host(alias)
    if host.transport == "ssh" and host.ssh_target.split("@",1)[0] == "root":
        raise ContractError("root SSH targets are not allowed")
    runtime = runner.runtime_bindings.get(alias)
    if not isinstance(runtime,dict):
        raise ContractError("node runtime is not enrolled for this alias")
    fields(runtime,("python","entrypoint","config"))
    for path in runtime.values():
        if not isinstance(path,str) or not PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
            raise ContractError("invalid installed runtime path")
    command = ACTIONS[action]
    argv = [runtime["python"],runtime["entrypoint"],"--config",runtime["config"],command]
    if command == "submit":
        fields(args,("request",),("start",))
        if type(args.get("start",False)) is not bool:
            raise ContractError("start must be boolean")
        argv += ["--request-json",canonical(args["request"])]
        if args.get("start"):
            argv.append("--start")
    elif command == "health":
        fields(args,())
    elif command == "profiles":
        fields(args,("project_id",))
        argv += ["--project",identifier(args["project_id"])]
    else:
        optional = ("stream","offset","limit") if command == "logs" else ("offset","limit") if command == "artifact" else ("after",) if command == "events" else ()
        required = ("project_id","run_id","name") if command == "artifact" else ("project_id","run_id")
        fields(args,required,optional)
        argv += ["--project",identifier(args["project_id"]),"--run",identifier(args["run_id"])]
        if command == "logs":
            stream = args.get("stream","stdout")
            if stream not in {"stdout","stderr"}:
                raise ContractError("invalid stream")
            argv += ["--stream",stream,"--offset",str(integer(args.get("offset",0),0,10**9)),
                     "--limit",str(integer(args.get("limit",32768),1,131072))]
        if command == "artifact":
            argv += ["--name",identifier(args["name"],"artifact"), "--offset",str(integer(args.get("offset",0),0,16*1024*1024)),
                     "--limit",str(integer(args.get("limit",65536),1,65536))]
        if command == "events":
            argv += ["--after",str(integer(args.get("after",0),0,10**12))]
    # B checks project grants again under its own configured principal.
    wire = argv if host.transport == "local" else runner._ssh_prefix(host)+[runner._remote_command(argv,None)]
    process = runner._run(wire,capture_output=True,text=True,timeout=60,check=False,env=safe_environment(os.environ))
    if process.returncode != 0:
        raise ContractError("node lifecycle call failed; inspect the private node service")
    try:
        value = loads(process.stdout)
        if not isinstance(value,dict):
            raise ContractError("node lifecycle response must be an object")
    except (ValueError,TypeError) as exc:
        raise ContractError("invalid node lifecycle response") from exc
    return value
