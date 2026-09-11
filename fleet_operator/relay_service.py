"""Safe canonical relay: durable claim, outbox retry, no side-effect replay."""
import json
import time
from pathlib import Path
from operation_contracts.common import ContractError, fields, number
from .relay import RelayConfig, RelayError, Ledger, JOB_RE
from .outbox import Outbox, relay_lock
from .relay_bus import ReliableBus
from .secure_gateway import configured_runner
from .remote_jobs import ACTIONS as PROCESS_ACTIONS, call as process_call

ACTIONS = frozenset({"status","exec_read","exec_write","read_file","git_pull"}) | (PROCESS_ACTIONS.keys() - {"process_artifact"})


def validate_job(payload, *, path, now=None):
    fields(payload,("version","job_id","host","action","expires_at_unix"),("args",))
    if type(payload["version"]) is not int or payload["version"] != 1:
        raise RelayError("invalid job version")
    job = payload["job_id"]
    if not isinstance(job,str) or not JOB_RE.fullmatch(job) or path != f".fleet/jobs/{job}.json":
        raise RelayError("job id must match its filename")
    if payload["action"] not in ACTIONS or not isinstance(payload["host"],str) or not payload["host"]:
        raise RelayError("invalid action or host")
    if not isinstance(payload.get("args",{}),dict):
        raise RelayError("invalid job args")
    now = time.time() if now is None else now
    number(payload["expires_at_unix"],now,now+86400,"job expiry")
    return {**payload,"args":payload.get("args",{})}


def execute_job(runner, job):
    host, action, args = job["host"], job["action"], job["args"]
    if action == "process_artifact":
        raise RelayError("artifact bytes require the private node/CLI/MCP transport")
    if action in PROCESS_ACTIONS:
        return process_call(runner,host,action,args)
    if action == "status":
        fields(args,())
        return runner.host_status(host)
    if action == "read_file":
        fields(args,("path",),("max_bytes",))
        return runner.read_file(host,args["path"],max_bytes=args.get("max_bytes",131072))
    if action == "git_pull":
        fields(args,("repo_path",))
        return runner.execute(host,["git","pull","--ff-only"],cwd=args["repo_path"],mode="write",timeout_seconds=120).as_dict()
    fields(args,("argv",),("cwd","timeout_seconds","allow_destructive"))
    if args.get("allow_destructive"):
        raise RelayError("destructive raw commands are unavailable; cancel an owned process instead")
    return runner.execute(host,args["argv"],cwd=args.get("cwd"),timeout_seconds=args.get("timeout_seconds"),
                          mode="read" if action == "exec_read" else "write").as_dict()


def run_once(config, *, bus=None, clock=time.time):
    bus = bus or ReliableBus(config)
    events = []
    with relay_lock(config.state_dir):
        ledger = Ledger(config.state_dir / "ledger.json")
        outbox = Outbox(config.state_dir)
        runner = configured_runner(config.fleet_config)
        bus.fetch()
        for path in bus.list_jobs():
            job_id = Path(path).stem
            if not JOB_RE.fullmatch(job_id):
                continue
            raw, sha = bus.read_job(path)
            seen = outbox.get(job_id)
            if seen and seen["digest"] != sha:
                events.append({"job_id":job_id,"status":"REJECTED","error":"conflicting job identity"})
                continue
            if seen and seen["state"] == "PUBLISHED":
                continue
            if not seen and ledger.seen(job_id):
                # Migration: historical published commands are never executed again.
                if ledger.seen(job_id) != sha:
                    events.append({"job_id":job_id,"status":"REJECTED","error":"conflicting historical job identity"})
                continue
            if seen:
                payload = seen["result"] or outbox.uncertain(job_id,sha)
            else:
                outbox.claim(job_id,sha)
                started = clock()
                try:
                    job = validate_job(raw,path=path,now=started)
                    result = execute_job(runner,job)
                    state = result.get("state")
                    status = ("ACCEPTED" if state in {"QUEUED","RUNNING","CANCELLING"} else
                              "PASS" if state == "SUCCEEDED" else state) if state else (
                              "PASS" if not result.get("timed_out") and result.get("exit_code",0) == 0 else "FAILED")
                    payload = {"version":1,"job_id":job_id,"job_sha256":sha,"host":job["host"],"action":job["action"],
                               "started_at_unix":started,"finished_at_unix":clock(),"status":status,"result":result}
                except Exception as exc:
                    payload = {"version":1,"job_id":job_id,"job_sha256":sha,"started_at_unix":started,
                               "finished_at_unix":clock(),"status":"ERROR","error":str(exc)}
                outbox.save(job_id,sha,payload)
            try:
                branch = bus.push_result(job_id,payload)
                outbox.published(job_id,sha)
                ledger.mark(job_id,sha)
                events.append({**payload,"result_branch":branch})
            except Exception as exc:
                events.append({**payload,"result_push_error":str(exc)})
    return events


def run_forever(config):
    while True:
        try:
            for result in run_once(config):
                print(json.dumps(result,sort_keys=True),flush=True)
        except Exception as exc:
            print(json.dumps({"relay_error":str(exc)}),flush=True)
        time.sleep(config.poll_seconds)
