"""Atomic private local records, separate from GitHub delivery receipts."""
import os
import tempfile
from pathlib import Path
from .common import canonical, loads, ContractError


def atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(canonical(payload)+"\n")
            out.flush()
            os.fsync(out.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
        dirfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def private_json(path):
    fd = os.open(Path(path), os.O_RDONLY | os.O_NOFOLLOW)
    try:
        data = os.read(fd, 1_048_577)
        if len(data) > 1_048_576:
            raise ContractError("record exceeds limit")
        return loads(data.decode("utf-8"))
    finally:
        os.close(fd)
