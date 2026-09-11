"""A: native Chat tool driving or direct adapters, with no second model runtime."""
import time
import uuid
from operation_contracts.common import ContractError, digest
from .catalog import Catalog
from .capability_store import CapabilityStore, SURFACES
from .workflows import validate_workflow, resolve


class Operations:
    def __init__(self, projects, journal, principal, *, surface="chatgpt-web-chat", session="current-chat", catalog=None):
        if surface not in SURFACES:
            raise ContractError("invalid surface")
        self.projects, self.journal, self.principal = projects, journal, principal
        self.surface, self.session, self.catalog = surface, session, catalog or Catalog()
        self.capabilities = CapabilityStore(journal)
        self.policy = digest([projects.revision, self.catalog.revision])

    def submit(self, workflow):
        workflow = validate_workflow(workflow, self.catalog)
        project = workflow["project_id"]
        self.projects.project(self.principal, project)
        row, new = self.journal.register(self.principal, project, "workflow", workflow["idempotency_key"], workflow, self.policy)
        return {"run_id":row["id"], "state":row["state"], "deduplicated":not new}

    def row(self, project, id_):
        self.projects.project(self.principal, project)
        row = self.journal.get(self.principal, project, id_)
        if row["kind"] != "workflow":
            raise ContractError("not an A workflow")
        return row

    def outputs(self, row):
        out = {}
        for step in row["request"]["steps"]:
            effect = self.journal.effect(row["id"], step["id"])
            if effect and "output" in effect["data"]:
                out[step["id"]] = effect["data"]["output"]
        return out

    def status(self, project, id_):
        row = self.row(project, id_)
        steps = []
        for step in row["request"]["steps"]:
            effect = self.journal.effect(id_, step["id"])
            steps.append({"id":step["id"], "action":step["action"], "resource":step["resource"],
                          "state":effect["state"] if effect else "READY",
                          "evidence_source":effect["data"].get("evidence_source") if effect else None})
        return {"run_id":id_, "project_id":project, "state":row["state"], "steps":steps,
                "extra_model_calls":0,
                "partial":any(step["state"] == "VERIFIED" for step in steps) and row["state"] != "SUCCEEDED"}

    def approve(self, project, id_, step_id):
        row = self.row(project, id_)
        step = next((step for step in row["request"]["steps"] if step["id"] == step_id), None)
        if step is None:
            raise ContractError("unknown step")
        exact = {**step, "arguments":resolve(step["arguments"], self.outputs(row))}
        self.projects.resource(self.principal, project, step["resource"], step["action"], exact["arguments"])
        self.journal.approve(id_, step_id, exact)
        return {"run_id":id_, "step":step_id, "approval":"bound-to-exact-step-and-inputs"}

    def invocation(self, project, step, kind, outputs):
        spec = step if kind == "call" else step[kind]
        args = resolve(spec["arguments"], outputs)
        binding = self.projects.resource(self.principal, project, step["resource"], spec["action"], args)
        capability = self.capabilities.require(self.principal, project, step["resource"], spec["action"],
                                              self.surface, self.session, binding)
        return {"resource":step["resource"], "action":spec["action"], "arguments":args,
                "connector":binding["connector"], "account_ref":binding["account_ref"],
                "tool_name":capability["tool_name"], "read_only":self.catalog.get(spec["action"])["read_only"]}

    def next(self, project, id_):
        row = self.row(project, id_)
        if row["state"] in {"SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED", "UNCERTAIN"}:
            return self.status(project, id_)
        if row["policy"] != self.policy:
            raise ContractError("project/action policy changed; review before continuing")
        if row["request"]["deadline"] <= time.time():
            effects = [self.journal.effect(id_, step["id"]) for step in row["request"]["steps"]]
            pending = any(effect and effect["state"] in {"PENDING", "READY_VERIFY"} for effect in effects)
            self.journal.transition(id_, {"QUEUED", "RUNNING"}, "UNCERTAIN" if pending else "BLOCKED", {"reason":"deadline"})
            return self.status(project, id_)
        self.journal.transition(id_, {"QUEUED"}, "RUNNING")
        outputs = self.outputs(row)
        for step in row["request"]["steps"]:
            self.journal.prepare_effect(id_, step["id"], step)
            effect = self.journal.effect(id_, step["id"])
            state = effect["state"]
            if state == "VERIFIED":
                continue
            if state == "PENDING":
                return {"run_id":id_, "state":"AWAITING_RESULT", "step":step["id"], "redispatch_allowed":False}
            if state not in {"READY", "READY_CALL", "READY_VERIFY"}:
                return self.status(project, id_)
            kind = "preflight" if state == "READY" and "preflight" in step else "verify" if state == "READY_VERIFY" else "call"
            invocation = self.invocation(project, step, kind, outputs)
            exact = {**step, "arguments":resolve(step["arguments"], outputs)}
            if kind == "call" and self.catalog.get(step["action"])["confirmation"] and not self.journal.approved(id_, step["id"], exact):
                return {"run_id":id_, "state":"AWAITING_APPROVAL", "step":step["id"], "invocation":invocation}
            token = uuid.uuid4().hex
            data = {**effect["data"], "pending":{"kind":kind, "token":token, "invocation":invocation}}
            if not self.journal.effect_transition(id_, step["id"], {state}, "PENDING", data):
                return {"run_id":id_, "state":"AWAITING_RESULT", "redispatch_allowed":False}
            return {"run_id":id_, "state":"INVOKE_TOOL", "step":step["id"], "token":token, "kind":kind,
                    "invocation":invocation, "instruction":"Invoke the exact native tool once and record its actual return. Never substitute model delegation."}
        self.journal.transition(id_, {"RUNNING"}, "SUCCEEDED", {"outputs_digest":digest(outputs)})
        return self.status(project, id_)

    def record(self, project, id_, step, token, output, *, error=False, evidence_source="native-tool-observation"):
        from .results import record
        return record(self, project, id_, step, token, output, error=error, evidence_source=evidence_source)

    def reconcile(self, project, id_, step):
        from .results import reconcile
        return reconcile(self, project, id_, step)

    def run(self, project, id_, transport):
        from .results import drive
        return drive(self, project, id_, transport)
