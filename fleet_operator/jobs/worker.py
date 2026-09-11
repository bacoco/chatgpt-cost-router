"""One supervisor for one owned child. No arbitrary restored PID is ever signalled."""
import argparse
import os
import signal
import subprocess
import time
from operation_contracts.common import ContractError, digest
from operation_contracts.files import atomic_json
from .config import NodeConfig
from .service import Jobs
from .workspace import prepare, root_for, artifacts
from .command import command
from .monitor import monitor, signal_child


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
    # One durable claim per supervisor. A restarted worker must reconcile, not spawn again.
    with service.journal.transaction() as db:
        claimed = service.journal.decode(db.execute("SELECT * FROM operations WHERE id=?", (id_,)).fetchone())
        if claimed["state"] not in {"RUNNING", "CANCELLING"} or claimed["data"].get("token") != token:
            return 0
        if claimed["data"].get("supervisor_claimed"):
            return 0
        from operation_contracts.common import canonical
        claimed["data"]["supervisor_claimed"] = time.time()
        db.execute("UPDATE operations SET data=? WHERE id=?", (canonical(claimed["data"]), id_))
    previous_umask = os.umask(0o077)
    process = None
    cleanup_complete = False
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
        if process is not None and profile["isolation"] == "container":
            from .command import cleanup_container
            state.update(cleanup_container(profile, root))
            cleanup_complete = True
        state["artifacts"] = artifacts(profile,work)
        receipt = {"version":1,"run_id":id_,"request_digest":row["digest"],"policy":row["policy"],"token":token,
                   "source":row["request"].get("source"),"runtime_revision":config.document.get("runtime_revision","unversioned"),
                   "finished":time.time(),**state}
        atomic_json(root / "result.json",receipt)
        service.journal.transition(id_,{"RUNNING","CANCELLING"},state["state"],{**state,"receipt_digest":digest(receipt)},token=token)
    except Exception as exc:
        service.journal.transition(id_,{"RUNNING","CANCELLING"},"UNCERTAIN" if process is not None else "FAILED",{"reason":type(exc).__name__},token=token)
    finally:
        os.umask(previous_umask)
        if process is not None and process.returncode is None:
            signal_child(process, signal.SIGKILL)
            process.wait(timeout=5)
        if process is not None and profile["isolation"] == "container" and not cleanup_complete:
            from .command import cleanup_container
            try:
                cleanup_container(profile, root)
            except Exception:
                pass  # The durable outcome is already UNCERTAIN; never report verified cleanup.
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ("config","project","run","token"):
        parser.add_argument("--"+name,required=True)
    args = parser.parse_args(argv)
    return execute(NodeConfig.from_file(args.config),args.project,args.run,args.token)
