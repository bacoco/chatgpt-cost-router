import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from fleet_operator.core import FleetConfig, FleetError, FleetRunner, is_destructive


class Proc:
    def __init__(self, code=0, out=b"ok\n", err=b""):
        self.returncode = code
        self.stdout = out
        self.stderr = err


class FleetOperatorTests(unittest.TestCase):
    def make_config(self, td: str, **overrides):
        data = {
            "version": 1, "ssh_bin": "/usr/bin/ssh", "connect_timeout_seconds": 7,
            "default_timeout_seconds": 30, "max_timeout_seconds": 120, "max_output_bytes": 4096,
            "hosts": {
                "macbook": {"ssh_target": "loic@macbook.example.ts.net", "allowed_roots": ["/Users/loic/work"], "read_commands": ["uname", "head", "git", "python3", "tail"], "write_commands": ["git", "python3", "launchctl", "kill", "rm"], "tags": ["mac", "worker"]},
                "studio": {"ssh_target": "macstudio@100.64.0.2", "allowed_roots": ["/Users/macstudio/work"], "read_commands": ["uname", "head", "git"], "write_commands": ["git"]},
            },
        }
        data.update(overrides)
        p = Path(td) / "fleet.json"
        p.write_text(json.dumps(data))
        return FleetConfig.load(p)

    def test_inventory_hides_ssh_targets(self):
        with tempfile.TemporaryDirectory() as td:
            text = json.dumps(FleetRunner(self.make_config(td)).inventory())
            self.assertIn("macbook", text); self.assertNotIn("loic@", text); self.assertNotIn("100.64.0.2", text)

    def test_read_command_enforces_allowlist(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc()))
            with self.assertRaises(FleetError): r.execute("macbook", ["rm", "-rf", "x"], mode="read")

    def test_root_admin_command_is_hard_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc()))
            with self.assertRaises(FleetError): r.execute("macbook", ["sudo", "true"], mode="write", allow_destructive=True)

    def test_destructive_requires_explicit_flag(self):
        self.assertTrue(is_destructive(["rm", "-rf", "tmp"])); self.assertTrue(is_destructive(["git", "reset", "--hard"]));
        with tempfile.TemporaryDirectory() as td:
            run = Mock(return_value=Proc()); r = FleetRunner(self.make_config(td), run=run)
            with self.assertRaises(FleetError): r.execute("macbook", ["kill", "123"], mode="write")
            r.execute("macbook", ["kill", "123"], mode="write", allow_destructive=True); self.assertEqual(run.call_count, 1)

    def test_cwd_cannot_escape_allowed_root(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc()))
            with self.assertRaises(FleetError): r.execute("macbook", ["git", "status"], cwd="/etc", mode="read")
            with self.assertRaises(FleetError): r.execute("macbook", ["git", "status"], cwd="/Users/loic/work/../secret", mode="read")

    def test_ssh_is_batch_strict_and_quotes_argv(self):
        with tempfile.TemporaryDirectory() as td:
            run = Mock(return_value=Proc(out=b"branch\n")); r = FleetRunner(self.make_config(td), run=run)
            result = r.execute("macbook", ["git", "status", "--short"], cwd="/Users/loic/work/repo", mode="read")
            cmd = run.call_args.args[0]; joined = " ".join(cmd)
            self.assertIn("BatchMode=yes", joined); self.assertIn("StrictHostKeyChecking=yes", joined); self.assertIn("loic@macbook.example.ts.net", joined); self.assertIn("cd -- /Users/loic/work/repo", cmd[-1]); self.assertEqual(result.exit_code, 0)

    def test_output_is_capped(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc(out=b"x" * 6000, err=b"y" * 6000)))
            out = r.execute("macbook", ["uname", "-a"], mode="read"); self.assertTrue(out.stdout_truncated); self.assertTrue(out.stderr_truncated); self.assertLessEqual(len(out.stdout.encode()), 4096)

    def test_timeout_becomes_structured_result(self):
        with tempfile.TemporaryDirectory() as td:
            run = Mock(side_effect=subprocess.TimeoutExpired(cmd="ssh", timeout=1, output=b"partial")); r = FleetRunner(self.make_config(td), run=run)
            out = r.execute("macbook", ["uname", "-a"], mode="read", timeout_seconds=1); self.assertTrue(out.timed_out); self.assertEqual(out.exit_code, 124); self.assertEqual(out.stdout, "partial")

    def test_parallel_preserves_requested_host_order(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc()))
            out = r.execute_many(["studio", "macbook"], ["uname", "-a"], mode="read"); self.assertEqual([x["host"] for x in out], ["studio", "macbook"])

    def test_read_file_stays_under_root_and_uses_head(self):
        with tempfile.TemporaryDirectory() as td:
            r = FleetRunner(self.make_config(td), run=Mock(return_value=Proc(out=b"hello")))
            out = r.read_file("macbook", "/Users/loic/work/repo/README.md", max_bytes=100); self.assertEqual(out["stdout"], "hello"); self.assertEqual(out["path"], "/Users/loic/work/repo/README.md")
            with self.assertRaises(FleetError): r.read_file("macbook", "/etc/passwd")

    def test_local_transport_skips_ssh(self):
        with tempfile.TemporaryDirectory() as td:
            data = {"version": 1, "max_output_bytes": 4096, "hosts": {"gateway": {"transport": "local", "allowed_roots": ["/tmp"], "read_commands": ["uname"], "write_commands": []}}}
            p = Path(td) / "fleet.json"; p.write_text(json.dumps(data)); run = Mock(return_value=Proc()); r = FleetRunner(FleetConfig.load(p), run=run)
            r.execute("gateway", ["uname", "-a"], mode="read"); self.assertEqual(run.call_args.args[0], ["uname", "-a"]); self.assertIsNone(run.call_args.kwargs["cwd"])


if __name__ == "__main__": unittest.main()
