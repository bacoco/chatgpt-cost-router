"""Versioned multi-app workflows: external data cannot grant permissions."""
from copy import deepcopy
from operation_contracts.common import ContractError, fields, identifier, no_credentials, number


def validate_workflow(value, catalog):
    fields(value, ("version", "project_id", "idempotency_key", "deadline", "steps"))
    if type(value["version"]) is not int or value["version"] != 1:
        raise ContractError("unsupported workflow version")
    identifier(value["project_id"])
    identifier(value["idempotency_key"])
    number(value["deadline"], 0, 32_503_680_000, "deadline")
    if not isinstance(value["steps"], list) or not 1 <= len(value["steps"]) <= 100:
        raise ContractError("workflow requires 1..100 steps")
    names = set()
    for step in value["steps"]:
        fields(step, ("id", "resource", "action", "arguments"), ("preflight", "verify", "recovery"))
        identifier(step["id"])
        if "." in step["id"]:
            raise ContractError("step ids cannot contain dots used by result references")
        identifier(step["resource"])
        if step["id"] in names:
            raise ContractError("duplicate workflow step")
        spec = catalog.get(step["action"])
        if spec["extra_model"]:
            raise ContractError("no implicit additional model delegation in Chat-first workflows")
        if not isinstance(step["arguments"], dict):
            raise ContractError("tool arguments must be an object")
        _references(step["arguments"], names)
        for key in ("preflight", "verify", "recovery"):
            if key not in step:
                continue
            check = step[key]
            fields(check, ("action", "arguments", "expect"), ("recover_output",) if key == "verify" else ())
            check_spec = catalog.get(check["action"])
            if not check_spec["read_only"] or check_spec["extra_model"]:
                raise ContractError("preflight/verification must be non-model read actions")
            if not isinstance(check["arguments"], dict) or not isinstance(check["expect"], dict) or not check["expect"]:
                raise ContractError("verification requires explicit arguments and expectations")
            _references({"arguments":check["arguments"], "expect":check["expect"]},
                        names | ({step["id"]} if key == "verify" else set()))
            if "recover_output" in check:
                if not isinstance(check["recover_output"], dict):
                    raise ContractError("recovered output must be an explicit object mapping")
                _references(check["recover_output"], {"verification"})
        if not spec["read_only"] and "verify" not in step:
            raise ContractError("write/send/publish requires read-back verification")
        names.add(step["id"])
    no_credentials(value)
    return deepcopy(value)


def _references(value, known):
    if isinstance(value, dict):
        if "$ref" in value:
            if set(value) != {"$ref"} or not isinstance(value["$ref"], str):
                raise ContractError("reference must contain only a string $ref")
            if value["$ref"].split(".")[0] not in known:
                raise ContractError("reference points to a missing/future step")
        else:
            for val in value.values():
                _references(val, known)
    elif isinstance(value, list):
        for val in value:
            _references(val, known)


def resolve(value, outputs):
    if isinstance(value, dict):
        if "$ref" in value:
            current = outputs
            try:
                for part in value["$ref"].split("."):
                    current = current[int(part)] if isinstance(current, list) else current[part]
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                raise ContractError("required prior tool result is unavailable") from exc
            return deepcopy(current)
        return {key:resolve(val, outputs) for key, val in value.items()}
    if isinstance(value, list):
        return [resolve(val, outputs) for val in value]
    return value


def matches(output, expect):
    for path, value in expect.items():
        current = output
        try:
            if path:
                for part in path.split("."):
                    current = current[int(part)] if isinstance(current, list) else current[part]
        except (KeyError, IndexError, ValueError, TypeError):
            return False
        if type(current) is not type(value) or current != value:
            return False
    return True
