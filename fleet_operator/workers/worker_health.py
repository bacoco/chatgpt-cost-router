"""Durable local health/quarantine state for model workers.

A cheap login-status probe can be stale or optimistic. Actual execution failures
that clearly indicate broken authentication quarantine the worker until an
operator explicitly clears it after re-authentication.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Callable, Mapping


DEFAULT_HEALTH_STATE = "~/.local/state/chatgpt-cost-router/worker-health.json"
AUTH_ERROR_PATTERNS = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"refresh[_ ]token[_ ]reused",
    r"refresh token has already been used",
    r"access token could not be refreshed",
    r"could not parse your authentication token",
    r"\b401\s+unauthorized\b",
    r"auth error:\s*401",
    r"please log out and sign in again",
))


def health_path(path: str | os.PathLike[str] | None = None) -> Path:
    return Path(path or DEFAULT_HEALTH_STATE).expanduser()


def _load(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "workers": {}}
    data = json.loads(path.read_text())
    if data.get("version") != 1 or not isinstance(data.get("workers"), dict):
        raise ValueError("invalid worker health state")
    return data


def _save(path: Path, data: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(data), indent=2, sort_keys=True) + "\n")
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    os.chmod(path, 0o600)


def auth_failure_reason(text: str) -> str | None:
    for pattern in AUTH_ERROR_PATTERNS:
        if pattern.search(text or ""):
            return "auth_failure"
    return None


def quarantine(worker_id: str, *, path: str | os.PathLike[str] | None = None,
               reason: str = "auth_failure", clock: Callable[[], float] = time.time) -> dict:
    p = health_path(path)
    data = _load(p)
    record = {"status": "quarantined", "reason": reason, "since_unix": float(clock())}
    data["workers"][worker_id] = record
    _save(p, data)
    return record


def clear(worker_id: str, *, path: str | os.PathLike[str] | None = None) -> bool:
    p = health_path(path)
    data = _load(p)
    existed = worker_id in data["workers"]
    if existed:
        data["workers"].pop(worker_id, None)
        _save(p, data)
    return existed


def status(worker_id: str, *, path: str | os.PathLike[str] | None = None) -> dict | None:
    return _load(health_path(path))["workers"].get(worker_id)
