"""One supervisor for one owned child. No arbitrary restored PID is ever signalled."""
import argparse
import subprocess
import time
from operation_contracts.common import ContractError, digest
from operation_contracts.files import atomic_json
from .config import NodeConfig
from .service import Jobs
from .workspace import prepare, root_for, artifacts
from .command import command
from .monitor import monitor, signal_child
import signal


def execute(config, project, id_, token):
    service = Jobs(config)
    row = service.row(project,id_)
    if row["state"] not in {"RUNNING","CANCELLING"} or row["data"].get("token") != token:
        return 0
    if row["policy"] != config.revision:
        service.journal.transition(id_,{"RUNNING","CANCELLING"},"BLOCKED",{"reason":"policy changed before spawn"},token=token)
        return 0
    if row["state"] == "CANCELLING":
        service.journal.transition(id_,{"CANCELLING"},"CANCELLED",{},token=token)
        return 0
    process = None
    try:
        profile = config.profile(row["request"]["profile"])
        root, work, home = prepare(config,row)
        current = service.row(project,id_)
        if current["state"] == "CANCELLING":
            state = {"state":"CANCELLED","exit_code":None,"reason":"cancelled before child start"}
        elif current["state"] != "RUNNING" or row["request"]["deadline"] <= time.time():
            state = {"state":"TIMED_OUT","exit_code":None,"reason":"deadline before child start"}
        else:
            argv, env = command(profile,root,work,home,id_)
            process = subprocess.Popen(argv,cwd=work,env=env,stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,close_fds=True)
            service.journal.transition(id_,{"RUNNING"},"RUNNING",{"child_started":time.time()},token=token)
            state = monitor(process,service.journal,row,token,root,profile)
        state["artifacts"] = artifacts(profile,work)
        receipt = {"version":1,"run_id":id_,"request_digest":row["digest"],"policy":row["policy"],"token":token,
                   "source":row["request"].get("source"),"runtime_revision":config.document.get("runtime_revision","unversioned"),
                   "finished":time.time(),**state}
        atomic_json(root / "result.json",receipt)
        service.journal.transition(id_,{"RUNNING","CANCELLING"},state["state"],{**state,"receipt_digest":digest(receipt)},token=token)
    except Exception as exc:
        service.journal.transition(id_,{"RUNNING","CANCELLING"},"FAILED",{"reason":type(exc).__name__},token=token)
    finally:
        if process is not None and process.poll() is None:
            signal_child(process, signal.SIGKILL)
            process.wait(timeout=5)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ("config","project","run","token"):
        parser.add_argument("--"+name,required=True)
    args = parser.parse_args(argv)
    return execute(NodeConfig.from_file(args.config),args.project,args.run,args.token)
