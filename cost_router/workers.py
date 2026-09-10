"""Small, safe worker registry and Codex CLI dispatcher."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Union


class WorkerError(ValueError):
    """Raised when a worker registry or invocation is invalid."""


@dataclass(frozen=True)
class Worker:
    id: str
    provider: str
    adapter: str
    codex_home: str
    cost_class: str = "included"
    priority: int = 100
    enabled: bool = True


COST_ORDER = {
    "included": 0,
    "external-free-tier": 1,
    "paid-credit": 2,
    "paid-api": 3,
    "compute-cost": 4,
}
PAID_API_ENV = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GOOGLE_API_KEY",
}
TOKENS_RE = re.compile(r"tokens used\s+([0-9\s,._\u202f\u00a0]+)", re.IGNORECASE)
MODEL_RE = re.compile(r"^model:\s*(\S+)", re.MULTILINE)
PROVIDER_RE = re.compile(r"^provider:\s*(\S+)", re.MULTILINE)

Run = Callable[..., subprocess.CompletedProcess]


def load_registry(path: Union[str, os.PathLike]) -> list[Worker]:
    data = json.loads(Path(path).expanduser().read_text())
    if data.get("version") != 1 or not isinstance(data.get("workers"), list):
        raise WorkerError("worker registry must have version=1 and a workers array")
    workers = []
    seen = set()
    for item in data["workers"]:
        try:
            worker = Worker(
                id=item["id"],
                provider=item["provider"],
                adapter=item["adapter"],
                codex_home=item["codex_home"],
                cost_class=item.get("cost_class", "included"),
                priority=int(item.get("priority", 100)),
                enabled=bool(item.get("enabled", True)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WorkerError(f"invalid worker descriptor: {exc}") from exc
        if not worker.id or worker.id in seen:
            raise WorkerError(f"duplicate or empty worker id: {worker.id!r}")
        if worker.adapter != "codex-exec":
            raise WorkerError(f"unsupported adapter for {worker.id}: {worker.adapter}")
        if worker.cost_class not in COST_ORDER:
            raise WorkerError(f"unknown cost_class for {worker.id}: {worker.cost_class}")
        if worker.cost_class == "paid-api":
            raise WorkerError(f"paid-api worker is forbidden in this prototype: {worker.id}")
        seen.add(worker.id)
        workers.append(worker)
    if not workers:
        raise WorkerError("worker registry is empty")
    return workers


def _worker_env(worker: Worker) -> dict[str, str]:
    env = os.environ.copy()
    for key in PAID_API_ENV:
        env.pop(key, None)
    env["CODEX_HOME"] = str(Path(worker.codex_home).expanduser())
    return env


def probe(worker: Worker, *, run: Run = subprocess.run, codex_bin: str = "codex") -> dict:
    if not worker.enabled:
        return {"worker": worker.id, "ready": False, "reason": "disabled"}
    result = run(
        [codex_bin, "login", "status"],
        capture_output=True,
        text=True,
        env=_worker_env(worker),
    )
    text = (result.stdout or "") + (result.stderr or "")
    ready = result.returncode == 0 and "Logged in using ChatGPT" in text
    return {
        "worker": worker.id,
        "ready": ready,
        "auth": "chatgpt" if ready else "unavailable",
        "exit_code": result.returncode,
    }


def _rank(worker: Worker) -> tuple[int, int, str]:
    return (COST_ORDER[worker.cost_class], worker.priority, worker.id)


def select_worker(
    workers: Iterable[Worker],
    requested: str = "auto",
    *,
    run: Run = subprocess.run,
    codex_bin: str = "codex",
) -> tuple[Worker, list[dict]]:
    candidates = list(workers)
    if requested != "auto":
        candidates = [worker for worker in candidates if worker.id == requested]
        if not candidates:
            raise WorkerError(f"unknown worker: {requested}")
    candidates = sorted((w for w in candidates if w.enabled), key=_rank)
    probes = []
    for worker in candidates:
        status = probe(worker, run=run, codex_bin=codex_bin)
        probes.append(status)
        if status["ready"]:
            return worker, probes
    raise WorkerError(f"no ready worker; probes={probes}")


def _parse_tokens(text: str) -> int | None:
    match = TOKENS_RE.search(text)
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(1))
    return int(digits) if digits else None


def run_task(
    worker: Worker,
    prompt: str,
    workspace: Union[str, os.PathLike],
    *,
    run: Run = subprocess.run,
    codex_bin: str = "codex",
    clock: Callable[[], float] = time.monotonic,
    ignore_user_config: bool = False,
) -> dict:
    if not prompt.strip():
        raise WorkerError("prompt must not be empty")
    root = Path(workspace).expanduser().resolve()
    if not root.is_dir():
        raise WorkerError(f"workspace does not exist: {root}")
    command = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
    ]
    if ignore_user_config:
        command.append("--ignore-user-config")
    command += [
        "-C",
        str(root),
        prompt,
    ]
    start = clock()
    result = run(command, capture_output=True, text=True, env=_worker_env(worker))
    elapsed = max(0.0, clock() - start)
    combined = (result.stderr or "") + "\n" + (result.stdout or "")
    model = MODEL_RE.search(combined)
    provider = PROVIDER_RE.search(combined)
    return {
        "worker": worker.id,
        "provider": provider.group(1) if provider else worker.provider,
        "model": model.group(1) if model else None,
        "tokens_reported": _parse_tokens(combined),
        "elapsed_seconds": round(elapsed, 3),
        "exit_code": result.returncode,
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
        "paid_api_env_removed": True,
        "sandbox": "read-only",
        "ephemeral": True,
    }
