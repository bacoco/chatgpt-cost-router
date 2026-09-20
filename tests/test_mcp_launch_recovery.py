"""Validate embedded recovery and both MCP SDK constructor paths without network."""
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from operation_contracts.mcp_recovery import (
    MCP_RECOVERY_INSTRUCTIONS as RULE, with_recovery_instructions,
)
from operation_contracts import mcp_runtime

ROOT = Path(__file__).resolve().parents[1]


class RecoveryInstructionsTests(unittest.TestCase):
    def test_preserves_server_instructions(self):
        base = "Project grants and exact write approvals remain required.\n"
        self.assertEqual(with_recovery_instructions(base), base + "\n\n" + RULE)

    def test_idempotent(self):
        once = with_recovery_instructions("Private server")
        self.assertEqual(with_recovery_instructions(once), once)

    def test_empty_instructions(self):
        self.assertEqual(with_recovery_instructions(""), RULE)

    def test_non_text_rejected(self):
        for value in (None, {}, 42):
            with self.subTest(value=value), self.assertRaises(TypeError):
                with_recovery_instructions(value)

    def test_partial_marker_does_not_suppress_complete_rule(self):
        text = "[MCP-CONVERSATION-RECOVERY-v1] placeholder"
        self.assertTrue(with_recovery_instructions(text).endswith(RULE))

    def test_guardrails_are_embedded(self):
        for phrase in ("This conversation does not support developer MCPs",
                       "is restricted to developer MCPs", "Pas une branche Git",
                       "un seul test", "pas cette piste comme un correctif garanti",
                       "aucune restriction administrateur", "écriture incertaine",
                       "En tâche planifiée", "sans créer", "approbation"):
            self.assertIn(phrase, RULE)

    def test_no_live_sdk_required_to_import(self):
        with patch.dict(sys.modules, {"mcp": None}):
            self.assertIs(importlib.reload(mcp_runtime), mcp_runtime)

    def _server(self, modern):
        class Capture:
            def __init__(self, name, instructions):
                self.name, self.instructions = name, instructions
        modules = {key: types.ModuleType(key) for key in
                   ("mcp", "mcp.server", "mcp.server.fastmcp")}
        if modern:
            modules["mcp.server"].MCPServer = Capture
        else:
            modules["mcp.server.fastmcp"].FastMCP = Capture
        with patch.dict(sys.modules, modules):
            return mcp_runtime.new_server("Test server", "Original constraints")

    def test_modern_constructor_receives_rule(self):
        server = self._server(True)
        self.assertEqual(server.name, "Test server")
        self.assertEqual(server.instructions,
                         "Original constraints\n\n" + RULE)

    def test_legacy_constructor_receives_rule(self):
        server = self._server(False)
        self.assertEqual(server.instructions,
                         "Original constraints\n\n" + RULE)

    def test_launch_copies_match(self):
        paths = (".chatgpt/PROJECT.md", ".chatgpt/SCHEDULER.md",
                 "docs/PROJECT_BOOTSTRAP_PROMPT.md",
                 "docs/REPO_SCHEDULER_WORKSPACE.md",
                 "docs/MCP_RECOVERY_INSTRUCTIONS.md",
                 "docs/FLEET_OPERATOR_PLUGIN.md",
                 "skills/project-workspace-bootstrap/SKILL.md")
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_text().count(RULE), 1)

    def test_copyable_prompts_include_rule_inside_fence(self):
        for path in ("docs/PROJECT_BOOTSTRAP_PROMPT.md",
                     "docs/REPO_SCHEDULER_WORKSPACE.md"):
            with self.subTest(path=path):
                self.assertIn("```text\n" + RULE, (ROOT / path).read_text())

    def test_all_repo_servers_use_common_factory(self):
        for path in ("chat_ops/mcp_server.py", "fleet_operator/mcp_server.py",
                     "fleet_operator/jobs/mcp_server.py"):
            text = (ROOT / path).read_text()
            with self.subTest(path=path):
                self.assertIn("from operation_contracts.mcp_runtime import new_server", text)
                self.assertIn("new_server(", text)


if __name__ == "__main__":
    unittest.main()
