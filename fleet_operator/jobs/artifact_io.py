"""Bounded artifact delivery, tied to a durable receipt rather than arbitrary paths."""
import base64
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath
from operation_contracts.common import ContractError, digest, integer
from operation_contracts.files import private_json

MAX_ARTIFACT = 16 * 1024 * 1024


def read_verified_file(work, name, offset=0, limit=65536):
    """Read through no-follow descriptors; hash the whole bounded regular file."""
    if (not isinstance(name, str) or not name or PurePosixPath(name).is_absolute()
            or any(part in {'', '.', '..'} for part in name.split('/'))):
        raise ContractError('invalid artifact name')
    integer(offset, 0, MAX_ARTIFACT, 'offset')
    integer(limit, 1, 65536, 'limit')
    directory = os.open(work, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = name.split('/')
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    finally:
        os.close(directory)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ContractError('artifact must be a regular file with no hard links')
        if before.st_size > MAX_ARTIFACT or offset > before.st_size:
            raise ContractError('artifact size or offset exceeds limit')
        sha, total, selected = hashlib.sha256(), 0, bytearray()
        while True:
            raw = os.read(fd, 65536)
            if not raw:
                break
            if total + len(raw) > MAX_ARTIFACT:
                raise ContractError('artifact exceeds limit while reading')
            sha.update(raw)
            left, right = max(offset, total), min(offset + limit, total + len(raw))
            if left < right:
                selected.extend(raw[left-total:right-total])
            total += len(raw)
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or total != before.st_size:
            raise ContractError('artifact changed while reading')
        return {'name': name, 'size': total, 'sha256': sha.hexdigest()}, bytes(selected)
    finally:
        os.close(fd)


def manifest(profile, work):
    found = []
    for name in profile.get('artifacts', []):
        try:
            item, _ = read_verified_file(work, name)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ContractError('artifact path is unavailable or contains a link') from exc
        found.append(item)
    return found


def artifact(service, project, run_id, name, offset=0, limit=65536):
    from .workspace import root_for
    row = service.row(project, run_id)
    result = service.result(project, run_id)
    if not result['receipt_digest']:
        raise ContractError('no verified completion receipt for this artifact')
    root = root_for(service.config, run_id)
    try:
        receipt = private_json(root / 'result.json')
        if (digest(receipt) != result['receipt_digest']
                or receipt.get('run_id') != run_id or receipt.get('request_digest') != row['digest']
                or receipt.get('policy') != row['policy'] or receipt.get('token') != row['data'].get('token')
                or receipt.get('state') != row['state']):
            raise ContractError('completion receipt does not match this execution')
        if receipt.get('artifacts') != result['artifacts']:
            raise ContractError('artifact manifest differs from completion receipt')
        expected = next((item for item in receipt['artifacts'] if item['name'] == name), None)
        if expected is None:
            raise ContractError('artifact is not in the completion manifest')
        observed, raw = read_verified_file(root / 'workspace', name, offset, limit)
        if observed != expected:
            raise ContractError('artifact differs from recorded size or hash')
    except OSError as exc:
        raise ContractError('recorded artifact or receipt is unavailable') from exc
    return {'run_id': run_id, **observed, 'offset': offset, 'next_offset': offset + len(raw),
            'eof': offset + len(raw) == observed['size'], 'encoding': 'base64',
            'data_base64': base64.b64encode(raw).decode('ascii'),
            'data': base64.b64encode(raw).decode('ascii'),
            'chunk_sha256': hashlib.sha256(raw).hexdigest(), 'verified': True}


# Preserve both published API names without bypassing receipt verification.
read_artifact = artifact
