import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from cost_router.remote_worker import (
    RemotePolicy,
    RemoteWorkerError,
    dispatch_remote,
    list_remote_workers,
    parse_request_body,
    tailscale_identity,
)
from cost_router.worker_health import status as worker_health_status


class FakeRun:
    def __init__(self, ready_homes=None):
        self.ready_homes = set(ready_homes or [])
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[1:3] == ["login", "status"]:
            ready = kwargs["env"]["CODEX_HOME"] in self.ready_homes
            return subprocess.CompletedProcess(command, 0 if ready else 1,
                "Logged in using ChatGPT\n" if ready else "Not logged in\n", "")
        return subprocess.CompletedProcess(
            command, 0, "REMOTE_OK\n",
            "model: gpt-test\nprovider: openai\ntokens used\n1\u202f234\n"
        )


def registry(path):
    path.write_text(json.dumps({"version": 1, "workers": [
        {"id": "A", "provider": "openai", "adapter": "codex-exec", "codex_home": "/A"},
        {"id": "B", "provider": "openai", "adapter": "codex-exec", "codex_home": "/B"},
    ]}))


class RemoteWorkerTests(unittest.TestCase):
    def policy(self, root, workers=("B",)):
        return RemotePolicy(frozenset({"friend@example.com"}), frozenset(workers), Path(root))

    def test_identity_required_and_allowlisted(self):
        with tempfile.TemporaryDirectory() as root:
            policy = self.policy(root)
            with self.assertRaises(RemoteWorkerError):
                tailscale_identity({}, policy)
            with self.assertRaises(RemoteWorkerError):
                tailscale_identity({"Tailscale-User-Login": "other@example.com"}, policy)
            self.assertEqual(
                tailscale_identity({"Tailscale-User-Login": "FRIEND@example.com"}, policy),
                "friend@example.com",
            )

    def test_request_schema_rejects_workspace_and_oversize(self):
        with tempfile.TemporaryDirectory() as root:
            policy = self.policy(root)
            with self.assertRaises(RemoteWorkerError):
                parse_request_body(json.dumps({"prompt": "x", "workspace": "/tmp"}).encode(), policy)
            with self.assertRaises(RemoteWorkerError):
                parse_request_body(json.dumps({"prompt": "x" * 12001}).encode(), policy)

    def test_remote_worker_listing_hides_paths(self):
        with tempfile.TemporaryDirectory() as root:
            reg = Path(root) / "workers.json"
            registry(reg)
            fake = FakeRun({"/B"})
            result = list_remote_workers(policy=self.policy(root), registry_path=str(reg), run=fake)
            self.assertEqual(result, [{"worker": "B", "ready": True, "auth": "chatgpt"}])
            self.assertNotIn("/B", json.dumps(result))

    def test_dispatch_rejects_non_allowed_worker_before_execution(self):
        with tempfile.TemporaryDirectory() as root:
            reg = Path(root) / "workers.json"
            registry(reg)
            fake = FakeRun({"/A", "/B"})
            with self.assertRaises(RemoteWorkerError):
                dispatch_remote({"worker": "A", "prompt": "hi"}, policy=self.policy(root), registry_path=str(reg), run=fake)
            self.assertEqual(fake.calls, [])

    def test_dispatch_uses_allowed_worker_and_returns_redacted_telemetry(self):
        with tempfile.TemporaryDirectory() as root:
            reg = Path(root) / "workers.json"
            registry(reg)
            fake = FakeRun({"/B"})
            ticks = iter([1.0, 2.25])
            result = dispatch_remote(
                {"worker": "B", "prompt": "hi"},
                policy=self.policy(root), registry_path=str(reg), run=fake, clock=lambda: next(ticks)
            )
            self.assertEqual(result["worker"], "B")
            self.assertEqual(result["tokens_reported"], 1234)
            self.assertEqual(result["elapsed_seconds"], 1.25)
            self.assertEqual(result["output"], "REMOTE_OK\n")
            self.assertNotIn("stderr", result)
            self.assertNotIn("codex_home", json.dumps(result))
            self.assertEqual(list(Path(root).glob("task-*")), [])
            exec_command = fake.calls[-1][0]
            self.assertIn("--ephemeral", exec_command)
            self.assertIn("--ignore-user-config", exec_command)
            self.assertEqual(exec_command[exec_command.index("--sandbox") + 1], "read-only")


    def test_actual_auth_failure_quarantines_worker_and_hides_ready_state(self):
        with tempfile.TemporaryDirectory() as root:
            reg = Path(root) / "workers.json"
            registry(reg)
            health = Path(root) / "health.json"

            class AuthFailRun(FakeRun):
                def __call__(self, command, **kwargs):
                    self.calls.append((command, kwargs))
                    if command[1:3] == ["login", "status"]:
                        return subprocess.CompletedProcess(command, 0, "Logged in using ChatGPT\n", "")
                    return subprocess.CompletedProcess(
                        command, 1, "",
                        "401 Unauthorized: refresh_token_reused; Please log out and sign in again.\n",
                    )

            fake = AuthFailRun({"/B"})
            result = dispatch_remote(
                {"worker": "B", "prompt": "hi"},
                policy=self.policy(root), registry_path=str(reg), run=fake,
                health_state_path=health,
            )
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(worker_health_status("B", path=health)["status"], "quarantined")
            calls_before = len(fake.calls)
            listing = list_remote_workers(
                policy=self.policy(root), registry_path=str(reg), run=fake,
                health_state_path=health,
            )
            self.assertEqual(listing, [{"worker": "B", "ready": False, "auth": "unavailable"}])
            self.assertEqual(len(fake.calls), calls_before)

    def test_policy_unknown_worker_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            reg = Path(root) / "workers.json"
            registry(reg)
            with self.assertRaises(RemoteWorkerError):
                list_remote_workers(policy=self.policy(root, workers=("Z",)), registry_path=str(reg), run=FakeRun())


if __name__ == "__main__":
    unittest.main()
