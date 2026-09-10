import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from cost_router.worker_budget import economic_order, load_budget_state, select_economic_worker
from cost_router.workers import Worker, WorkerError


class FakeRun:
    def __init__(self, statuses=None):
        self.statuses = statuses or {}
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        home = kwargs["env"]["CODEX_HOME"]
        ok = self.statuses.get(home, False)
        return subprocess.CompletedProcess(
            command, 0 if ok else 1,
            "Logged in using ChatGPT\n" if ok else "Not logged in\n", ""
        )


class WorkerBudgetTests(unittest.TestCase):
    def test_prefers_greater_known_headroom_at_same_cost(self):
        a = Worker("A", "openai", "codex-exec", "/A", priority=10)
        b = Worker("B", "openai", "codex-exec", "/B", priority=20)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(json.dumps({"version": 1, "budgets": [
                {"worker": "A", "status": "available", "five_hour_remaining_pct": 20, "weekly_remaining_pct": 80},
                {"worker": "B", "status": "available", "five_hour_remaining_pct": 70, "weekly_remaining_pct": 60},
            ]}))
            budgets = load_budget_state(path)
        self.assertEqual([w.id for w in economic_order([a, b], budgets)], ["B", "A"])

    def test_exhausted_worker_is_skipped(self):
        a = Worker("A", "openai", "codex-exec", "/A", priority=10)
        b = Worker("B", "openai", "codex-exec", "/B", priority=20)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(json.dumps({"version": 1, "budgets": [
                {"worker": "A", "status": "quota_exhausted", "five_hour_remaining_pct": 0},
                {"worker": "B", "status": "available", "five_hour_remaining_pct": 40},
            ]}))
            budgets = load_budget_state(path)
        fake = FakeRun({"/B": True})
        selected, probes = select_economic_worker([a, b], budgets, run=fake)
        self.assertEqual(selected.id, "B")
        self.assertEqual([p["worker"] for p in probes], ["B"])

    def test_explicit_exhausted_worker_fails_before_probe(self):
        a = Worker("A", "openai", "codex-exec", "/A")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(json.dumps({"version": 1, "budgets": [
                {"worker": "A", "status": "quota_exhausted"}
            ]}))
            budgets = load_budget_state(path)
        fake = FakeRun({"/A": True})
        with self.assertRaises(WorkerError):
            select_economic_worker([a], budgets, "A", run=fake)
        self.assertEqual(fake.calls, [])

    def test_unknown_budget_falls_behind_known_headroom(self):
        a = Worker("A", "openai", "codex-exec", "/A", priority=1)
        b = Worker("B", "openai", "codex-exec", "/B", priority=50)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(json.dumps({"version": 1, "budgets": [
                {"worker": "A", "status": "unknown"},
                {"worker": "B", "status": "available", "weekly_remaining_pct": 25},
            ]}))
            budgets = load_budget_state(path)
        self.assertEqual([w.id for w in economic_order([a, b], budgets)], ["B", "A"])

    def test_invalid_percentage_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(json.dumps({"version": 1, "budgets": [
                {"worker": "A", "five_hour_remaining_pct": 101}
            ]}))
            with self.assertRaises(WorkerError):
                load_budget_state(path)


if __name__ == "__main__":
    unittest.main()
