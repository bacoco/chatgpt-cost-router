"""Local serialization and cancellation never confer new connector permissions."""
from functools import wraps
from operation_contracts.common import integer
from operation_contracts.locking import file_lock


def serialized(method):
    @wraps(method)
    def wrapped(self, project, id_, *args, **kwargs):
        # Resolve and authorize before using a caller-provided identifier as a path.
        row = self.row(project, id_)
        with file_lock(self.journal.path.parent / "workflow-locks" / (row["id"] + ".lock")):
            return method(self, project, id_, *args, **kwargs)
    return wrapped


@serialized
def cancel(engine, project, id_):
    row = engine.row(project, id_)
    if row["state"] in {"SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"}:
        return engine.status(project, id_)
    effects = [engine.journal.effect(id_, step["id"]) for step in row["request"]["steps"]]
    uncertain = any(e and e["state"] in {"PENDING", "READY_VERIFY", "UNCERTAIN"} for e in effects)
    engine.journal.transition(id_, {"QUEUED", "RUNNING", "UNCERTAIN"},
                              "UNCERTAIN" if uncertain else "CANCELLED", {"cancel_requested": True})
    return engine.status(project, id_)


def events(engine, project, id_, after=0):
    engine.row(project, id_)
    integer(after, 0, 10**12, "event cursor")
    return {"events": engine.journal.events(engine.principal, project, id_, after)}
