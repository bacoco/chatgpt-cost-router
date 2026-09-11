"""Never rerun a machine command because publishing its result failed."""
from contextlib import contextmanager
import fcntl
import json
import os
import sqlite3
import time
from pathlib import Path
from operation_contracts.common import ContractError, canonical
from operation_contracts.files import atomic_json


@contextmanager
def relay_lock(state_dir):
    directory = Path(state_dir)
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd = os.open(directory / "dispatch.lock",os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,0o600)
    try:
        try:
            fcntl.flock(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ContractError("another relay owns this dispatch state")
        yield
    finally:
        os.close(fd)


class Outbox:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.path = self.directory / "outbox.sqlite3"
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS dispatch(job TEXT PRIMARY KEY,digest TEXT NOT NULL,state TEXT NOT NULL,result TEXT)")
        self.path.chmod(0o600)

    def connect(self):
        db = sqlite3.connect(str(self.path),timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def get(self, job):
        with self.connect() as db:
            row = db.execute("SELECT * FROM dispatch WHERE job=?",(job,)).fetchone()
            return None if row is None else {**dict(row),"result":json.loads(row["result"]) if row["result"] else None}

    def claim(self, job, sha):
        with self.connect() as db:
            row = db.execute("SELECT digest FROM dispatch WHERE job=?",(job,)).fetchone()
            if row:
                if row["digest"] != sha:
                    raise ContractError("job id belongs to a different payload")
                return False
            db.execute("INSERT INTO dispatch VALUES(?,?,?,NULL)",(job,sha,"RUNNING"))
            return True

    def save(self, job, sha, result):
        atomic_json(self.directory / "results" / (job+".json"),result)
        with self.connect() as db:
            row = db.execute("SELECT digest FROM dispatch WHERE job=?",(job,)).fetchone()
            if row is None or row["digest"] != sha:
                raise ContractError("dispatch identity changed")
            db.execute("UPDATE dispatch SET state='RESULT',result=? WHERE job=?",(canonical(result),job))

    def uncertain(self, job, sha):
        result = {"version":1,"job_id":job,"job_sha256":sha,"status":"UNCERTAIN",
                  "finished_at_unix":time.time(),"error":"execution was claimed before interruption; automatic replay forbidden"}
        self.save(job,sha,result)
        return result

    def published(self, job, sha):
        with self.connect() as db:
            changed = db.execute("UPDATE dispatch SET state='PUBLISHED' WHERE job=? AND digest=? AND state='RESULT'",(job,sha)).rowcount
            if not changed:
                raise ContractError("no matching durable result to acknowledge")
