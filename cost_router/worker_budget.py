"""Quota/budget metadata and zero-model worker ranking."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Union

from .workers import COST_ORDER, Worker, WorkerError, probe


@dataclass(frozen=True)
class WorkerBudget:
    worker: str
    status: str = "unknown"
    five_hour_remaining_pct: float | None = None
    weekly_remaining_pct: float | None = None
    reported_tokens_5h: int | None = None
    reported_tokens_weekly: int | None = None


VALID_STATUS = {"available", "busy", "quota_exhausted", "unknown"}


def _pct(value, field: str) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not 0 <= number <= 100:
        raise WorkerError(f"{field} must be between 0 and 100")
    return number


def _tokens(value, field: str) -> int | None:
    if value is None:
        return None
    number = int(value)
    if number < 0:
        raise WorkerError(f"{field} must be >= 0")
    return number


def load_budget_state(path: Union[str, Path]) -> dict[str, WorkerBudget]:
    data = json.loads(Path(path).expanduser().read_text())
    if data.get("version") != 1 or not isinstance(data.get("budgets"), list):
        raise WorkerError("budget state must have version=1 and a budgets array")
    result: dict[str, WorkerBudget] = {}
    for item in data["budgets"]:
        worker = item.get("worker")
        status = item.get("status", "unknown")
        if not worker or worker in result:
            raise WorkerError(f"duplicate or empty budget worker: {worker!r}")
        if status not in VALID_STATUS:
            raise WorkerError(f"invalid budget status for {worker}: {status}")
        result[worker] = WorkerBudget(
            worker=worker,
            status=status,
            five_hour_remaining_pct=_pct(item.get("five_hour_remaining_pct"), "five_hour_remaining_pct"),
            weekly_remaining_pct=_pct(item.get("weekly_remaining_pct"), "weekly_remaining_pct"),
            reported_tokens_5h=_tokens(item.get("reported_tokens_5h"), "reported_tokens_5h"),
            reported_tokens_weekly=_tokens(item.get("reported_tokens_weekly"), "reported_tokens_weekly"),
        )
    return result


def _headroom(budget: WorkerBudget | None) -> tuple[int, float]:
    if budget is None:
        return (1, -1.0)
    values = [v for v in (budget.five_hour_remaining_pct, budget.weekly_remaining_pct) if v is not None]
    if not values:
        return (1, -1.0)
    return (0, min(values))


def _eligible(worker: Worker, budget: WorkerBudget | None) -> bool:
    return worker.enabled and (budget is None or budget.status not in {"busy", "quota_exhausted"})


def economic_order(workers: Iterable[Worker], budgets: Mapping[str, WorkerBudget]) -> list[Worker]:
    eligible = [w for w in workers if _eligible(w, budgets.get(w.id))]
    return sorted(
        eligible,
        key=lambda w: (
            COST_ORDER[w.cost_class],
            _headroom(budgets.get(w.id))[0],
            -_headroom(budgets.get(w.id))[1],
            w.priority,
            w.id,
        ),
    )


def select_economic_worker(
    workers: Iterable[Worker],
    budgets: Mapping[str, WorkerBudget],
    requested: str = "auto",
    *,
    run=None,
    codex_bin: str = "codex",
):
    all_workers = list(workers)
    if requested != "auto":
        matches = [w for w in all_workers if w.id == requested]
        if not matches:
            raise WorkerError(f"unknown worker: {requested}")
        budget = budgets.get(requested)
        if not _eligible(matches[0], budget):
            reason = budget.status if budget else "disabled"
            raise WorkerError(f"worker {requested} is unavailable by budget state: {reason}")
        ordered = matches
    else:
        ordered = economic_order(all_workers, budgets)
    if not ordered:
        raise WorkerError("no worker eligible by budget state")
    probes = []
    for worker in ordered:
        kwargs = {"codex_bin": codex_bin}
        if run is not None:
            kwargs["run"] = run
        status = probe(worker, **kwargs)
        status["budget"] = budget_summary(budgets.get(worker.id))
        probes.append(status)
        if status["ready"]:
            return worker, probes
    raise WorkerError(f"no ready worker; probes={probes}")


def budget_summary(budget: WorkerBudget | None) -> dict:
    if budget is None:
        return {"status": "unknown", "five_hour_remaining_pct": None, "weekly_remaining_pct": None}
    return {
        "status": budget.status,
        "five_hour_remaining_pct": budget.five_hour_remaining_pct,
        "weekly_remaining_pct": budget.weekly_remaining_pct,
        "reported_tokens_5h": budget.reported_tokens_5h,
        "reported_tokens_weekly": budget.reported_tokens_weekly,
    }
