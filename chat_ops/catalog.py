"""Connector-independent actions; actual tool names come from current discovery."""
from copy import deepcopy
from operation_contracts.common import ContractError, fields, identifier, digest

READS = {
    "gmail": "search read thread.read draft.read",
    "github": "read search diff status pr.read issue.read",
    "cowboy": "read search",
    "calendar": "read search availability",
    "contacts": "read search",
    "documents": "read search",
    "serena": "read symbols references",
    "fleet": "status logs result artifact profiles nodes health events",
}
WRITES = {
    "gmail": "draft.create send draft.send trash",
    "github": "write branch.create issue.create issue.comment pr.create pr.review pr.merge",
    "cowboy": "publish update",
    "calendar": "create update delete",
    "contacts": "update",
    "documents": "write",
    "serena": "edit",
    "fleet": "submit start cancel reconcile",
}


class Catalog:
    def __init__(self, extensions=None):
        self.actions = {}
        for read, groups in ((True, READS), (False, WRITES)):
            for family, names in groups.items():
                for name in names.split():
                    self.actions[f"{family}.{name}"] = {
                        "read_only":read, "confirmation":not read,
                        "extra_model":False, "description":f"{family}: {name}",
                    }
        for name, spec in (extensions or {}).items():
            identifier(name, "action")
            fields(spec, ("read_only", "confirmation", "extra_model", "description"))
            if any(type(spec[key]) is not bool for key in ("read_only", "confirmation", "extra_model")):
                raise ContractError("action safety flags must be booleans")
            if name in self.actions:
                raise ContractError("built-in action safety cannot be overwritten")
            self.actions[name] = deepcopy(spec)
        self.revision = digest(self.actions)

    def get(self, action):
        if action not in self.actions:
            raise ContractError("unregistered action; operator-reviewed descriptor required")
        return deepcopy(self.actions[action])

    def list(self):
        return [{"action":key, **val} for key, val in sorted(self.actions.items())]
