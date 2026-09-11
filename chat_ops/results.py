"""A failed read-back is reconciled by reading; it never repeats a mutation."""
from operation_contracts.common import ContractError, no_credentials, digest
from .workflows import matches, resolve


def record(engine, project, id_, step_id, token, output, *, error=False, evidence_source="native-tool-observation"):
    row = engine.row(project, id_)
    if type(error) is not bool or not isinstance(evidence_source, str) or not 1 <= len(evidence_source) <= 256:
        raise ContractError("invalid result observation metadata")
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
        data["uncertain_kind"] = pending["kind"]
        new, parent_state = "UNCERTAIN", "UNCERTAIN"
    elif pending["kind"] == "call":
        data["output"] = output
        new = "READY_VERIFY" if "verify" in step else "VERIFIED"
    else:
        expectations = resolve(step[pending["kind"]]["expect"], engine.outputs(row))
        passed = matches(output, expectations)
        if pending["kind"] == "recovery":
            if passed:
                data["output"] = output
            new = "READY_VERIFY" if passed else "UNCERTAIN"
        elif pending["kind"] == "preflight":
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
            data["uncertain_kind"] = pending["kind"]
    if not engine.journal.effect_transition(id_, step_id, {"PENDING"}, new, data, token=token):
        raise ContractError("concurrent result already recorded")
    if row["data"].get("cancel_requested") and new in {"VERIFIED", "READY_CALL", "BLOCKED"}:
        engine.journal.transition(id_, {"RUNNING", "UNCERTAIN"}, "CANCELLED")
    if parent_state:
        engine.journal.transition(id_, {"RUNNING"}, parent_state, {"reason":"tool_error" if error else "read_back_mismatch"})
    return engine.status(project, id_)


def reconcile(engine, project, id_, step_id):
    """Read-only recovery may outlive a write deadline; it cannot redispatch a write."""
    row = engine.row(project, id_)
    if row["policy"] != engine.policy:
        raise ContractError("policy changed; operator review required")
    if row["state"] not in {"UNCERTAIN", "RUNNING"}:
        raise ContractError("workflow is not reconcilable")
    step = next((s for s in row["request"]["steps"] if s["id"] == step_id), None)
    effect = engine.journal.effect(id_, step_id)
    if not step or not effect or effect["state"] not in {"UNCERTAIN", "PENDING", "READY_VERIFY"}:
        raise ContractError("no uncertain effect to reconcile")
    phase = effect["data"].get("pending", {}).get("kind", effect["data"].get("uncertain_kind"))
    kind = "preflight" if phase == "preflight" else "verify" if "verify" in step else "call"
    spec = step if kind == "call" else step[kind]
    if not engine.catalog.get(spec["action"])["read_only"]:
        raise ContractError("read-only reconciliation required")
    outputs = engine.outputs(row)
    try:
        resolve(spec["arguments"], outputs)
        if kind != "call":
            resolve(spec["expect"], outputs)
    except ContractError:
        if kind != "verify" or "recovery" not in step:
            raise ContractError("lost result identity; an operator-bound recovery read is required") from None
        kind = "recovery"
    invocation = engine.invocation(project, step, kind, outputs)
    engine.journal.transition(id_, {"UNCERTAIN"}, "RUNNING")
    return engine.dispatch(row, step, effect, kind, invocation)


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
