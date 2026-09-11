"""Durable principal/project-scoped journal and compare-and-set transitions."""
from __future__ import annotations
from contextlib import contextmanager
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from .common import ContractError, canonical, digest, identifier

TERMINAL = frozenset({"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT", "BLOCKED", "UNCERTAIN"})


class Journal:
    def __init__(self, path):
        supplied = Path(path).expanduser()
        if supplied.is_symlink():
            raise ContractError("journal cannot be a symlink")
        self.path = supplied.absolute()
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        os.fchmod(fd, 0o600)
        os.close(fd)
        with self.transaction() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS operations(
                  id TEXT PRIMARY KEY, principal TEXT NOT NULL, project TEXT NOT NULL,
                  kind TEXT NOT NULL, idem TEXT NOT NULL, digest TEXT NOT NULL,
                  request TEXT NOT NULL, policy TEXT NOT NULL, state TEXT NOT NULL,
                  data TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
                  UNIQUE(principal,project,kind,idem));
                CREATE TABLE IF NOT EXISTS events(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT, operation TEXT NOT NULL,
                  at REAL NOT NULL, event TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS effects(
                  operation TEXT NOT NULL, step TEXT NOT NULL, digest TEXT NOT NULL,
                  state TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(operation,step));
                CREATE TABLE IF NOT EXISTS approvals(
                  operation TEXT NOT NULL, step TEXT NOT NULL, digest TEXT NOT NULL,
                  PRIMARY KEY(operation,step));
            """)
        os.chmod(self.path, 0o600)

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(str(self.path), timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("PRAGMA journal_mode=WAL")
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def decode(row):
        if row is None:
            raise ContractError("operation not found in this context")
        item = dict(row)
        for key in ("request", "data"):
            item[key] = json.loads(item[key])
        return item

    def register(self, principal, project, kind, key, request, policy):
        for val in (principal, project, kind, key):
            identifier(val)
        hash_ = digest(request)
        now = time.time()
        with self.transaction() as db:
            row = db.execute("SELECT * FROM operations WHERE principal=? AND project=? AND kind=? AND idem=?",
                             (principal, project, kind, key)).fetchone()
            if row:
                if row["digest"] != hash_:
                    raise ContractError("idempotency key belongs to a different request")
                return self.decode(row), False
            id_ = uuid.uuid4().hex
            db.execute("INSERT INTO operations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                       (id_,principal,project,kind,key,hash_,canonical(request),policy,"QUEUED","{}",now,now))
            self._event(db, id_, "submitted", {})
            return self.decode(db.execute("SELECT * FROM operations WHERE id=?", (id_,)).fetchone()), True

    @staticmethod
    def _event(db, id_, event, data):
        db.execute("INSERT INTO events(operation,at,event,data) VALUES(?,?,?,?)",
                   (id_, time.time(), event, canonical(data)))

    def get(self, principal, project, id_):
        with self.transaction() as db:
            return self.decode(db.execute("SELECT * FROM operations WHERE id=? AND principal=? AND project=?",
                                          (id_, principal, project)).fetchone())

    def list(self, principal, project, kind=None):
        with self.transaction() as db:
            rows = db.execute("SELECT * FROM operations WHERE principal=? AND project=? ORDER BY created DESC LIMIT 200",
                              (principal, project)).fetchall()
            return [self.decode(row) for row in rows if kind is None or row["kind"] == kind]

    def transition(self, id_, expected, new, data=None, *, token=None):
        with self.transaction() as db:
            row = self.decode(db.execute("SELECT * FROM operations WHERE id=?", (id_,)).fetchone())
            if row["state"] not in expected:
                return False
            if token is not None and row["data"].get("token") != token:
                return False
            merged = {**row["data"], **(data or {})}
            db.execute("UPDATE operations SET state=?,data=?,updated=? WHERE id=?",
                       (new, canonical(merged), time.time(), id_))
            safe = {k:v for k,v in (data or {}).items() if k not in {"token", "output"}}
            self._event(db, id_, new, safe)
            return True

    def events(self, principal, project, id_, after=0):
        from .common import integer
        integer(after, 0, 2**63-1, "event offset")
        self.get(principal, project, id_)
        with self.transaction() as db:
            return [{**dict(row), "data": json.loads(row["data"])} for row in db.execute(
                "SELECT * FROM events WHERE operation=? AND seq>? ORDER BY seq LIMIT 200", (id_, after))]

    def effect(self, id_, step):
        with self.transaction() as db:
            row = db.execute("SELECT * FROM effects WHERE operation=? AND step=?", (id_, step)).fetchone()
            return None if row is None else {**dict(row), "data": json.loads(row["data"])}

    def prepare_effect(self, id_, step, request):
        with self.transaction() as db:
            row = db.execute("SELECT digest FROM effects WHERE operation=? AND step=?", (id_,step)).fetchone()
            if row:
                if row["digest"] != digest(request):
                    raise ContractError("registered effect changed")
                return
            db.execute("INSERT INTO effects VALUES(?,?,?,?,?)", (id_,step,digest(request),"READY","{}"))

    def effect_transition(self, id_, step, expected, new, data, *, token=None):
        with self.transaction() as db:
            row = db.execute("SELECT * FROM effects WHERE operation=? AND step=?", (id_,step)).fetchone()
            if not row or row["state"] not in expected:
                return False
            if token is not None and json.loads(row["data"]).get("pending", {}).get("token") != token:
                return False
            db.execute("UPDATE effects SET state=?,data=? WHERE operation=? AND step=?",
                       (new,canonical(data),id_,step))
            self._event(db, id_, "effect-"+new.lower(), {"step":step})
            return True

    def approve(self, id_, step, request):
        with self.transaction() as db:
            db.execute("INSERT OR REPLACE INTO approvals VALUES(?,?,?)", (id_,step,digest(request)))

    def approved(self, id_, step, request):
        with self.transaction() as db:
            row = db.execute("SELECT digest FROM approvals WHERE operation=? AND step=?", (id_,step)).fetchone()
            return bool(row and row["digest"] == digest(request))

    def claim_invocation(self, id_, step, expected, data, read_only):
        """Fence cancellation/deadline and competing invocations in one transaction."""
        with self.transaction() as db:
            parent = self.decode(db.execute("SELECT * FROM operations WHERE id=?", (id_,)).fetchone())
            if parent["state"] != "RUNNING":
                raise ContractError("workflow no longer authorizes an invocation")
            if not read_only and (parent["data"].get("cancel_requested") or parent["request"]["deadline"] <= time.time()):
                raise ContractError("workflow no longer authorizes a mutation")
            current = db.execute("SELECT * FROM effects WHERE operation=? AND step=?", (id_,step)).fetchone()
            if not current or current["state"] != expected["state"] or json.loads(current["data"]) != expected["data"]:
                return False
            db.execute("UPDATE effects SET state='PENDING',data=? WHERE operation=? AND step=?", (canonical(data),id_,step))
            self._event(db,id_,"effect-pending",{"step":step,"kind":data["pending"]["kind"]})
            return True
