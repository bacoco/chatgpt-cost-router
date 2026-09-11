"""Operator-owned process profiles: requests cannot supply shell commands or paths."""
from copy import deepcopy
import os
import re
from pathlib import Path
from operation_contracts.common import ContractError, fields, identifier, integer, load, digest
from operation_contracts.projects import Projects


class NodeConfig:
    def __init__(self, document, path=None):
        fields(document, ("version", "node_id", "principal", "state_dir", "projects_file", "profiles"),
               ("repositories", "max_concurrency", "runtime_revision"))
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("node version must be 1")
        identifier(document["node_id"])
        identifier(document["principal"])
        self.path = Path(path).expanduser().resolve() if path else None
        self.document = deepcopy(document)
        self.node_id, self.principal = document["node_id"], document["principal"]
        self.state_dir = Path(document["state_dir"]).expanduser().resolve()
        self.projects = Projects.from_file(document["projects_file"])
        self.max_concurrency = integer(document.get("max_concurrency", 2), 1, 16, "concurrency")
        self.profiles = deepcopy(document["profiles"])
        if not isinstance(self.profiles, dict) or not self.profiles:
            raise ContractError("node requires profiles")
        for name, profile in self.profiles.items():
            identifier(name)
            self._profile(profile)
        for project, repository in document.get("repositories", {}).items():
            identifier(project)
            fields(repository, ("slug", "path"))
            if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository["slug"]):
                raise ContractError("invalid repository slug")
            if not Path(repository["path"]).expanduser().is_absolute():
                raise ContractError("repository path must be absolute")
        self.revision = digest([document, self.projects.revision])

    @staticmethod
    def _profile(profile):
        fields(profile, ("argv", "isolation", "timeout_seconds", "max_output_bytes"),
               ("artifacts", "source_required", "container", "environment", "description"))
        if profile["isolation"] not in {"trusted-local", "container"}:
            raise ContractError("explicit isolation is required")
        argv = profile["argv"]
        if not isinstance(argv, list) or not 1 <= len(argv) <= 64 or any(not isinstance(x,str) or "\x00" in x for x in argv):
            raise ContractError("profile argv must be a fixed string array")
        if not os.path.isabs(argv[0]):
            raise ContractError("profile executable must be absolute")
        if Path(argv[0]).name in {"sudo", "su", "doas", "codex", "claude"}:
            raise ContractError("ordinary profiles cannot silently invoke admin/model adapters")
        integer(profile["timeout_seconds"], 1, 86400, "timeout")
        integer(profile["max_output_bytes"], 1024, 4*1024*1024, "log limit")
        if type(profile.get("source_required", False)) is not bool:
            raise ContractError("invalid source_required")
        artifacts = profile.get("artifacts", [])
        if not isinstance(artifacts, list) or len(artifacts) > 32:
            raise ContractError("at most 32 artifact names are allowed")
        for artifact in artifacts:
            if not isinstance(artifact,str) or not artifact or Path(artifact).is_absolute() or ".." in Path(artifact).parts:
                raise ContractError("artifact must be relative and confined")
        env = profile.get("environment", {})
        if not isinstance(env, dict) or any(k not in {"PATH", "LANG", "LC_ALL", "TZ"} or not isinstance(v,str) for k,v in env.items()):
            raise ContractError("environment may set only PATH/LANG/LC_ALL/TZ")
        if profile["isolation"] == "container":
            container = profile.get("container", {})
            fields(container, ("engine", "image", "cpus", "memory_mb", "pids_limit"))
            if not os.path.isabs(container["engine"]) or Path(container["engine"]).name not in {"podman", "docker"}:
                raise ContractError("explicit container engine required")
            if not re.fullmatch(r"[A-Za-z0-9./:_-]+@sha256:[0-9a-f]{64}", container["image"]):
                raise ContractError("container image must be pinned by digest")
            for key, low, high in [("cpus",1,64), ("memory_mb",64,524288), ("pids_limit",16,4096)]:
                integer(container[key], low, high, key)

    @classmethod
    def from_file(cls, path):
        return cls(load(path), path)

    def profile(self, name):
        if name not in self.profiles:
            raise ContractError("unknown process profile")
        return deepcopy(self.profiles[name])
