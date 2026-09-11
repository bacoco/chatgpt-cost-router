"""Central account-scoped operator budgets; not automatic provider quota telemetry."""
from __future__ import annotations
import time
from .common import ContractError, identifier, integer, number


class AccountBudgets:
    def __init__(self, journal):
        self.journal = journal
        with journal.transaction() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS account_allowances(
                account TEXT PRIMARY KEY, units INTEGER NOT NULL, expires REAL NOT NULL,
                evidence TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS account_reservations(
                account TEXT NOT NULL, operation TEXT NOT NULL, units INTEGER NOT NULL,
                settled INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(account,operation));
            """)

        with journal.transaction() as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(account_reservations)")}
            if "reserved_units" not in columns:
                db.execute("ALTER TABLE account_reservations ADD COLUMN reserved_units INTEGER")
                db.execute("UPDATE account_reservations SET reserved_units=units WHERE settled=0")

    def observe(self, account_ref, limit_units, expires, evidence_ref, *, now=None):
        identifier(account_ref)
        identifier(evidence_ref, "budget evidence reference")
        integer(limit_units, 0, 1_000_000_000, "allowance units")
        now = time.time() if now is None else now
        number(expires, now+1, now+604800, "allowance expiry")
        with self.journal.transaction() as db:
            db.execute("INSERT OR REPLACE INTO account_allowances VALUES(?,?,?,?)",
                       (account_ref,limit_units,expires,evidence_ref))

    def reserve(self, account_ref, operation_id, units, *, now=None):
        identifier(account_ref)
        identifier(operation_id)
        integer(units, 1, 1_000_000_000)
        now = time.time() if now is None else now
        with self.journal.transaction() as db:
            old = db.execute("SELECT units,reserved_units,settled FROM account_reservations WHERE account=? AND operation=?",
                             (account_ref,operation_id)).fetchone()
            if old:
                if old["reserved_units"] is None:
                    raise ContractError("historical settled reservation has no original amount; no new reservation allowed")
                if old["reserved_units"] != units:
                    raise ContractError("reservation changed")
                return
            quota = db.execute("SELECT * FROM account_allowances WHERE account=?", (account_ref,)).fetchone()
            if not quota or quota["expires"] <= now:
                raise ContractError("account allowance unknown or stale")
            used = db.execute("SELECT COALESCE(SUM(units),0) FROM account_reservations WHERE account=?",
                              (account_ref,)).fetchone()[0]
            if used+units > quota["units"]:
                raise ContractError("account budget exhausted across projects/nodes")
            db.execute("INSERT INTO account_reservations(account,operation,units,reserved_units) VALUES(?,?,?,?)",
                       (account_ref,operation_id,units,units))

    def settle(self, account_ref, operation_id, actual_units):
        integer(actual_units, 0, 1_000_000_000)
        with self.journal.transaction() as db:
            row = db.execute("SELECT * FROM account_reservations WHERE account=? AND operation=?",
                             (account_ref,operation_id)).fetchone()
            if row is None:
                raise ContractError("no reservation")
            if row["settled"]:
                if row["units"] != actual_units:
                    raise ContractError("conflicting settlement")
                return
            db.execute("UPDATE account_reservations SET units=?,settled=1 WHERE account=? AND operation=?",
                       (actual_units,account_ref,operation_id))

    def status(self, account_ref, *, now=None):
        now = time.time() if now is None else now
        with self.journal.transaction() as db:
            row = db.execute("SELECT * FROM account_allowances WHERE account=?", (account_ref,)).fetchone()
            used = db.execute("SELECT COALESCE(SUM(units),0) FROM account_reservations WHERE account=?",
                              (account_ref,)).fetchone()[0]
            known = bool(row and row["expires"] > now)
            return {"account_ref":account_ref,"known":known,"reserved_or_used_units":used,
                    "remaining_units":max(0,row["units"]-used) if known else None,
                    "source":"operator-budget" if known else "unknown"}
