import json
import importlib.util
import os
import plistlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cost_router.macos_launchd import (
    LABELS, LaunchdError, install_control, install_worker_node,
    launchagent_plist, private_json,
)


class LaunchdTests(unittest.TestCase):
    def load_runner(self):
        path = Path(__file__).resolve().parents[1] / "scripts/mesh_service_runner.py"
        spec = importlib.util.spec_from_file_location("mesh_service_runner", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def fake_repo(self, root: Path) -> Path:
        repo = root / "repo"
        for rel in (
            "scripts/mesh_service_runner.py", "scripts/mesh_control_server.py",
            "scripts/remote_worker_server.py", "scripts/mesh_node_agent.py",
            "examples/workers.json",
        ):
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
        return repo

    def test_private_json_is_0600(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a/b.json"
            private_json(p, {"version": 1})
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)

    def test_plist_is_keepalive_user_process(self):
        p = launchagent_plist(LABELS["control"], "/usr/bin/python3", Path("/repo/runner.py"),
                              "control", Path("/cfg.json"), Path("/logs"))
        self.assertTrue(p["RunAtLoad"])
        self.assertEqual(p["KeepAlive"], {"SuccessfulExit": False})
        self.assertNotIn("UserName", p)
        self.assertNotIn("EnvironmentVariables", p)

    @patch("cost_router.macos_launchd.executable")
    def test_dry_install_control_writes_private_config_and_plist(self, exe):
        exe.side_effect = lambda x: f"/bin/{x}"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = self.fake_repo(root)
            home = root / "home"
            files = install_control(repo=repo, home=home, allowed_users="owner@example.com", dry_run=True)
            self.assertEqual(len(files), 2)
            cfg, plist = files
            self.assertEqual(cfg.stat().st_mode & 0o777, 0o600)
            self.assertEqual(plist.stat().st_mode & 0o777, 0o600)
            with plist.open("rb") as fh:
                data = plistlib.load(fh)
            self.assertEqual(data["Label"], LABELS["control"])
            self.assertNotIn("owner@example.com", repr(data))

    @patch("cost_router.macos_launchd.executable")
    def test_dry_install_worker_node_creates_two_agents(self, exe):
        exe.side_effect = lambda x: f"/bin/{x}"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = self.fake_repo(root)
            home = root / "home"
            files = install_worker_node(repo=repo, home=home,
                control_url="https://control.example.ts.net:8444",
                allowed_users="owner@example.com", workers="openai-B", dry_run=True)
            self.assertEqual(len(files), 4)
            plists = [p for p in files if p.suffix == ".plist"]
            self.assertEqual(len(plists), 2)
            for p in plists:
                with p.open("rb") as fh:
                    data = plistlib.load(fh)
                self.assertNotIn("owner@example.com", repr(data))
                self.assertNotIn("openai-B", repr(data))

    @patch("cost_router.macos_launchd.executable")
    def test_worker_node_rejects_non_tailnet_control_url(self, exe):
        exe.side_effect = lambda x: f"/bin/{x}"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(LaunchdError):
                install_worker_node(repo=self.fake_repo(root), home=root / "home",
                    control_url="https://example.com", allowed_users="x", workers="B", dry_run=True)

    def test_runner_requires_versioned_config(self):
        module = self.load_runner()
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text('{"version":2}')
            with self.assertRaises(ValueError):
                module.load_config(str(p))

    def test_runner_remote_worker_uses_absolute_registry_and_binary_paths(self):
        module = self.load_runner()
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "cfg.json"
            cfg.write_text(json.dumps({
                "version": 1, "repo": "/repo", "allowed_users": "u",
                "workers": "openai-B", "tailscale_bin": "/opt/tailscale/bin/tailscale",
                "codex_bin": "/opt/codex/bin/codex", "https_port": 8443, "backend_port": 8787
            }))
            with patch.object(module, "wait_tailscale"), patch.object(module, "serve"), \
                 patch.object(module, "exec_python") as exec_python:
                self.assertEqual(module.main(["remote-worker", "--config", str(cfg)]), 0)
            args = exec_python.call_args.args
            self.assertIn("--registry", args[2])
            self.assertIn("/repo/examples/workers.json", args[2])
            self.assertIn("/opt/tailscale/bin", args[3]["PATH"])
            self.assertIn("/opt/codex/bin", args[3]["PATH"])

    def test_runner_mesh_node_uses_absolute_registry(self):
        module = self.load_runner()
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "cfg.json"
            cfg.write_text(json.dumps({
                "version": 1, "repo": "/repo", "control_url": "https://c.example.ts.net:8444",
                "workers": "openai-B", "tailscale_bin": "/opt/tailscale/bin/tailscale",
                "codex_bin": "/opt/codex/bin/codex", "worker_port": 8443, "heartbeat_seconds": 30
            }))
            with patch.object(module, "wait_tailscale"), patch.object(module, "wait_port"), \
                 patch.object(module, "exec_python") as exec_python:
                self.assertEqual(module.main(["mesh-node", "--config", str(cfg)]), 0)
            args = exec_python.call_args.args
            self.assertIn("--registry", args[2])
            self.assertIn("/repo/examples/workers.json", args[2])


if __name__ == "__main__":
    unittest.main()
