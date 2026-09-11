"""Stage exact Git snapshots and switch an idle node's versioned runtime explicitly."""
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from operation_contracts.common import ContractError, SHA, digest, fields, load
from operation_contracts.files import atomic_json, private_json
from ..jobs.config import NodeConfig
from ..jobs.service import Jobs
from ..jobs.workspace import extract_snapshot

ROOTS = {"chat_ops", "fleet_operator", "operation_contracts", "cost_router", "scripts", "schemas", "policy"}
FILES = {"requirements.txt", "requirements-fleet-operator.txt", "pyproject.toml", "setup.py", "MANIFEST.in"}


def inventory(path):
    found = {}
    for file in sorted(Path(path).rglob("*")):
        if file.is_symlink():
            raise ContractError("runtime releases cannot contain symlinks")
        if not file.is_file() or file.name == "release-manifest.json" or "__pycache__" in file.parts:
            continue
        if file.stat().st_size > 4*1024*1024:
            raise ContractError("runtime member exceeds 4 MiB")
        found[file.relative_to(path).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return found


def stage(repo, root, revision):
    if not isinstance(revision, str) or not SHA.fullmatch(revision):
        raise ContractError("runtime source must be an exact Git commit SHA")
    repo, root = Path(repo).resolve(), Path(root).resolve()
    observed = subprocess.check_output(["git", "-C", str(repo), "rev-parse", revision+"^{commit}"], timeout=15, text=True).strip()
    if observed != revision:
        raise ContractError("runtime source commit not available locally")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = root / "releases" / revision
    if target.exists():
        return verify(target)
    raw = subprocess.check_output(["git", "-C", str(repo), "archive", "--format=tar", revision], timeout=60)
    if len(raw) > 256*1024*1024:
        raise ContractError("runtime source exceeds archive limit")
    target.parent.mkdir(exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(dir=root) as temp:
        source, output = Path(temp)/"source", Path(temp)/"runtime"
        source.mkdir(mode=0o700)
        output.mkdir(mode=0o700)
        extract_snapshot(raw, source)
        for name in ROOTS | FILES:
            item = source / name
            if item.is_symlink():
                raise ContractError("runtime root cannot be a symlink")
            if item.is_dir():
                shutil.copytree(item, output/name, symlinks=True)
            elif item.is_file():
                shutil.copy2(item, output/name)
        if not (output / "scripts/fleet_jobs.py").is_file() or not (output / "fleet_operator/jobs/service.py").is_file():
            raise ContractError("source commit does not contain the Fleet Jobs runtime")
        members = inventory(output)
        manifest = {"version":1,"source_revision":revision,"files":members,"tree_digest":digest(members)}
        atomic_json(output / "release-manifest.json", manifest)
        output.rename(target)
    return verify(target)


def verify(path):
    path = Path(path).resolve()
    manifest = private_json(path / "release-manifest.json")
    fields(manifest, ("version", "source_revision", "files", "tree_digest"))
    if type(manifest["version"]) is not int or manifest["version"] != 1 or not SHA.fullmatch(manifest["source_revision"]):
        raise ContractError("unsupported runtime manifest")
    if path.name != manifest["source_revision"]:
        raise ContractError("release directory differs from its source revision")
    actual = inventory(path)
    if actual != manifest["files"] or digest(actual) != manifest["tree_digest"]:
        raise ContractError("runtime release integrity mismatch")
    return {"release_dir":str(path), **manifest}


def activation(root, revision, node_config, python, *, apply=False):
    if not isinstance(revision, str) or not SHA.fullmatch(revision):
        raise ContractError("invalid activation revision")
    root = Path(root).resolve()
    release = verify(root / "releases" / revision)
    # Preserve a virtualenv interpreter path: resolving its symlink discards the venv.
    executable = Path(python).expanduser().absolute()
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ContractError("operator Python executable is unavailable")
    config = NodeConfig.from_file(node_config)
    service = Jobs(config)
    with service.journal.transaction() as db:
        busy = db.execute("SELECT COUNT(*) FROM operations WHERE kind='process' AND state IN ('QUEUED','RUNNING','CANCELLING','UNCERTAIN')").fetchone()[0]
        if busy:
            raise ContractError("node must be idle with no uncertain jobs before activation or rollback")
        active = root / "active.json"
        previous = private_json(active).get("revision") if active.exists() else None
        record = {"version":1, "revision":revision, "node_config":str(Path(node_config).resolve()),
                  "python":str(executable), "previous":previous}
        if apply:
            # Serialize with submissions/claims sharing the node journal during the atomic switch.
            atomic_json(active, record)
    return {"applied":apply, "active_file":str(active), "record":record,
            "release_digest":release["tree_digest"], "services_reloaded":False,
            "notice":"running service reload and gateway binding update remain explicit operator actions"}


def prepare_active(active_file):
    """Resolve and verify an activation; produce a pinned config without executing a job."""
    path = Path(active_file).resolve()
    record = private_json(path)
    fields(record, ("version", "revision", "node_config", "python", "previous"))
    if type(record["version"]) is not int or record["version"] != 1:
        raise ContractError("unsupported activation record")
    if not isinstance(record["revision"], str) or not SHA.fullmatch(record["revision"]):
        raise ContractError("invalid active revision")
    release = verify(path.parent / "releases" / record["revision"])
    document = load(record["node_config"])
    document["runtime_revision"] = record["revision"]
    NodeConfig(document)
    pinned = path.parent / "configs" / (digest(document)+".json")
    if pinned.exists():
        if private_json(pinned) != document:
            raise ContractError("pinned node configuration changed")
    else:
        atomic_json(pinned, document)
    return [record["python"], str(Path(release["release_dir"])/"scripts/fleet_jobs.py"), "--config", str(pinned)]
