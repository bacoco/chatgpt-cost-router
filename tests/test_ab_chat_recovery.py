from concurrent.futures import ThreadPoolExecutor
import time
import unittest
from unittest.mock import patch
import test_chat_operations as fixtures
from operation_contracts.common import ContractError
from operation_contracts.projects import Projects
from chat_ops.mcp_transport import MCPTransport


class ChatRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ChatOperationsTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.e = self.fixture.engine

    def test_preflight_failure_retries_only_preflight(self):
        run = self.e.submit(self.fixture.workflow())["run_id"]
        todo = self.e.next("alpha", run)
        self.e.record("alpha", run, "mail", todo["token"], {"messages": [{"subject": "context"}]})
        todo = self.e.next("alpha", run)
        self.assertEqual(todo["kind"], "preflight")
        self.e.record("alpha", run, "issue", todo["token"], {}, error=True)
        todo = self.e.reconcile("alpha", run, "issue")
        self.assertEqual(todo["kind"], "preflight")
        self.assertTrue(todo["invocation"]["read_only"])

    def test_concurrent_next_emits_one_instruction(self):
        run = self.e.submit(self.fixture.workflow())["run_id"]
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(pool.map(lambda _: self.e.next("alpha", run), range(12)))
        self.assertEqual(sum(r["state"] == "INVOKE_TOOL" for r in responses), 1)

    def test_cancel_before_execution_stops_all_tools(self):
        tools = fixtures.FakeTools()
        run = self.e.submit(self.fixture.workflow())["run_id"]
        self.assertEqual(self.e.cancel("alpha", run)["state"], "CANCELLED")
        self.e.run("alpha", run, tools)
        self.assertEqual(tools.calls, [])

    def test_cancel_pending_write_allows_only_readback(self):
        workflow = self.fixture.workflow()
        workflow["steps"].append({"id": "more", "resource": "mail", "action": "gmail.search", "arguments": {}})
        tools = fixtures.FakeTools()
        run = self.e.submit(workflow)["run_id"]
        self.e.run("alpha", run, tools)
        self.e.approve("alpha", run, "issue")
        todo = self.e.next("alpha", run)
        tools.invoke(todo["invocation"])
        self.assertEqual(self.e.cancel("alpha", run)["state"], "UNCERTAIN")
        verified = self.e.reconcile("alpha", run, "issue")
        self.assertEqual(verified["kind"], "verify")
        self.e.record("alpha", run, "issue", verified["token"], tools.invoke(verified["invocation"]))
        self.assertEqual(self.e.run("alpha", run, tools)["state"], "CANCELLED")
        self.assertEqual(tools.writes, 1)
        self.assertEqual(sum(c["action"] == "gmail.search" for c in tools.calls), 1)

    def test_deadline_does_not_prevent_verifying_an_already_completed_write(self):
        workflow = self.fixture.workflow()
        tools = fixtures.FakeTools()
        run = self.e.submit(workflow)["run_id"]
        self.e.run("alpha", run, tools)
        self.e.approve("alpha", run, "issue")
        todo = self.e.next("alpha", run)
        self.e.record("alpha", run, "issue", todo["token"], tools.invoke(todo["invocation"]))
        with patch("chat_ops.engine.time.time", return_value=workflow["deadline"] + 1):
            self.assertEqual(self.e.run("alpha", run, tools)["state"], "SUCCEEDED")
        self.assertEqual(tools.writes, 1)

    def test_expired_workflow_cannot_start_a_new_tool(self):
        workflow = self.fixture.workflow()
        workflow["deadline"] = time.time() - 1
        run = self.e.submit(workflow)["run_id"]
        self.assertEqual(self.e.next("alpha", run)["state"], "BLOCKED")

    def test_events_are_scoped_and_do_not_expose_tool_output(self):
        run = self.e.submit(self.fixture.workflow())["run_id"]
        self.e.next("alpha", run)
        self.assertTrue(self.e.events("alpha", run)["events"])
        with self.assertRaises(ContractError):
            self.e.events("other", run)
        self.assertNotIn("token", str(self.e.events("alpha", run)))

    def test_same_connector_supports_multiple_explicit_accounts(self):
        make = lambda account: {"url": "http://127.0.0.1:12345/mcp", "account_ref": account, "actions": {"github.read": "read"}}
        transport = MCPTransport({"github": [make("a"), make("b")]})
        self.assertEqual(set(transport.clients), {("github", "a"), ("github", "b")})
        with self.assertRaises(ContractError):
            MCPTransport({"github": [make("a"), make("a")]})
        with self.assertRaises(ContractError):
            transport.invoke({"connector": "github", "account_ref": "unknown"})

    def test_bound_resource_distinguishes_boolean_and_number(self):
        policy = Projects({"version": 1, "projects": {"p": {"members": ["alice"], "resources": {
            "r": {"connector": "github", "account_ref": "a", "actions": ["github.read"], "bindings": {"id": 1}}}}}})
        with self.assertRaises(ContractError):
            policy.resource("alice", "p", "r", "github.read", {"id": True})

    def test_missing_null_binding_is_not_authorized(self):
        policy = Projects({"version": 1, "projects": {"p": {"members": ["alice"], "resources": {
            "r": {"connector": "github", "account_ref": "a", "actions": ["github.read"], "bindings": {"id": None}}}}}})
        with self.assertRaises(ContractError):
            policy.resource("alice", "p", "r", "github.read", {})
