import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from cost_router.mesh import (
    MeshError, MeshPolicy, NodeRegistry, build_local_registration,
    dispatch_mesh, tailscale_identity, validate_endpoint,
)


class FakeRun:
    def __init__(self, ready=None):
        self.ready = set(ready or [])
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        home = kwargs["env"]["CODEX_HOME"]
        ok = home in self.ready
        return subprocess.CompletedProcess(command, 0 if ok else 1,
                                           "Logged in using ChatGPT\n" if ok else "Not logged in\n", "")


def registration(node_id="node-a", endpoint="https://node-a.tail123.ts.net:8443", worker="openai-B",
                 ready=True, five=80, weekly=70):
    return {
        "version": 1,
        "node_id": node_id,
        "endpoint": endpoint,
        "location": "remote",
        "workers": [{
            "worker": worker,
            "provider": "openai",
            "cost_class": "included",
            "priority": 20,
            "ready": ready,
            "auth": "chatgpt" if ready else "unavailable",
            "budget": {"status": "available", "five_hour_remaining_pct": five,
                       "weekly_remaining_pct": weekly},
        }],
    }


class MeshTests(unittest.TestCase):
    def policy(self):
        return MeshPolicy(frozenset({"owner@example.com"}), ttl_seconds=120)

    def test_tailscale_identity_and_endpoint_validation(self):
        self.assertEqual(tailscale_identity({"Tailscale-User-Login": "OWNER@example.com"}, self.policy()),
                         "owner@example.com")
        self.assertEqual(validate_endpoint("https://node.tail123.ts.net:8443/"),
                         "https://node.tail123.ts.net:8443")
        for bad in ["http://node.tail123.ts.net", "https://example.com", "https://node.tail123.ts.net/x"]:
            with self.assertRaises(MeshError):
                validate_endpoint(bad)

    def test_registration_persists_and_ttl_expires(self):
        now = [1000.0]
        with tempfile.TemporaryDirectory() as root:
            reg = NodeRegistry(Path(root) / "nodes.json", self.policy(), clock=lambda: now[0])
            result = reg.register(registration(), "owner@example.com")
            self.assertEqual(result["node_id"], "node-a")
            self.assertEqual(len(reg.live_nodes()), 1)
            self.assertEqual((Path(root) / "nodes.json").stat().st_mode & 0o777, 0o600)
            state = (Path(root) / "nodes.json").read_text()
            self.assertNotIn("owner@example.com", state)
            self.assertIn("owner_hash", state)
            now[0] += 121
            self.assertEqual(reg.live_nodes(), [])

    def test_node_id_cannot_be_taken_over_by_other_identity(self):
        with tempfile.TemporaryDirectory() as root:
            reg = NodeRegistry(Path(root) / "nodes.json", self.policy())
            reg.register(registration(), "owner@example.com")
            with self.assertRaises(MeshError):
                reg.register(registration(), "other@example.com")

    def test_workers_are_namespaced_and_ambiguous_alias_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            reg = NodeRegistry(Path(root) / "nodes.json", self.policy())
            reg.register(registration(node_id="a", endpoint="https://a.tail123.ts.net:8443"), "owner@example.com")
            reg.register(registration(node_id="b", endpoint="https://b.tail123.ts.net:8443"), "owner@example.com")
            names = [w["mesh_worker"] for w in reg.workers()]
            self.assertEqual(names, ["a/openai-B", "b/openai-B"])
            with self.assertRaises(MeshError):
                reg.resolve("openai-B")
            self.assertEqual(reg.resolve("b/openai-B")["node_id"], "b")

    def test_auto_selection_prefers_more_known_headroom(self):
        with tempfile.TemporaryDirectory() as root:
            reg = NodeRegistry(Path(root) / "nodes.json", self.policy())
            reg.register(registration(node_id="a", endpoint="https://a.tail123.ts.net:8443", worker="A", five=20, weekly=90), "owner@example.com")
            reg.register(registration(node_id="b", endpoint="https://b.tail123.ts.net:8443", worker="B", five=80, weekly=70), "owner@example.com")
            self.assertEqual(reg.resolve("auto")["mesh_worker"], "b/B")

    def test_mesh_dispatch_forwards_only_worker_and_prompt(self):
        calls = []
        def fake_post(url, payload):
            calls.append((url, payload))
            return {"worker": "openai-B", "exit_code": 0, "output": "MESH_OK\n"}
        with tempfile.TemporaryDirectory() as root:
            reg = NodeRegistry(Path(root) / "nodes.json", self.policy())
            reg.register(registration(), "owner@example.com")
            result = dispatch_mesh(reg, {"worker": "node-a/openai-B", "prompt": "hi"}, http_post=fake_post)
            self.assertEqual(result["mesh_worker"], "node-a/openai-B")
            self.assertEqual(calls, [("https://node-a.tail123.ts.net:8443/v1/run",
                                      {"worker": "openai-B", "prompt": "hi"})])

    def test_local_advertisement_hides_codex_home(self):
        with tempfile.TemporaryDirectory() as root:
            workers_path = Path(root) / "workers.json"
            workers_path.write_text(json.dumps({"version": 1, "workers": [{
                "id": "openai-B", "provider": "openai", "adapter": "codex-exec",
                "codex_home": "/secret/home", "cost_class": "included", "priority": 20,
            }]}))
            fake = FakeRun({"/secret/home"})
            payload = build_local_registration(
                node_id="node-a", endpoint="https://node-a.tail123.ts.net:8443",
                registry_path=str(workers_path), allowed_workers={"openai-B"}, run=fake,
            )
            text = json.dumps(payload)
            self.assertNotIn("codex_home", text)
            self.assertNotIn("/secret/home", text)
            self.assertTrue(payload["workers"][0]["ready"])


if __name__ == "__main__":
    unittest.main()
