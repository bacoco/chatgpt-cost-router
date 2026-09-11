"""One supervisor for one owned child. No arbitrary restored PID is ever signalled."""
import argparse
import subprocess
import time
import signal
from operation_contracts.locking import file_lock
from .artifact_store import capture
from .containers import cleanup
from operation_contracts.common import ContractError, digest
from operation_contracts.files import atomic_json
from .config import NodeConfig
from .service import Jobs
from .workspace import prepare, root_for, artifacts
from .command import command
from .monitor import monitor


def _execute(config, project, id_, token):
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
    root = root_for(config, id_)
    if root.exists():
        service.journal.transition(id_, {"RUNNING", "CANCELLING"}, "UNCERTAIN",
                                   {"reason": "previous supervisor created this workspace; no replay"}, token=token)
        try:
            service.reconcile(project, id_)
        except (ContractError, OSError, ValueError):
            pass
        return 0
    process = None
    profile = config.profile(row["request"]["profile"])
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
        if not cleanup(profile, id_):
            state = {**state, "state": "UNCERTAIN", "reason": "container stop could not be verified"}
        state["artifacts"] = capture(profile, work, root)
        state["artifact_store"] = "artifacts"
        receipt = {"version":1,"run_id":id_,"request_digest":row["digest"],"policy":row["policy"],"token":token,
                   "source":row["request"].get("source"),"runtime_revision":config.document.get("runtime_revision","unversioned"),
                   "finished":time.time(),**state}
        atomic_json(root / "result.json",receipt)
        service.journal.transition(id_,{"RUNNING","CANCELLING"},state["state"],{**state,"receipt_digest":digest(receipt)},token=token)
    except Exception as exc:
        if process is not None and process.returncode is None:
            from .monitor import signal_child
            signal_child(process, signal.SIGKILL)
            process.wait(timeout=5)
        stopped = cleanup(profile, id_)
        state = "UNCERTAIN" if process is not None or not stopped else "FAILED"
        service.journal.transition(id_, {"RUNNING", "CANCELLING"}, state, {"reason":type(exc).__name__}, token=token)
    return 0


def execute(config, project, id_, token):
    service = Jobs(config)
    row = service.row(project, id_)
    try:
        with file_lock(config.state_dir / "worker-locks" / (row["id"] + ".lock"), blocking=False):
            return _execute(config, project, id_, token)
    except ContractError as exc:
        if str(exc) == "operation is already owned":
            return 0
        raise


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ("config","project","run","token"):
        parser.add_argument("--"+name,required=True)
    args = parser.parse_args(argv)
    return execute(NodeConfig.from_file(args.config),args.project,args.run,args.token)
