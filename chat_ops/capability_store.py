"""Action evidence scoped to principal, project, resource, surface and session."""
import json
import time
from operation_contracts.common import ContractError, canonical, fields, identifier, number

SURFACES = frozenset({"chatgpt-web-chat", "codex-mac-chat", "codex-mac-work", "codex-cli",
                      "chatgpt-scheduled-task", "service"})
LEVELS = {"visible":0, "invocable":1, "executed":2, "verified":3, "denied":-1}


class CapabilityStore:
    def __init__(self, journal):
        self.journal = journal
        with journal.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS connector_evidence(scope TEXT PRIMARY KEY, observed REAL NOT NULL, data TEXT NOT NULL)")

    @staticmethod
    def scope(principal, project, resource, action, surface, session):
        if surface not in SURFACES:
            raise ContractError("unknown conversation surface")
        for value in (principal, project, resource, action, session):
            identifier(value)
        return canonical([principal, project, resource, action, surface, session])

    def observe(self, principal, project, resource, action, surface, session, evidence, *, now=None):
        fields(evidence, ("level", "tool_name", "connector", "account_ref", "observed_at", "expires_at", "evidence_ref"))
        now = time.time() if now is None else now
        if evidence["level"] not in LEVELS:
            raise ContractError("invalid capability level")
        number(evidence["observed_at"], now-86400, now+5, "observation time")
        number(evidence["expires_at"], evidence["observed_at"]+1, evidence["observed_at"]+3600, "expiry")
        for key in ("connector", "account_ref", "evidence_ref"):
            identifier(evidence[key], key)
        if not isinstance(evidence["tool_name"], str) or not 1 <= len(evidence["tool_name"]) <= 256:
            raise ContractError("tool name must come from current discovery")
        scope = self.scope(principal, project, resource, action, surface, session)
        with self.journal.transaction() as db:
            old = db.execute("SELECT * FROM connector_evidence WHERE scope=?", (scope,)).fetchone()
            if old and old["observed"] > evidence["observed_at"]:
                raise ContractError("cannot replace newer capability evidence")
            if old and old["observed"] == evidence["observed_at"] and old["data"] != canonical(evidence):
                raise ContractError("conflicting evidence at the same timestamp")
            db.execute("INSERT OR REPLACE INTO connector_evidence VALUES(?,?,?)",
                       (scope, evidence["observed_at"], canonical(evidence)))

    def require(self, principal, project, resource, action, surface, session, binding, *, now=None):
        now = time.time() if now is None else now
        scope = self.scope(principal, project, resource, action, surface, session)
        with self.journal.transaction() as db:
            row = db.execute("SELECT data FROM connector_evidence WHERE scope=?", (scope,)).fetchone()
        if not row:
            raise ContractError("capability not observed in this exact context")
        evidence = json.loads(row["data"])
        if evidence["expires_at"] <= now or LEVELS[evidence["level"]] < 1:
            raise ContractError("capability is expired, denied or only visible")
        if evidence["connector"] != binding["connector"] or evidence["account_ref"] != binding["account_ref"]:
            raise ContractError("observed connector account differs from project binding")
        return evidence
