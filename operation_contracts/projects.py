"""Project grants are operator policy, never permissions granted by repository text."""
from __future__ import annotations
from copy import deepcopy
from .common import ContractError, fields, identifier, load, digest


class Projects:
    def __init__(self, document):
        fields(document, ("version", "projects"))
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("unsupported project registry version")
        if not isinstance(document["projects"], dict) or not document["projects"]:
            raise ContractError("projects must be a nonempty object")
        for project_id, project in document["projects"].items():
            identifier(project_id, "project")
            fields(project, ("members",), ("resources", "nodes", "profiles", "accounts", "description"))
            for key in ("members", "nodes", "profiles", "accounts"):
                values = project.get(key, [])
                if not isinstance(values, list):
                    raise ContractError(f"invalid project {key}")
                for val in values:
                    identifier(val, key)
                if len(set(values)) != len(values):
                    raise ContractError(f"duplicate project {key}")
            if not project["members"]:
                raise ContractError("project must have a member")
            if not isinstance(project.get("resources", {}), dict):
                raise ContractError("invalid resources")
            for resource_id, resource in project.get("resources", {}).items():
                identifier(resource_id, "resource")
                fields(resource, ("connector", "account_ref", "actions"), ("bindings",))
                identifier(resource["connector"], "connector")
                identifier(resource["account_ref"], "account reference")
                if not isinstance(resource["actions"], list) or not resource["actions"]:
                    raise ContractError("resource requires actions")
                for action in resource["actions"]:
                    identifier(action, "action")
                if not isinstance(resource.get("bindings", {}), dict):
                    raise ContractError("resource bindings must be an object")
        self.document = deepcopy(document)
        self.revision = digest(document)

    @classmethod
    def from_file(cls, path):
        return cls(load(path))

    def project(self, principal, project_id):
        identifier(principal, "principal")
        project = self.document["projects"].get(project_id)
        if project is None or principal not in project["members"]:
            raise ContractError("project is unavailable to this principal")
        return deepcopy(project)

    def list(self, principal):
        return [{"project_id": key, "description": val.get("description", "")}
                for key, val in self.document["projects"].items() if principal in val["members"]]

    def resource(self, principal, project_id, resource_id, action, arguments):
        project = self.project(principal, project_id)
        resource = project.get("resources", {}).get(resource_id)
        if resource is None or action not in resource["actions"]:
            raise ContractError("resource/action is not authorized for this project")
        for key, expected in resource.get("bindings", {}).items():
            if arguments.get(key) != expected:
                raise ContractError("operation does not match the bound project resource")
        return resource

    def execution(self, principal, project_id, node, profile, account_ref=None):
        project = self.project(principal, project_id)
        if node not in project.get("nodes", []) or profile not in project.get("profiles", []):
            raise ContractError("node/profile is not authorized for this project")
        if account_ref is not None and account_ref not in project.get("accounts", []):
            raise ContractError("model account is not authorized for this project")
        return project
