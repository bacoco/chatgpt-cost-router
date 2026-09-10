"""Private Tailscale worker-mesh registry and cross-node dispatcher."""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Union
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .worker_budget import WorkerBudget, budget_summary, load_budget_state
from .workers import COST_ORDER, load_registry, probe


class MeshError(ValueError):
    """Safe mesh configuration/dispatch error."""


NODE_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
WORKER_RE = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
VALID_AUTH = {"chatgpt", "unavailable"}


@dataclass(frozen=True)
class MeshPolicy:
    allowed_users: frozenset[str]
    ttl_seconds: int = 120
    max_body_bytes: int = 64 * 1024
    max_prompt_chars: int = 12_000

    def __post_init__(self):
        if not self.allowed_users:
            raise MeshError("at least one Tailscale user must be allowed")
        if self.ttl_seconds < 15:
            raise MeshError("ttl_seconds must be >= 15")


def _split_env(name: str) -> frozenset[str]:
    return frozenset(x.strip().lower() for x in os.environ.get(name, "").split(",") if x.strip())


def policy_from_env() -> MeshPolicy:
    ttl = int(os.environ.get("COST_ROUTER_MESH_TTL_SECONDS", "120"))
    return MeshPolicy(_split_env("COST_ROUTER_MESH_ALLOWED_USERS"), ttl_seconds=ttl)


def tailscale_identity(headers: Mapping[str, str], policy: MeshPolicy) -> str:
    login = (headers.get("Tailscale-User-Login") or headers.get("tailscale-user-login") or "").strip().lower()
    if not login:
        raise MeshError("missing Tailscale identity; use Tailscale Serve")
    if login not in policy.allowed_users:
        raise MeshError("Tailscale user is not authorized for this mesh")
    return login


def validate_endpoint(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise MeshError("node endpoint must be an https Tailscale Serve URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise MeshError("node endpoint must not contain credentials, query, or fragment")
    host = parsed.hostname.rstrip(".").lower()
    if not host.endswith(".ts.net"):
        raise MeshError("node endpoint host must end in .ts.net")
    if parsed.path not in {"", "/"}:
        raise MeshError("node endpoint must be a base URL without a path")
    try:
        port = parsed.port
    except ValueError as exc:
        raise MeshError("invalid node endpoint port") from exc
    if port is not None and not (1 <= port <= 65535):
        raise MeshError("invalid node endpoint port")
    authority = host if port is None else f"{host}:{port}"
    return f"https://{authority}"


def _validate_worker(item: Mapping) -> dict:
    worker = item.get("worker")
    if not isinstance(worker, str) or not WORKER_RE.fullmatch(worker):
        raise MeshError("invalid worker id in node advertisement")
    provider = item.get("provider")
    if not isinstance(provider, str) or not provider or len(provider) > 32:
        raise MeshError("invalid provider in node advertisement")
    cost_class = item.get("cost_class", "included")
    if cost_class not in COST_ORDER or cost_class == "paid-api":
        raise MeshError("invalid or forbidden worker cost_class")
    priority = int(item.get("priority", 100))
    ready = bool(item.get("ready", False))
    auth = item.get("auth", "unavailable")
    if auth not in VALID_AUTH:
        raise MeshError("invalid worker auth state")
    budget = item.get("budget")
    if budget is not None and not isinstance(budget, dict):
        raise MeshError("worker budget must be an object")
    return {"worker": worker, "provider": provider, "cost_class": cost_class,
            "priority": priority, "ready": ready, "auth": auth, "budget": budget}


def validate_registration(payload: Mapping) -> dict:
    if not isinstance(payload, Mapping):
        raise MeshError("registration must be an object")
    unknown = set(payload) - {"version", "node_id", "endpoint", "workers", "location"}
    if unknown:
        raise MeshError(f"unknown registration field(s): {', '.join(sorted(unknown))}")
    if payload.get("version") != 1:
        raise MeshError("registration version must be 1")
    node_id = payload.get("node_id")
    if not isinstance(node_id, str) or not NODE_RE.fullmatch(node_id):
        raise MeshError("invalid node_id")
    workers = payload.get("workers")
    if not isinstance(workers, list) or not workers:
        raise MeshError("registration workers must be a non-empty array")
    normalized = [_validate_worker(w) for w in workers]
    if len({w["worker"] for w in normalized}) != len(normalized):
        raise MeshError("duplicate worker id in node advertisement")
    location = payload.get("location", "remote")
    if location not in {"local", "remote", "cloud"}:
        raise MeshError("invalid node location")
    return {"version": 1, "node_id": node_id,
            "endpoint": validate_endpoint(payload.get("endpoint", "")),
            "location": location, "workers": normalized}


class NodeRegistry:
    """Small durable runtime registry. No credentials are stored."""

    def __init__(self, path: Union[str, Path], policy: MeshPolicy,
                 *, clock: Callable[[], float] = time.time):
        self.path = Path(path).expanduser()
        self.policy = policy
        self.clock = clock

    def _load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "nodes": {}}
        data = json.loads(self.path.read_text())
        if data.get("version") != 1 or not isinstance(data.get("nodes"), dict):
            raise MeshError("invalid mesh registry file")
        return data

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)

    def register(self, payload: Mapping, owner: str) -> dict:
        node = validate_registration(payload)
        data = self._load()
        owner_hash = hashlib.sha256(owner.encode("utf-8")).hexdigest()
        old = data["nodes"].get(node["node_id"])
        if old and old.get("owner_hash") != owner_hash:
            raise MeshError("node_id is already owned by another Tailscale identity")
        record = {**node, "owner_hash": owner_hash, "last_seen": float(self.clock())}
        data["nodes"][node["node_id"]] = record
        self._save(data)
        return self.public_node(record)

    def live_nodes(self) -> list[dict]:
        now = float(self.clock())
        nodes = []
        for record in self._load()["nodes"].values():
            age = max(0.0, now - float(record.get("last_seen", 0)))
            if age <= self.policy.ttl_seconds:
                item = self.public_node(record)
                item["age_seconds"] = round(age, 3)
                nodes.append(item)
        return sorted(nodes, key=lambda x: x["node_id"])

    @staticmethod
    def public_node(record: Mapping) -> dict:
        return {"node_id": record["node_id"], "endpoint": record["endpoint"],
                "location": record.get("location", "remote"),
                "workers": record["workers"], "last_seen": record["last_seen"]}

    def workers(self) -> list[dict]:
        result = []
        for node in self.live_nodes():
            for worker in node["workers"]:
                result.append({"mesh_worker": f'{node["node_id"]}/{worker["worker"]}',
                               "node_id": node["node_id"], **worker})
        return result

    @staticmethod
    def _headroom(worker: Mapping) -> tuple[int, float]:
        budget = worker.get("budget") or {}
        values = [budget.get("five_hour_remaining_pct"), budget.get("weekly_remaining_pct")]
        values = [float(v) for v in values if v is not None]
        return (0, min(values)) if values else (1, -1.0)

    def resolve(self, requested: str = "auto") -> dict:
        workers = [w for w in self.workers() if w.get("ready") and w.get("auth") == "chatgpt"]
        if requested != "auto":
            if "/" in requested:
                workers = [w for w in workers if w["mesh_worker"] == requested]
            else:
                matches = [w for w in workers if w["worker"] == requested]
                if len(matches) > 1:
                    raise MeshError(f"worker alias is ambiguous across nodes: {requested}; use node/worker")
                workers = matches
        if not workers:
            raise MeshError(f"no live ready worker matches: {requested}")
        workers.sort(key=lambda w: (COST_ORDER[w["cost_class"]],
                                    self._headroom(w)[0], -self._headroom(w)[1],
                                    int(w.get("priority", 100)), w["node_id"], w["worker"]))
        return workers[0]


def parse_json_body(raw: bytes, policy: MeshPolicy) -> dict:
    if len(raw) > policy.max_body_bytes:
        raise MeshError("request body is too large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MeshError("request body must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise MeshError("request body must be a JSON object")
    return value


def default_http_post(url: str, payload: Mapping, timeout: int = 300) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def dispatch_mesh(registry: NodeRegistry, payload: Mapping, *, http_post=default_http_post) -> dict:
    unknown = set(payload) - {"worker", "prompt"}
    if unknown:
        raise MeshError(f"unknown run field(s): {', '.join(sorted(unknown))}")
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise MeshError("prompt must be a non-empty string")
    if len(prompt) > registry.policy.max_prompt_chars:
        raise MeshError("prompt is too long")
    requested = payload.get("worker", "auto")
    if not isinstance(requested, str) or not requested:
        raise MeshError("worker must be a string")
    selected = registry.resolve(requested)
    node = next(n for n in registry.live_nodes() if n["node_id"] == selected["node_id"])
    result = http_post(node["endpoint"] + "/v1/run",
                       {"worker": selected["worker"], "prompt": prompt})
    return {"mesh_worker": selected["mesh_worker"], "node_id": selected["node_id"],
            "node_location": node["location"], "result": result}


def build_local_registration(*, node_id: str, endpoint: str, registry_path: str,
                             allowed_workers: set[str], budget_state_path: str | None = None,
                             location: str = "remote", codex_bin: str = "codex", run=None) -> dict:
    workers = [w for w in load_registry(registry_path) if w.id in allowed_workers]
    unknown = allowed_workers - {w.id for w in workers}
    if unknown:
        raise MeshError(f"unknown local worker(s): {', '.join(sorted(unknown))}")
    budgets: dict[str, WorkerBudget] = load_budget_state(budget_state_path) if budget_state_path else {}
    ads = []
    for worker in workers:
        kwargs = {"codex_bin": codex_bin}
        if run is not None:
            kwargs["run"] = run
        status = probe(worker, **kwargs)
        ads.append({"worker": worker.id, "provider": worker.provider,
                    "cost_class": worker.cost_class, "priority": worker.priority,
                    "ready": status["ready"], "auth": status["auth"],
                    "budget": budget_summary(budgets.get(worker.id))})
    return validate_registration({"version": 1, "node_id": node_id,
                                  "endpoint": endpoint, "location": location,
                                  "workers": ads})
