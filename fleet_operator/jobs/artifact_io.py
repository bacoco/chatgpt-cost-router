"""Read only receipt-listed artifacts, with confined paths and per-chunk integrity."""
import base64
import hashlib
import os
import stat
from operation_contracts.common import ContractError, integer
from .workspace import root_for


def read_artifact(service, project, id_, name, offset=0, limit=65536):
    result = service.result(project, id_)
    item = next((v for v in result["artifacts"] if v["name"] == name), None)
    if item is None:
        raise ContractError("artifact is not in the verified result manifest")
    integer(offset, 0, item["size"], "artifact offset")
    integer(limit, 1, 131072, "artifact limit")
    base = root_for(service.config, id_) / "workspace"
    fd = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = name.split("/")
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        file = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            if not stat.S_ISREG(os.fstat(file).st_mode):
                raise ContractError("artifact is no longer a regular file")
            raw = bytearray()
            while len(raw) <= 16*1024*1024:
                chunk = os.read(file, 65536)
                if not chunk:
                    break
                raw.extend(chunk)
            if len(raw) != item["size"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ContractError("artifact changed since its receipt")
            chunk = bytes(raw[offset:offset+limit])
        finally:
            os.close(file)
    finally:
        os.close(fd)
    return {"run_id":id_, **item, "offset":offset,"next_offset":offset+len(chunk),
            "eof":offset+len(chunk) == item["size"], "encoding":"base64",
            "data":base64.b64encode(chunk).decode(), "chunk_sha256":hashlib.sha256(chunk).hexdigest()}
