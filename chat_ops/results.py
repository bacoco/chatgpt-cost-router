"""A failed read-back is reconciled by reading; it never repeats a mutation."""
from operation_contracts.common import ContractError, no_credentials, digest
from .workflows import matches, resolve


def record(engine, project, id_, step_id, token, output, *, error=False, evidence_source="native-tool-observation"):
    row = engine.row(project, id_)
    no_credentials(output)
    effect = engine.journal.effect(id_, step_id)
    if not effect or effect["state"] != "PENDING" or effect["data"].get("pending", {}).get("token") != token:
        raise ContractError("no matching pending tool invocation")
    step = next(step for step in row["request"]["steps"] if step["id"] == step_id)
    pending = effect["data"]["pending"]
    if pending.get("session",engine.session) != engine.session or pending.get("surface",engine.surface) != engine.surface:
        raise ContractError("pending invocation belongs to another conversation context")
    data = {key:val for key,val in effect["data"].items() if key != "pending"}
    data.update(evidence_source=evidence_source, tool_result_digest=digest(output))
    parent_state = None
    if error:
        data["reason"] = "tool outcome uncertain; do not redispatch"
        new, parent_state = "UNCERTAIN", "UNCERTAIN"
    elif pending["kind"] == "call":
        data["output"] = output
        new = "READY_VERIFY" if "verify" in step else "VERIFIED"
    else:
        expectations = resolve(step[pending["kind"]]["expect"], engine.outputs(row))
        passed = matches(output, expectations)
        if pending["kind"] == "preflight":
            new = "READY_CALL" if passed else "BLOCKED"
        else:
            new = "VERIFIED" if passed else "UNCERTAIN"
            if passed and "output" not in data and "recover_output" in step["verify"]:
                recovered = resolve(step["verify"]["recover_output"], {"verification":output})
                no_credentials(recovered)
                data.update(output=recovered, output_recovered_from_verification=True)
        data[pending["kind"]+"_digest"] = digest(output)
        data["verification_passed"] = passed
        if not passed:
            parent_state = new
    if not engine.journal.effect_transition(id_, step_id, {"PENDING"}, new, data, token=token):
        raise ContractError("concurrent result already recorded")
    if parent_state:
        engine.journal.transition(id_, {"RUNNING"}, parent_state, {"reason":"tool_error" if error else "read_back_mismatch"})
    return engine.status(project, id_)


def reconcile(engine, project, id_, step_id):
    row = engine.row(project, id_)
    if row["policy"] != engine.policy:
        raise ContractError("policy changed; operator review required")
    step = next((step for step in row["request"]["steps"] if step["id"] == step_id), None)
    effect = engine.journal.effect(id_, step_id)
    if not step or not effect or effect["state"] not in {"UNCERTAIN", "PENDING"}:
        raise ContractError("no uncertain effect to reconcile")
    if "verify" in step:
        engine.invocation(project, step, "verify", engine.outputs(row))
        new = "READY_VERIFY"
    elif engine.catalog.get(step["action"])["read_only"]:
        new = "READY_CALL"
    else:
        raise ContractError("read-only reconciliation required")
    data = {key:val for key,val in effect["data"].items() if key != "pending"}
    if not engine.journal.effect_transition(id_, step_id, {effect["state"]}, new, data):
        raise ContractError("effect changed during reconciliation")
    engine.journal.transition(id_, {"UNCERTAIN"}, "RUNNING")
    return engine.next(project, id_)


def drive(engine, project, id_, transport):
    for _ in range(400):
        todo = engine.next(project, id_)
        if todo["state"] != "INVOKE_TOOL":
            return todo
        try:
            output = transport.invoke(todo["invocation"])
        except Exception:
            engine.record(project,id_,todo["step"],todo["token"],{},error=True,evidence_source="adapter-exception")
            return engine.status(project, id_)
        engine.record(project,id_,todo["step"],todo["token"],output,evidence_source="adapter-tool-return")
    raise ContractError("workflow transition bound exceeded")
