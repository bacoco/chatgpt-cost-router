import json
import plistlib
import tempfile
import unittest
from pathlib import Path

from fleet_operator.macos import SERVER_LABEL, RELAY_LABEL, InstallError, init_fleet_config, install_relay, install_server, install_tunnel, launch_plist, tunnel_yaml


class MacOSFleetOperatorTests(unittest.TestCase):
    def fake_repo(self, root: Path) -> Path:
        repo = root / "repo"
        for rel in ("scripts/fleet_operator_server.py", "fleet_operator/core.py", "fleet_operator/mcp_server.py", "requirements-fleet-operator.txt"):
            p = repo / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x")
        return repo

    def test_plist_keepalive_and_loopback_env(self):
        p = launch_plist(SERVER_LABEL, ["/venv/python", "/repo/server.py"], Path("/logs"), {"FLEET_OPERATOR_HOST": "127.0.0.1"})
        self.assertTrue(p["RunAtLoad"]); self.assertEqual(p["KeepAlive"], {"SuccessfulExit": False}); self.assertEqual(p["EnvironmentVariables"]["FLEET_OPERATOR_HOST"], "127.0.0.1")

    def test_dry_server_install_plist_has_config_path_not_config_contents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self.fake_repo(root); home = root / "home"; cfg = home / ".config/chatgpt-cost-router/fleet-operator.json"; cfg.parent.mkdir(parents=True); cfg.write_text(json.dumps({"version":1,"hosts":{"secret-host":{"transport":"local"}}}))
            files = install_server(repo=repo, home=home, config=cfg, dry_run=True); self.assertEqual(len(files),1)
            with files[0].open("rb") as fh: plist=plistlib.load(fh)
            text=repr(plist); self.assertIn(str(cfg.resolve()),text); self.assertNotIn("secret-host",text); self.assertEqual(plist["EnvironmentVariables"]["FLEET_OPERATOR_HOST"],"127.0.0.1")

    def test_tunnel_yaml_uses_file_secret_and_local_mcp(self):
        y=tunnel_yaml(tunnel_id="tunnel_"+"a"*32,key_file=Path("/secret/key")); self.assertIn("api_key: file:/secret/key",y); self.assertIn("url: http://127.0.0.1:8810/mcp",y); self.assertNotIn("sk-",y)

    def test_tunnel_id_validation(self):
        with self.assertRaises(InstallError): tunnel_yaml(tunnel_id="bad",key_file=Path("/secret/key"))

    def test_dry_tunnel_install_plist_contains_no_api_key(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td)/"home"; files=install_tunnel(home=home,tunnel_id="tunnel_"+"b"*32,key_file=Path(td)/"runtime.key",tunnel_client="/usr/local/bin/tunnel-client",dry_run=True); config,plist_path=files; self.assertEqual(config.stat().st_mode & 0o777,0o600)
            with plist_path.open("rb") as fh: plist=plistlib.load(fh)
            text=repr(plist); self.assertNotIn("runtime.key",text); self.assertNotIn("tunnel_",text); self.assertIn(str(config),text)

    def test_init_config_is_private_and_hides_nothing_in_repo(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fleet.json"; init_fleet_config(path=p,local_host=("gateway","/tmp/work"),ssh_hosts=[("studio","macstudio@studio.example.ts.net","/Users/macstudio/work")]); self.assertEqual(p.stat().st_mode & 0o777,0o600); data=json.loads(p.read_text()); self.assertEqual(data["hosts"]["gateway"]["transport"],"local"); self.assertEqual(data["hosts"]["studio"]["transport"],"ssh"); self.assertIn("git",data["hosts"]["studio"]["write_commands"])

    def test_dry_relay_install_has_no_host_targets_in_plist(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo=self.fake_repo(root); (repo/".git").mkdir(); (repo/"scripts/fleet_operator_relay.py").write_text("x"); (repo/"fleet_operator/relay.py").write_text("x"); home=root/"home"; cfg=home/".config/chatgpt-cost-router/fleet-operator.json"; cfg.parent.mkdir(parents=True); cfg.write_text(json.dumps({"version":1,"hosts":{"studio":{"ssh_target":"secret@host"}}})); files=install_relay(repo=repo,home=home,fleet_config=cfg,dry_run=True); self.assertEqual(len(files),2)
            with files[1].open("rb") as fh: plist=plistlib.load(fh)
            self.assertNotIn("secret@host",repr(plist)); self.assertEqual(plist["Label"],RELAY_LABEL)


if __name__ == "__main__": unittest.main()
