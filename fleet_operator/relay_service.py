"""Canonical relay: durable claim, independent outbox retry, no effect replay."""
import json
import time
from pathlib import Path
from operation_contracts.common import ContractError, fields, number
from .relay import RelayConfig, RelayError, Ledger, JOB_RE
from .outbox import Outbox, relay_lock
from .relay_bus import ReliableBus
from .secure_gateway import configured_runner
from .remote_jobs import ACTIONS as PROCESS_ACTIONS, call as process_call

ACTIONS = frozenset({"status", "exec_read", "exec_write", "read_file", "git_pull"}) | PROCESS_ACTIONS.keys()


def validate_job(payload, *, path, now=None):
    try:
        fields(payload, ("version", "job_id", "host", "action", "expires_at_unix"), ("args",))
        if type(payload["version"]) is not int or payload["version"] != 1:
            raise RelayError("invalid job version")
        job = payload["job_id"]
        if not isinstance(job, str) or not JOB_RE.fullmatch(job) or path != f".fleet/jobs/{job}.json":
            raise RelayError("job id must match its filename")
        if not isinstance(payload["action"], str) or payload["action"] not in ACTIONS:
            raise RelayError("unknown relay action")
        if not isinstance(payload["host"], str) or not payload["host"]:
            raise RelayError("invalid host")
        if not isinstance(payload.get("args", {}), dict):
            raise RelayError("invalid job args")
        now = time.time() if now is None else now
        number(payload["expires_at_unix"], now, now + 86400, "job expiry")
        return {**payload, "args": payload.get("args", {})}
    except ContractError as exc:
        raise RelayError(str(exc)) from exc


def execute_job(runner, job):
    host, action, args = job["host"], job["action"], job.get("args", {})
    if action in PROCESS_ACTIONS:
        return process_call(runner, host, action, args)
    if action == "status":
        fields(args, ())
        return runner.host_status(host)
    if action == "read_file":
        fields(args, ("path",), ("max_bytes",))
        return runner.read_file(host, args["path"], max_bytes=args.get("max_bytes", 131072))
    if action == "git_pull":
        fields(args, ("repo_path",))
        return runner.execute(host, ["git", "pull", "--ff-only"], cwd=args["repo_path"], mode="write", timeout_seconds=120).as_dict()
    fields(args, ("argv",), ("cwd", "timeout_seconds", "allow_destructive"))
    if args.get("allow_destructive"):
        raise RelayError("destructive raw commands are unavailable; cancel an owned process instead")
    return runner.execute(host, args["argv"], cwd=args.get("cwd"), timeout_seconds=args.get("timeout_seconds"),
                          mode="read" if action == "exec_read" else "write").as_dict()


def receipt_status(result):
    state = result.get("state")
    if state in {"QUEUED", "RUNNING", "CANCELLING"}:
        return "ACCEPTED"
    if state in {"FAILED", "CANCELLED", "TIMED_OUT", "BLOCKED", "UNCERTAIN"}:
        return state
    return "PASS" if not result.get("timed_out") and result.get("exit_code", 0) in (0, None) else "FAILED"


def _publish(bus, ledger, outbox, job, sha, payload):
    try:
        branch = bus.push_result(job, payload)
        outbox.published(job, sha)
        ledger.mark(job, sha)
        return {**payload, "result_branch": branch}
    except Exception as exc:
        return {**payload, "result_push_error": type(exc).__name__}


def run_once(config, *, bus=None, clock=time.time):
    bus = bus or ReliableBus(config)
    events, attempted = [], set()
    with relay_lock(config.state_dir):
        ledger, outbox = Ledger(config.state_dir / "ledger.json"), Outbox(config.state_dir)
        # Delivery must not depend on the command still existing or on node readiness.
        for old in outbox.pending():
            job_id, sha = old["job"], old["digest"]
            attempted.add(job_id)
            try:
                payload = outbox.recover(job_id, sha)
                events.append(_publish(bus, ledger, outbox, job_id, sha, payload))
            except Exception as exc:
                events.append({"job_id": job_id, "status": "UNCERTAIN", "error": type(exc).__name__})
        try:
            bus.fetch()
        except Exception as exc:
            return events + [{"status": "ERROR", "error": "command fetch failed: " + type(exc).__name__}]
        runner = None
        for path in bus.list_jobs():
            job_id = Path(path).stem
            if not JOB_RE.fullmatch(job_id):
                continue
            try:
                raw, sha = bus.read_job(path)
            except Exception as exc:
                events.append({"job_id": job_id, "status": "ERROR", "error": type(exc).__name__})
                continue
            seen = outbox.get(job_id)
            historic = ledger.seen(job_id)
            if (seen and seen["digest"] != sha) or (historic and historic != sha):
                events.append({"job_id": job_id, "status": "REJECTED", "error": "conflicting job identity"})
                continue
            if job_id in attempted or seen or historic:
                continue
            if not outbox.claim(job_id, sha):
                continue
            started, executing = clock(), False
            try:
                job = validate_job(raw, path=path, now=started)
                runner = runner or configured_runner(config.fleet_config)
                executing = True
                result = execute_job(runner, job)
                payload = {"version": 1, "job_id": job_id, "job_sha256": sha, "host": job["host"], "action": job["action"],
                           "started_at_unix": started, "finished_at_unix": clock(), "status": receipt_status(result), "result": result}
            except Exception as exc:
                payload = {"version": 1, "job_id": job_id, "job_sha256": sha, "started_at_unix": started,
                           "finished_at_unix": clock(), "status": "UNCERTAIN" if executing else "ERROR",
                           "error": str(exc) if isinstance(exc, (ContractError, RelayError)) and not executing else type(exc).__name__}
            outbox.save(job_id, sha, payload)
            events.append(_publish(bus, ledger, outbox, job_id, sha, payload))
    return events


def run_forever(config):
    while True:
        try:
            for result in run_once(config):
                print(json.dumps(result, sort_keys=True), flush=True)
        except Exception as exc:
            print(json.dumps({"relay_error": type(exc).__name__}), flush=True)
        time.sleep(config.poll_seconds)
