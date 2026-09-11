"""Crash-safe dispatch and publication; a lost reply never authorizes a replay."""
from contextlib import contextmanager
import fcntl
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from operation_contracts.common import ContractError, canonical
from operation_contracts.files import atomic_json, private_json


def _identity(job, sha):
    if not isinstance(job, str) or not re.fullmatch(r"[A-Za-z0-9._-]{8,80}", job):
        raise ContractError("invalid outbox job identity")
    if not isinstance(sha, str) or not 1 <= len(sha) <= 128:
        raise ContractError("invalid outbox payload identity")


@contextmanager
def relay_lock(state_dir):
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(directory / "dispatch.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ContractError("another relay owns this dispatch state") from exc
        yield
    finally:
        os.close(fd)


class Outbox:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.directory / "outbox.sqlite3"
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS dispatch(job TEXT PRIMARY KEY,digest TEXT NOT NULL,state TEXT NOT NULL,result TEXT)")
        self.path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(str(self.path), timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _decode(row):
        return None if row is None else {**dict(row), "result": json.loads(row["result"]) if row["result"] else None}

    def get(self, job):
        with self.connect() as db:
            return self._decode(db.execute("SELECT * FROM dispatch WHERE job=?", (job,)).fetchone())

    def pending(self):
        with self.connect() as db:
            return [self._decode(row) for row in db.execute("SELECT * FROM dispatch WHERE state!='PUBLISHED' ORDER BY rowid LIMIT 1000")]

    def claim(self, job, sha):
        _identity(job, sha)
        with self.connect() as db:
            row = db.execute("SELECT digest FROM dispatch WHERE job=?", (job,)).fetchone()
            if row:
                if row["digest"] != sha:
                    raise ContractError("job id belongs to a different payload")
                return False
            db.execute("INSERT INTO dispatch VALUES(?,?,?,NULL)", (job, sha, "RUNNING"))
            return True

    @staticmethod
    def _validate_result(job, sha, result):
        if not isinstance(result, dict) or (result.get("job_id"), result.get("job_sha256")) != (job, sha):
            raise ContractError("private receipt belongs to a different dispatch")
        if result.get("version") != 1 or result.get("status") not in {
            "PASS", "FAILED", "ERROR", "UNCERTAIN", "ACCEPTED", "CANCELLED", "TIMED_OUT", "BLOCKED"
        }:
            raise ContractError("invalid private dispatch receipt")

    def save(self, job, sha, result):
        _identity(job, sha)
        self._validate_result(job, sha, result)
        with self.connect() as db:
            row = db.execute("SELECT * FROM dispatch WHERE job=?", (job,)).fetchone()
            if row is None or row["digest"] != sha:
                raise ContractError("dispatch identity changed")
            if row["result"] and row["result"] != canonical(result):
                raise ContractError("refusing to overwrite an existing receipt")
            path = self.directory / "results" / (job + ".json")
            if path.exists() or path.is_symlink():
                if private_json(path) != result:
                    raise ContractError("private receipt differs; preserve it for operator review")
            else:
                atomic_json(path, result)
            if row["state"] != "PUBLISHED":
                db.execute("UPDATE dispatch SET state='RESULT',result=? WHERE job=?", (canonical(result), job))

    def recover(self, job, sha):
        """Recover the fsynced receipt before considering an uncertain outcome."""
        row = self.get(job)
        if row is None or row["digest"] != sha:
            raise ContractError("unclaimed or conflicting dispatch")
        if row["result"] is not None:
            return row["result"]
        path = self.directory / "results" / (job + ".json")
        if path.exists() or path.is_symlink():
            result = private_json(path)
            self._validate_result(job, sha, result)
        else:
            result = {"version": 1, "job_id": job, "job_sha256": sha, "status": "UNCERTAIN",
                      "finished_at_unix": time.time(),
                      "error": "execution was claimed before interruption; automatic replay forbidden"}
        self.save(job, sha, result)
        return result

    def uncertain(self, job, sha):
        return self.recover(job, sha)

    def published(self, job, sha):
        with self.connect() as db:
            changed = db.execute("UPDATE dispatch SET state='PUBLISHED' WHERE job=? AND digest=? AND state='RESULT'", (job, sha)).rowcount
            if not changed:
                raise ContractError("no matching durable result to acknowledge")
