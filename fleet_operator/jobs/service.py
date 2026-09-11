"""B lifecycle service; persists intent before spawning an owned foreground supervisor."""
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from operation_contracts.common import ContractError, canonical, integer
from operation_contracts.files import private_json
from operation_contracts.journal import Journal, TERMINAL
from .requests import validate_request
from .workspace import root_for, artifacts


class Jobs:
    def __init__(self, config):
        self.config = config
        self.journal = Journal(config.state_dir / "jobs.sqlite3")

    def row(self, project, id_):
        self.config.projects.project(self.config.principal, project)
        row = self.journal.get(self.config.principal, project, id_)
        if row["kind"] != "process" or row["request"]["node_id"] != self.config.node_id:
            raise ContractError("not a process on this node")
        return row

    def submit(self, request):
        request = validate_request(request, self.config)
        row, new = self.journal.register(self.config.principal, request["project_id"], "process",
                                         request["idempotency_key"], request, self.config.revision)
        return {**self.status(row["project"],row["id"]),"deduplicated":not new}

    def status(self, project, id_):
        row = self.row(project,id_)
        data = row["data"]
        profile = self.config.profiles.get(row["request"]["profile"], {})
        return {"run_id":id_, "project_id":project, "node_id":self.config.node_id, "state":row["state"],
                "profile":row["request"]["profile"], "isolation":data.get("isolation",profile.get("isolation","unknown")),
                "source":row["request"].get("source"), "created":row["created"], "updated":row["updated"],
                "metrics":data.get("metrics"), "heartbeat":data.get("heartbeat"), "progress":data.get("progress"),
                "last_output_at":data.get("last_output_at"), "exit_code":data.get("exit_code"),
                "reason":data.get("reason"), "runtime_revision":data.get("runtime_revision"),
                "extra_model_calls":0}

    def start(self, project, id_):
        before = self.row(project,id_)
        if before["state"] != "QUEUED":
            return self.status(project,id_)
        if before["policy"] != self.config.revision:
            self.journal.transition(id_,{"QUEUED"},"BLOCKED",{"reason":"operator policy changed"})
            return self.status(project,id_)
        validate_request(before["request"], self.config)
        if before["request"]["deadline"] <= time.time():
            self.journal.transition(id_,{"QUEUED"},"TIMED_OUT",{"reason":"deadline before start"})
            return self.status(project,id_)
        if self.config.path is None or not self.config.path.is_file():
            raise ContractError("durable node config file required")
        token = uuid.uuid4().hex
        claimed = False
        with self.journal.transaction() as db:
            count = db.execute("SELECT COUNT(*) FROM operations WHERE kind='process' AND state IN ('RUNNING','CANCELLING')").fetchone()[0]
            if count < self.config.max_concurrency:
                data = canonical({"token":token,"heartbeat":time.time(),
                                  "isolation":self.config.profile(before["request"]["profile"])["isolation"],
                                  "runtime_revision":self.config.document.get("runtime_revision","unversioned")})
                changed = db.execute("UPDATE operations SET state='RUNNING',data=?,updated=? WHERE id=? AND state='QUEUED'",
                                     (data,time.time(),id_)).rowcount
                if changed:
                    claimed = True
                    self.journal._event(db,id_,"claimed",{"node":self.config.node_id})
        if not claimed:
            return self.status(project,id_)
        script = Path(__file__).resolve().parents[1] / "process_worker.py"
        try:
            child = subprocess.Popen([sys.executable,str(script),"--config",str(self.config.path),"--project",project,
                                      "--run",id_,"--token",token], stdin=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,close_fds=True)
            threading.Thread(target=child.wait,daemon=True).start()
        except OSError:
            self.journal.transition(id_,{"RUNNING"},"FAILED",{"reason":"supervisor spawn failed"},token=token)
        return self.status(project,id_)

    def cancel(self, project, id_):
        row = self.row(project,id_)
        if row["state"] == "QUEUED":
            self.journal.transition(id_,{"QUEUED"},"CANCELLED",{"reason":"cancelled before execution"})
        elif row["state"] == "RUNNING":
            self.journal.transition(id_,{"RUNNING"},"CANCELLING",{"cancel_requested_at":time.time()})
        return self.status(project,id_)

    def logs(self, project, id_, stream="stdout", offset=0, limit=32768):
        self.row(project,id_)
        if stream not in {"stdout","stderr"}:
            raise ContractError("invalid stream")
        integer(offset,0,10**9,"offset")
        integer(limit,1,131072,"limit")
        path = root_for(self.config,id_) / (stream+".log")
        if not path.exists():
            return {"run_id":id_,"stream":stream,"offset":offset,"next_offset":offset,"text":""}
        fd = os.open(path,os.O_RDONLY | os.O_NOFOLLOW)
        try:
            os.lseek(fd,offset,os.SEEK_SET)
            raw = os.read(fd,limit)
        finally:
            os.close(fd)
        return {"run_id":id_,"stream":stream,"offset":offset,"next_offset":offset+len(raw),
                "text":raw.decode("utf-8",errors="replace")}

    def result(self, project, id_):
        row = self.row(project,id_)
        if row["state"] not in TERMINAL:
            raise ContractError("process is not terminal")
        return {**self.status(project,id_),"artifacts":row["data"].get("artifacts",[]),
                "output_truncated":row["data"].get("output_truncated",False),
                "request_digest":row["digest"],"receipt_digest":row["data"].get("receipt_digest")}

    def reconcile(self, project, id_):
        from operation_contracts.common import digest
        row = self.row(project,id_)
        if row["state"] != "UNCERTAIN":
            raise ContractError("only uncertain processes need reconciliation")
        receipt = private_json(root_for(self.config,id_) / "result.json")
        expected = (id_,row["digest"],row["data"].get("token"),row["policy"])
        observed = (receipt.get("run_id"),receipt.get("request_digest"),receipt.get("token"),receipt.get("policy"))
        if expected != observed or receipt.get("state") not in TERMINAL-{"UNCERTAIN"}:
            raise ContractError("receipt does not prove the exact submitted execution")
        current = artifacts({"artifacts":[item["name"] for item in receipt["artifacts"]]},root_for(self.config,id_) / "workspace")
        if current != receipt["artifacts"]:
            raise ContractError("recorded artifacts changed")
        self.journal.transition(id_,{"UNCERTAIN"},receipt["state"],{**receipt,"receipt_digest":digest(receipt)},token=expected[2])
        return self.result(project,id_)

    def artifact(self, project, id_, name, offset=0, limit=65536):
        from .artifact_io import read_artifact
        return read_artifact(self, project, id_, name, offset, limit)

    def health(self):
        from .metrics import node_health
        return node_health(self)

    def recover_stale(self, age=120):
        integer(age,5,86400,"stale age")
        recovered = []
        with self.journal.transaction() as db:
            rows = db.execute("SELECT * FROM operations WHERE principal=? AND kind='process' AND state IN ('RUNNING','CANCELLING')",
                              (self.config.principal,)).fetchall()
        for record in rows:
            row = self.journal.decode(record)
            if time.time()-row["data"].get("heartbeat", row["updated"]) > age:
                if self.journal.transition(row["id"], {row["state"]}, "UNCERTAIN",
                                           {"reason":"supervisor heartbeat lost"}, token=row["data"].get("token")):
                    recovered.append(row["id"])
        return recovered

    def profiles(self, project):
        policy = self.config.projects.project(self.config.principal,project)
        return [{"profile":key,"description":value.get("description",""),"isolation":value["isolation"]}
                for key,value in self.config.profiles.items() if key in policy.get("profiles",[])
                and self.config.node_id in policy.get("nodes",[])]

    def start_pending(self):
        with self.journal.transaction() as db:
            rows = db.execute("SELECT id,project FROM operations WHERE principal=? AND kind='process' AND state='QUEUED' ORDER BY created,id LIMIT 200",
                              (self.config.principal,)).fetchall()
        for row in rows:
            self.start(row["project"],row["id"])
