"""Reentrant, cross-thread and cross-process local operation serialization (POSIX)."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import threading
import weakref
from .common import ContractError

_mutex = threading.Lock()
_locks = weakref.WeakValueDictionary()
_local = threading.local()


@contextmanager
def file_lock(path, *, blocking=True):
    key = str(Path(path).absolute())
    with _mutex:
        lock = _locks.get(key)
        if lock is None:
            lock = threading.RLock()
            _locks[key] = lock
    if not lock.acquire(blocking=blocking):
        raise ContractError("operation is already owned")
    depths = getattr(_local, "depths", None)
    if depths is None:
        depths = _local.depths = {}
    fd = None
    try:
        if key not in depths:
            Path(key).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(key, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            except BlockingIOError as exc:
                raise ContractError("operation is already owned") from exc
        depths[key] = depths.get(key, 0) + 1
        try:
            yield
        finally:
            depths[key] -= 1
            if not depths[key]:
                del depths[key]
    finally:
        if fd is not None:
            os.close(fd)
        lock.release()
