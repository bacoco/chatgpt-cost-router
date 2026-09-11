"""Failure injection on A, without using any real external connector or model."""
import os
from copy import deepcopy
import time
import unittest
from unittest.mock import patch
from operation_contracts.common import ContractError, load, loads
from operation_contracts.journal import Journal
import test_chat_operations as fixtures


class RecoveryTests(unittest.TestCase):
    setUp = fixtures.ChatOperationsTests.setUp
    tearDown = fixtures.ChatOperationsTests.tearDown
    workflow = fixtures.ChatOperationsTests.workflow

    def pending_write(self, workflow=None):
        tools = fixtures.FakeTools()
        run = self.engine.submit(workflow or self.workflow())["run_id"]
        self.engine.run("alpha", run, tools)
        self.engine.approve("alpha", run, "issue")
        todo = self.engine.next("alpha", run)
        self.assertEqual(todo["kind"], "call")
        return run, tools, todo

    def test_failed_preflight_is_retried_as_read_not_skipped(self):
        run = self.engine.submit(self.workflow())["run_id"]
        first = self.engine.next("alpha", run)
        self.engine.record("alpha", run, "mail", first["token"], {"messages":[{"subject":"x"}]})
        before = self.engine.next("alpha", run)
        self.assertEqual(before["kind"], "preflight")
        self.engine.record("alpha", run, "issue", before["token"], {}, error=True)
        read = self.engine.reconcile("alpha", run, "issue")
        self.assertEqual(read["kind"], "preflight")
        self.engine.record("alpha", run, "issue", read["token"], {"count":0})
        self.assertEqual(self.engine.next("alpha", run)["state"], "AWAITING_APPROVAL")

    def test_readback_can_complete_after_deadline_without_replaying_write(self):
        flow = self.workflow()
        run, tools, todo = self.pending_write(flow)
        output = tools.invoke(todo["invocation"])
        self.engine.record("alpha", run, "issue", todo["token"], output)
        with patch("chat_ops.engine.time.time", return_value=flow["deadline"]+1):
            self.assertEqual(self.engine.next("alpha", run)["state"], "UNCERTAIN")
            read = self.engine.reconcile("alpha", run, "issue")
            self.assertTrue(read["invocation"]["read_only"])
            self.engine.record("alpha", run, "issue", read["token"], tools.invoke(read["invocation"]))
            self.assertEqual(self.engine.next("alpha", run)["state"], "SUCCEEDED")
        self.assertEqual(tools.writes, 1)

    def test_lost_created_id_is_recovered_using_bound_read(self):
        flow = self.workflow()
        step = flow["steps"][1]
        step["verify"]["arguments"] = deepcopy(step["verify"]["arguments"])
        step["verify"]["arguments"]["id"] = {"$ref":"issue.id"}
        step["recovery"] = {"action":"github.search","arguments":{"owner":"example","repo":"alpha"},"expect":{"count":1}}
        run, tools, todo = self.pending_write(flow)
        tools.invoke(todo["invocation"])
        self.engine.record("alpha", run, "issue", todo["token"], {}, error=True)
        recovery = self.engine.reconcile("alpha", run, "issue")
        self.assertEqual(recovery["kind"], "recovery")
        self.engine.record("alpha", run, "issue", recovery["token"], tools.invoke(recovery["invocation"]))
        self.assertEqual(self.engine.run("alpha", run, tools)["state"], "SUCCEEDED")
        self.assertEqual(tools.writes, 1)

    def test_missing_recovery_identity_fails_closed(self):
        flow = self.workflow()
        flow["steps"][1]["verify"]["arguments"] = deepcopy(flow["steps"][1]["verify"]["arguments"])
        flow["steps"][1]["verify"]["arguments"]["id"] = {"$ref":"issue.id"}
        run, tools, todo = self.pending_write(flow)
        self.engine.record("alpha", run, "issue", todo["token"], {}, error=True)
        with self.assertRaises(ContractError):
            self.engine.reconcile("alpha", run, "issue")
        self.assertEqual(tools.writes, 0)

    def test_cancel_pending_read_does_not_allow_following_write(self):
        run = self.engine.submit(self.workflow())["run_id"]
        todo = self.engine.next("alpha", run)
        self.assertEqual(self.engine.cancel("alpha", run)["state"], "UNCERTAIN")
        self.engine.record("alpha", run, "mail", todo["token"], {"messages":[{"subject":"x"}]})
        self.assertEqual(self.engine.next("alpha", run)["state"], "CANCELLED")

    def test_cancellation_is_fenced_at_mutation_claim(self):
        tools = fixtures.FakeTools()
        run = self.engine.submit(self.workflow())["run_id"]
        self.engine.run("alpha", run, tools)
        self.engine.approve("alpha", run, "issue")
        invoke = self.engine.invocation
        def racing(*args):
            value = invoke(*args)
            if not value["read_only"]:
                self.engine.cancel("alpha", run)
            return value
        with patch.object(self.engine, "invocation", side_effect=racing), self.assertRaises(ContractError):
            self.engine.next("alpha", run)
        self.assertEqual(tools.writes, 0)

    def test_cancelled_uncertain_write_is_only_reconciled_by_read(self):
        run, tools, todo = self.pending_write()
        tools.invoke(todo["invocation"])
        self.engine.cancel("alpha", run)
        read = self.engine.reconcile("alpha", run, "issue")
        self.engine.record("alpha", run, "issue", read["token"], tools.invoke(read["invocation"]))
        self.assertEqual(self.engine.next("alpha", run)["state"], "CANCELLED")
        self.assertEqual(tools.writes, 1)

    def test_late_reply_cannot_overwrite_new_read_token(self):
        run, tools, todo = self.pending_write()
        read = self.engine.reconcile("alpha", run, "issue")
        with self.assertRaises(ContractError):
            self.engine.record("alpha", run, "issue", todo["token"], {"id":42})
        self.assertNotEqual(read["token"], todo["token"])

    def test_ungranted_later_action_is_rejected_before_any_work(self):
        flow = self.workflow()
        flow["steps"][1]["action"] = "github.write"
        with self.assertRaises(ContractError):
            self.engine.submit(flow)

    def test_recovery_cannot_be_a_write(self):
        flow = self.workflow()
        flow["steps"][1]["recovery"] = {"action":"github.issue.create","arguments":{},"expect":{"id":42}}
        with self.assertRaises(ContractError):
            self.engine.submit(flow)

    def test_events_are_project_scoped(self):
        run = self.engine.submit(self.workflow())["run_id"]
        self.assertTrue(self.engine.events("alpha", run)["events"])
        with self.assertRaises(ContractError):
            self.engine.events("beta", run)
        with self.assertRaises(ContractError):
            self.engine.events("alpha", run, after=-1)

    def test_journal_is_private_at_creation_and_refuses_symlink(self):
        path = self.engine.journal.path
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        link = path.parent / "linked.db"
        link.symlink_to(path)
        with self.assertRaises(ContractError):
            Journal(link)

    def test_utf8_byte_limit_and_nonregular_json(self):
        with self.assertRaises(ContractError):
            loads('"'+("é"*600000)+'"')
        fifo = self.engine.journal.path.parent / "fifo"
        os.mkfifo(fifo, 0o600)
        with self.assertRaises(ContractError):
            load(fifo)

    def test_other_session_cannot_record_pending_native_output(self):
        from chat_ops.engine import Operations
        run = self.engine.submit(self.workflow())["run_id"]
        todo = self.engine.next("alpha",run)
        other = Operations(self.projects,self.engine.journal,"alice",session="another-conversation")
        with self.assertRaises(ContractError):
            other.record("alpha",run,"mail",todo["token"],{"messages":[]})
        self.engine.record("alpha",run,"mail",todo["token"],{"messages":[{"subject":"ok"}]})

    def test_verified_output_mapping_unblocks_downstream_without_replay(self):
        flow = self.workflow()
        flow["steps"][1]["verify"]["recover_output"] = {"id":{"$ref":"verification.id"},"title":{"$ref":"verification.title"}}
        flow["steps"].append({"id":"followup","resource":"mail","action":"gmail.read","arguments":{"message_id":{"$ref":"issue.id"}}})
        run, tools, todo = self.pending_write(flow)
        tools.invoke(todo["invocation"])
        self.engine.record("alpha",run,"issue",todo["token"],{},error=True)
        read = self.engine.reconcile("alpha",run,"issue")
        self.engine.record("alpha",run,"issue",read["token"],tools.invoke(read["invocation"]))
        self.assertEqual(self.engine.run("alpha",run,tools)["state"],"SUCCEEDED")
        self.assertEqual(self.engine.outputs(self.engine.row("alpha",run))["issue"]["id"],42)
        self.assertEqual(tools.writes,1)

    def test_recover_output_cannot_reference_future_or_unobserved_result(self):
        flow = self.workflow()
        flow["steps"][1]["verify"]["recover_output"] = {"id":{"$ref":"unobserved.id"}}
        with self.assertRaises(ContractError):
            self.engine.submit(flow)
