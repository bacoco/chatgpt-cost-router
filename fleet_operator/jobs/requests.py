"""B submit contract, usable from Chat, MCP, CLI or another authorized client."""
from copy import deepcopy
from operation_contracts.common import ContractError, SHA, fields, identifier, number, no_credentials


def validate_request(value, config):
    fields(value, ("version", "project_id", "idempotency_key", "node_id", "profile", "inputs", "deadline"), ("source",))
    if type(value["version"]) is not int or value["version"] != 1:
        raise ContractError("unsupported task version")
    for key in ("project_id", "idempotency_key", "node_id", "profile"):
        identifier(value[key], key)
    if value["node_id"] != config.node_id:
        raise ContractError("request addressed to another node")
    if not isinstance(value["inputs"], dict):
        raise ContractError("task inputs must be a JSON object")
    number(value["deadline"], 0, 32_503_680_000, "deadline")
    config.projects.execution(config.principal, value["project_id"], config.node_id, value["profile"])
    profile = config.profile(value["profile"])
    if profile.get("source_required") and "source" not in value:
        raise ContractError("profile requires an immutable source")
    if "source" in value:
        source = value["source"]
        fields(source, ("repo", "sha"))
        repository = config.document.get("repositories", {}).get(value["project_id"])
        if not repository or source["repo"] != repository["slug"] or not isinstance(source["sha"],str) or not SHA.fullmatch(source["sha"]):
            raise ContractError("repository/SHA does not match project binding")
    no_credentials(value)
    return deepcopy(value)
