import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from cost_router.workers import Worker, WorkerError, load_registry, probe, run_task, select_worker


class FakeRun:
    def __init__(self, statuses=None, exec_output=""):
        self.statuses = statuses or {}
        self.exec_output = exec_output
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        home = kwargs["env"]["CODEX_HOME"]
        if command[1:3] == ["login", "status"]:
            ok = self.statuses.get(home, False)
            return subprocess.CompletedProcess(command, 0 if ok else 1,
                                               "Logged in using ChatGPT\n" if ok else "Not logged in\n", "")
        return subprocess.CompletedProcess(command, 0, "WORKER_OK\n", self.exec_output)


class WorkerTests(unittest.TestCase):
    def test_registry_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workers.json"
            path.write_text(json.dumps({"version": 1, "workers": [
                {"id": "x", "provider": "openai", "adapter": "codex-exec", "codex_home": "a"},
                {"id": "x", "provider": "openai", "adapter": "codex-exec", "codex_home": "b"},
            ]}))
            with self.assertRaises(WorkerError):
                load_registry(path)

    def test_probe_uses_worker_home_and_removes_paid_api_keys(self):
        worker = Worker("B", "openai", "codex-exec", "~/B")
        expected = str(Path("~/B").expanduser())
        fake = FakeRun({expected: True})
        with patch.dict(os.environ, {"OPENAI_API_KEY": "must-not-leak"}):
            result = probe(worker, run=fake)
        self.assertTrue(result["ready"])
        self.assertEqual(fake.calls[0][1]["env"]["CODEX_HOME"], expected)
        self.assertNotIn("OPENAI_API_KEY", fake.calls[0][1]["env"])

    def test_auto_selection_falls_back_to_ready_worker(self):
        a = Worker("A", "openai", "codex-exec", "/A", priority=10)
        b = Worker("B", "openai", "codex-exec", "/B", priority=20)
        fake = FakeRun({"/A": False, "/B": True})
        selected, statuses = select_worker([b, a], run=fake)
        self.assertEqual(selected.id, "B")
        self.assertEqual([x["worker"] for x in statuses], ["A", "B"])

    def test_explicit_selection_does_not_probe_other_worker(self):
        a = Worker("A", "openai", "codex-exec", "/A")
        b = Worker("B", "openai", "codex-exec", "/B")
        fake = FakeRun({"/B": True})
        selected, statuses = select_worker([a, b], "B", run=fake)
        self.assertEqual(selected.id, "B")
        self.assertEqual([x["worker"] for x in statuses], ["B"])

    def test_run_is_ephemeral_read_only_and_parses_telemetry(self):
        worker = Worker("B", "openai", "codex-exec", "/B")
        fake = FakeRun(exec_output="model: gpt-6-astra\nprovider: openai\ntokens used\n4\u202f432\n")
        ticks = iter([10.0, 12.5])
        with tempfile.TemporaryDirectory() as folder:
            result = run_task(worker, "hello", folder, run=fake, clock=lambda: next(ticks))
        command = fake.calls[0][0]
        self.assertIn("--ephemeral", command)
        self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
        self.assertEqual(result["model"], "gpt-6-astra")
        self.assertEqual(result["tokens_reported"], 4432)
        self.assertEqual(result["elapsed_seconds"], 2.5)
        self.assertTrue(result["paid_api_env_removed"])


if __name__ == "__main__":
    unittest.main()
