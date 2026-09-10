"""Private Tailscale-facing adapter for the local Codex worker broker.

The HTTP layer must sit behind Tailscale Serve and listen only on loopback.
No raw shell, arbitrary workspace path, credential, or CODEX_HOME is exposed.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .worker_budget import WorkerBudget, load_budget_state, select_economic_worker
from .workers import Worker, WorkerError, load_registry, probe, run_task, select_worker


class RemoteWorkerError(ValueError):
    """Safe, client-displayable remote worker request error."""


@dataclass(frozen=True)
class RemotePolicy:
    allowed_users: frozenset[str]
    allowed_workers: frozenset[str]
    workspace_root: Path
    max_prompt_chars: int = 12_000
    max_body_bytes: int = 64 * 1024

    def __post_init__(self):
        if not self.allowed_users:
            raise RemoteWorkerError("at least one Tailscale user must be allowed")
        if not self.allowed_workers:
            raise RemoteWorkerError("at least one worker must be allowed")
        if self.max_prompt_chars < 1 or self.max_body_bytes < 128:
            raise RemoteWorkerError("invalid request limits")


def _split_env(name: str) -> frozenset[str]:
    return frozenset(part.strip().lower() for part in os.environ.get(name, "").split(",") if part.strip())


def policy_from_env() -> RemotePolicy:
    """Load non-secret authorization policy from environment variables."""
    root = Path(os.environ.get("COST_ROUTER_REMOTE_WORKSPACE_ROOT", "~/codex-remote-worker-tasks")).expanduser()
    return RemotePolicy(
        allowed_users=_split_env("COST_ROUTER_ALLOWED_TAILSCALE_USERS"),
        allowed_workers=frozenset(
            part.strip() for part in os.environ.get("COST_ROUTER_REMOTE_WORKERS", "").split(",") if part.strip()
        ),
        workspace_root=root,
    )


def tailscale_identity(headers: Mapping[str, str], policy: RemotePolicy) -> str:
    """Authorize a Tailscale Serve identity header against the local allowlist."""
    login = (headers.get("Tailscale-User-Login") or headers.get("tailscale-user-login") or "").strip().lower()
    if not login:
        raise RemoteWorkerError("missing Tailscale identity; access through Tailscale Serve is required")
    if login not in policy.allowed_users:
        raise RemoteWorkerError("Tailscale user is not authorized")
    return login


def _allowed_workers(all_workers: Iterable[Worker], policy: RemotePolicy) -> list[Worker]:
    all_workers = list(all_workers)
    workers = [w for w in all_workers if w.id in policy.allowed_workers]
    unknown = sorted(policy.allowed_workers - {w.id for w in all_workers})
    if unknown:
        raise RemoteWorkerError(f"policy references unknown worker(s): {', '.join(unknown)}")
    if not workers:
        raise RemoteWorkerError("no worker is available to this remote endpoint")
    return workers


def parse_request_body(raw: bytes, policy: RemotePolicy) -> dict:
    if len(raw) > policy.max_body_bytes:
        raise RemoteWorkerError("request body is too large")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RemoteWorkerError("request body must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise RemoteWorkerError("request body must be a JSON object")
    unknown = set(payload) - {"worker", "prompt"}
    if unknown:
        raise RemoteWorkerError(f"unknown request field(s): {', '.join(sorted(unknown))}")
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise RemoteWorkerError("prompt must be a non-empty string")
    if len(prompt) > policy.max_prompt_chars:
        raise RemoteWorkerError("prompt is too long")
    worker = payload.get("worker", "auto")
    if not isinstance(worker, str) or not worker:
        raise RemoteWorkerError("worker must be a string")
    return {"worker": worker, "prompt": prompt}


def list_remote_workers(*, policy: RemotePolicy, registry_path: str, codex_bin: str = "codex", run=None) -> list[dict]:
    workers = _allowed_workers(load_registry(registry_path), policy)
    result = []
    for worker in workers:
        kwargs = {"codex_bin": codex_bin}
        if run is not None:
            kwargs["run"] = run
        state = probe(worker, **kwargs)
        result.append({"worker": worker.id, "ready": state["ready"], "auth": state["auth"]})
    return result


def dispatch_remote(payload: Mapping[str, str], *, policy: RemotePolicy, registry_path: str,
                    budget_state_path: str | None = None, codex_bin: str = "codex", run=None, clock=None) -> dict:
    """Dispatch one bounded remote prompt to one locally isolated worker."""
    workers = _allowed_workers(load_registry(registry_path), policy)
    requested = payload["worker"]
    if requested != "auto" and requested not in policy.allowed_workers:
        raise RemoteWorkerError("requested worker is not authorized for remote use")

    select_kwargs = {"codex_bin": codex_bin}
    if run is not None:
        select_kwargs["run"] = run
    if budget_state_path:
        budgets = load_budget_state(budget_state_path)
        worker, probes = select_economic_worker(workers, budgets, requested, **select_kwargs)
    else:
        worker, probes = select_worker(workers, requested, **select_kwargs)

    root = policy.workspace_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="task-", dir=root) as folder:
        task_kwargs = {"codex_bin": codex_bin}
        if run is not None:
            task_kwargs["run"] = run
        if clock is not None:
            task_kwargs["clock"] = clock
        result = run_task(worker, payload["prompt"], folder, **task_kwargs)

    return {
        "worker": result["worker"],
        "provider": result["provider"],
        "model": result["model"],
        "tokens_reported": result["tokens_reported"],
        "elapsed_seconds": result["elapsed_seconds"],
        "exit_code": result["exit_code"],
        "output": result["stdout"],
        "sandbox": result["sandbox"],
        "ephemeral": result["ephemeral"],
        "paid_api_env_removed": result["paid_api_env_removed"],
        "selection_probes": [
            {"worker": item["worker"], "ready": item["ready"], **({"budget": item["budget"]} if "budget" in item else {})}
            for item in probes
        ],
    }
