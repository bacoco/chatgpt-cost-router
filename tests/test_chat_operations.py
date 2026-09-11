import tempfile
import time
import unittest
from pathlib import Path
from operation_contracts.common import ContractError
from operation_contracts.projects import Projects
from operation_contracts.journal import Journal
from chat_ops.catalog import Catalog
from chat_ops.engine import Operations


class FakeTools:
    def __init__(self):
        self.calls = []
        self.writes = 0
        self.fail_after_write = False

    def invoke(self, request):
        self.calls.append(request)
        if request["action"] == "github.issue.create":
            self.writes += 1
            if self.fail_after_write:
                raise RuntimeError("response lost after remote success")
            return {"id":42,"title":"verified context"}
        if request["action"] == "gmail.search":
            return {"messages":[{"subject":"verified context"}]}
        return {"count":self.writes,"id":42,"title":"verified context"}


class ChatOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        resources = {
            "mail":{"connector":"gmail","account_ref":"mail-a","actions":["gmail.search","gmail.read","gmail.send"]},
            "repo":{"connector":"github","account_ref":"git-a","actions":["github.read","github.search","github.issue.create"],
                    "bindings":{"owner":"example","repo":"alpha"}},
        }
        self.projects = Projects({"version":1,"projects":{"alpha":{"members":["alice"],"resources":resources}}})
        self.engine = Operations(self.projects,Journal(Path(self.tmp.name)/"a.db"),"alice",session="chat-one")
        now = time.time()
        for resource, binding in resources.items():
            for action in binding["actions"]:
                self.engine.capabilities.observe("alice","alpha",resource,action,self.engine.surface,self.engine.session,
                    {"level":"invocable","connector":binding["connector"],"account_ref":binding["account_ref"],
                     "tool_name":action,"observed_at":now,"expires_at":now+300,"evidence_ref":"test-fixture-discovery"})

    def tearDown(self):
        self.tmp.cleanup()

    def workflow(self):
        bound = {"owner":"example","repo":"alpha"}
        return {"version":1,"project_id":"alpha","idempotency_key":"multi-app-test","deadline":time.time()+60,
                "steps":[{"id":"mail","resource":"mail","action":"gmail.search","arguments":{}},
                         {"id":"issue","resource":"repo","action":"github.issue.create",
                          "arguments":{**bound,"title":{"$ref":"mail.messages.0.subject"}},
                          "preflight":{"action":"github.search","arguments":bound,"expect":{"count":0}},
                          "verify":{"action":"github.read","arguments":bound,"expect":{"count":1,"id":42}}}]}

    def test_catalog_is_not_limited_to_issues(self):
        actions = {item["action"] for item in Catalog().list()}
        self.assertTrue({"gmail.send","github.write","github.pr.merge","cowboy.publish","calendar.create",
                         "documents.write","contacts.search","serena.references","fleet.submit"} <= actions)

    def test_multi_app_workflow_approval_and_readback(self):
        workflow, tools = self.workflow(), FakeTools()
        run = self.engine.submit(workflow)["run_id"]
        self.assertEqual(self.engine.run("alpha",run,tools)["state"],"AWAITING_APPROVAL")
        self.assertEqual(tools.writes,0)
        self.engine.approve("alpha",run,"issue")
        self.assertEqual(self.engine.run("alpha",run,tools)["state"],"SUCCEEDED")
        self.assertEqual(tools.writes,1)
        self.assertTrue(self.engine.submit(workflow)["deduplicated"])
        self.engine.run("alpha",run,tools)
        self.assertEqual(tools.writes,1)

    def test_uncertain_write_is_never_redispatched(self):
        tools = FakeTools()
        tools.fail_after_write = True
        run = self.engine.submit(self.workflow())["run_id"]
        self.engine.run("alpha",run,tools)
        self.engine.approve("alpha",run,"issue")
        self.assertEqual(self.engine.run("alpha",run,tools)["state"],"UNCERTAIN")
        self.engine.run("alpha",run,tools)
        self.assertEqual(tools.writes,1)
        todo = self.engine.reconcile("alpha",run,"issue")
        self.assertEqual(todo["kind"],"verify")
        self.engine.record("alpha",run,"issue",todo["token"],tools.invoke(todo["invocation"]))
        self.assertEqual(self.engine.run("alpha",run,tools)["state"],"SUCCEEDED")
        self.assertEqual(tools.writes,1)

    def test_pending_native_call_has_single_use_token(self):
        run = self.engine.submit(self.workflow())["run_id"]
        todo = self.engine.next("alpha",run)
        self.assertEqual(self.engine.next("alpha",run)["state"],"AWAITING_RESULT")
        with self.assertRaises(ContractError):
            self.engine.record("alpha",run,"mail","wrong",{})
        self.engine.record("alpha",run,"mail",todo["token"],{"messages":[{"subject":"s"}]})
        with self.assertRaises(ContractError):
            self.engine.record("alpha",run,"mail",todo["token"],{})

    def test_new_chat_does_not_inherit_capability_claims(self):
        other = Operations(self.projects,self.engine.journal,"alice",session="chat-two")
        run = other.submit(self.workflow())["run_id"]
        with self.assertRaises(ContractError):
            other.next("alpha",run)

    def test_wrong_project_binding_is_rejected(self):
        workflow = self.workflow()
        workflow["steps"][1]["preflight"]["arguments"]["repo"] = "another-repo"
        run = self.engine.submit(workflow)["run_id"]
        with self.assertRaises(ContractError):
            self.engine.run("alpha",run,FakeTools())

    def test_unverified_write_and_credentials_are_rejected(self):
        workflow = self.workflow()
        del workflow["steps"][1]["verify"]
        with self.assertRaises(ContractError):
            self.engine.submit(workflow)
        workflow = self.workflow()
        workflow["steps"][0]["arguments"]["access_token"] = "not-a-real-token"
        with self.assertRaises(ContractError):
            self.engine.submit(workflow)

    def test_unknown_plugin_requires_operator_descriptor(self):
        workflow = self.workflow()
        workflow["steps"][0]["action"] = "unknown.execute"
        with self.assertRaises(ContractError):
            self.engine.submit(workflow)

    def test_newer_denial_wins(self):
        now = time.time()+1
        self.engine.capabilities.observe("alice","alpha","mail","gmail.search",self.engine.surface,self.engine.session,
            {"level":"denied","connector":"gmail","account_ref":"mail-a","tool_name":"gmail.search",
             "observed_at":now,"expires_at":now+60,"evidence_ref":"denial"})
        run = self.engine.submit(self.workflow())["run_id"]
        with self.assertRaises(ContractError):
            self.engine.next("alpha",run)
