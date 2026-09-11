"""Operator-owned enrollment plans with drift detection and explicit application."""
from copy import deepcopy
from pathlib import Path
from operation_contracts.common import ContractError, digest, fields, load
from operation_contracts.files import atomic_json
from ..core import FleetConfig
from ..jobs.config import NodeConfig
from .releases import verify


def plan(gateway_file, alias, release_dir, node_config, python):
    gateway_file = Path(gateway_file).expanduser().resolve()
    current = load(gateway_file)
    gateway = FleetConfig.load(gateway_file)
    if alias not in gateway.hosts:
        raise ContractError("enrollment cannot create an unreviewed network destination")
    release = verify(release_dir)
    node = NodeConfig.from_file(node_config)
    if node.document.get("runtime_revision") != release["source_revision"]:
        raise ContractError("node config must be pinned to the enrolled release")
    python = Path(python)
    if not python.is_absolute() or ".." in python.parts:
        raise ContractError("operator runtime Python path must be absolute")
    binding = {"python":str(python),"entrypoint":str(Path(release["release_dir"])/"scripts/fleet_jobs.py"),
               "config":str(Path(node_config).resolve()),"node_id":node.node_id,
               "runtime_revision":release["source_revision"],"policy_revision":node.revision}
    return {"version":1,"gateway_file":str(gateway_file),"gateway_before":digest(current),
            "host":alias,"runtime":binding,"project_ids":[p["project_id"] for p in node.projects.list(node.principal)],
            "release_digest":release["tree_digest"],"live_probe":"NOT_RUN","services_reloaded":False}


def apply(plan_document):
    fields(plan_document, ("version","gateway_file","gateway_before","host","runtime","project_ids",
                           "release_digest","live_probe","services_reloaded"))
    current = load(plan_document["gateway_file"])
    if digest(current) != plan_document["gateway_before"]:
        raise ContractError("gateway configuration changed since enrollment planning")
    if plan_document["host"] not in current["hosts"]:
        raise ContractError("host is no longer configured")
    # Recheck every binding and release hash, rather than trusting an editable plan file.
    runtime = plan_document["runtime"]
    checked = plan(plan_document["gateway_file"],plan_document["host"],
                   str(Path(runtime["entrypoint"]).parents[1]),runtime["config"],runtime["python"])
    if checked != plan_document:
        raise ContractError("enrollment plan differs from current validated bindings")
    result = deepcopy(current)
    result["hosts"][plan_document["host"]]["runtime"] = runtime
    atomic_json(plan_document["gateway_file"],result)
    return {"enrolled":plan_document["host"],"gateway_after":digest(result),"services_reloaded":False,
            "live_probe":"NOT_RUN"}
