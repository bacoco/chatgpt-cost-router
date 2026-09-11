"""Immutable snapshots and per-run directories; never switch the user's checkout."""
import hashlib
import io
import os
import posixpath
import subprocess
import tarfile
from pathlib import Path
from operation_contracts.common import ContractError, canonical


def root_for(config, id_):
    if len(id_) != 32 or any(char not in "0123456789abcdef" for char in id_):
        raise ContractError("invalid run id")
    base = config.state_dir / "runs"
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    return base / id_


def _slug(url):
    for prefix in ("https://github.com/", "git@github.com:", "ssh://git@github.com/"):
        if url.startswith(prefix):
            path = url[len(prefix):].rstrip("/")
            return path[:-4] if path.endswith(".git") else path
    return None


def extract_snapshot(raw, destination):
    destination = Path(destination).resolve()
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        members, total, links = archive.getmembers(), 0, []
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not path.parts:
                raise ContractError("unsafe archive path")
            if not (member.isdir() or member.isfile() or member.issym()):
                raise ContractError("unsupported archive member")
            total += member.size
            if total > 256*1024*1024 or len(members) > 100000:
                raise ContractError("source snapshot too large")
            if member.issym():
                target = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), member.linkname))
                if member.linkname.startswith("/") or target == ".." or target.startswith("../"):
                    raise ContractError("archive link escapes workspace")
                links.append(member)
        for member in members:
            if member.issym():
                continue
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
                continue
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with archive.extractfile(member) as source, target.open("xb") as out:
                while True:
                    chunk = source.read(65536)
                    if not chunk:
                        break
                    out.write(chunk)
            target.chmod(0o700 if member.mode & 0o111 else 0o600)
        for member in links:
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            resolved = (target.parent / member.linkname).resolve()
            if resolved != destination and destination not in resolved.parents:
                raise ContractError("link chain escapes snapshot")
            target.symlink_to(member.linkname)


def prepare(config, row):
    root = root_for(config, row["id"])
    root.mkdir(mode=0o700)
    work, home = root / "workspace", root / "home"
    work.mkdir(mode=0o700)
    home.mkdir(mode=0o700)
    request = row["request"]
    if "source" in request:
        repository = config.document["repositories"][row["project"]]
        source = Path(repository["path"]).expanduser().resolve()
        origin = subprocess.check_output(["git","-C",str(source),"remote","get-url","origin"], text=True, timeout=15).strip()
        if _slug(origin) != repository["slug"]:
            raise ContractError("local repository origin differs from project binding")
        sha = request["source"]["sha"]
        observed = subprocess.check_output(["git","-C",str(source),"rev-parse","--verify",sha+"^{commit}"], text=True, timeout=15).strip()
        if observed != sha:
            raise ContractError("immutable source object not found")
        raw = subprocess.check_output(["git","-C",str(source),"archive","--format=tar",sha], timeout=60)
        if len(raw) > 256*1024*1024:
            raise ContractError("source archive exceeds limit")
        extract_snapshot(raw, work)
    metadata = work / ".fleet-runtime"
    metadata.mkdir(mode=0o700)
    inputs = metadata / "input.json"
    inputs.write_text(canonical(request["inputs"]), encoding="utf-8")
    inputs.chmod(0o600)
    return root, work, home


def artifacts(profile, work):
    found, root = [], work.resolve()
    for name in profile.get("artifacts", []):
        path = work / name
        if not path.exists():
            continue
        if path.is_symlink() or root not in path.resolve().parents or not path.is_file():
            raise ContractError("artifact escapes workspace or is not regular")
        size = path.stat().st_size
        if size > 16*1024*1024:
            raise ContractError("artifact exceeds 16 MiB")
        found.append({"name":name, "size":size, "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    return found
