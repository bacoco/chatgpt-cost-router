"""Power-loss/publication failure simulations with local private receipts."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from operation_contracts.common import ContractError
from operation_contracts.files import atomic_json
from fleet_operator.outbox import Outbox, relay_lock
from fleet_operator.relay import RelayConfig
from fleet_operator.relay_service import run_once, receipt_status
import test_fleet_operator_relay as fixtures


class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.box = Outbox(self.root/"state")
        self.job, self.sha = "job-outbox-test-001", "a"*64
        self.receipt = {"version":1,"job_id":self.job,"job_sha256":self.sha,"status":"PASS","result":{"exit_code":0}}

    def tearDown(self):
        self.temp.cleanup()

    def test_atomic_receipt_is_preserved_after_sql_interruption(self):
        self.box.claim(self.job,self.sha)
        atomic_json(self.root/"state/results"/(self.job+".json"),self.receipt)
        self.assertEqual(self.box.recover(self.job,self.sha),self.receipt)
        self.assertEqual(self.box.get(self.job)["state"],"RESULT")

    def test_claim_without_receipt_becomes_uncertain_and_cannot_reclaim(self):
        self.assertTrue(self.box.claim(self.job,self.sha))
        self.assertEqual(self.box.recover(self.job,self.sha)["status"],"UNCERTAIN")
        self.assertFalse(self.box.claim(self.job,self.sha))

    def test_conflicting_receipt_or_payload_never_overwrites_evidence(self):
        self.box.claim(self.job,self.sha)
        self.box.save(self.job,self.sha,self.receipt)
        with self.assertRaises(ContractError):
            self.box.save(self.job,self.sha,{**self.receipt,"status":"FAILED"})
        with self.assertRaises(ContractError):
            self.box.claim(self.job,"b"*64)
        self.assertEqual(self.box.get(self.job)["result"],self.receipt)

    def test_connection_is_closed_on_success_and_error(self):
        import sqlite3
        with self.box.connect() as db:
            self.assertEqual(db.execute("SELECT 1").fetchone()[0],1)
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute("SELECT 1")
        with self.assertRaises(ValueError):
            with self.box.connect() as db:
                raise ValueError("injected")
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute("SELECT 1")

    def test_dispatch_lock_excludes_concurrent_relay(self):
        with relay_lock(self.root):
            with self.assertRaises(ContractError):
                with relay_lock(self.root):
                    self.fail("lock was not exclusive")

    def test_outbox_delivery_does_not_need_job_file_or_node_config(self):
        self.box.claim(self.job,self.sha)
        self.box.save(self.job,self.sha,self.receipt)
        repo = self.root/"repo"
        (repo/".git").mkdir(parents=True)
        config = RelayConfig(repo=repo,fleet_config=self.root/"missing.json",state_dir=self.root/"state")
        bus = fixtures.FakeBus({})
        with patch("fleet_operator.relay_service.configured_runner",side_effect=AssertionError("must not execute")):
            result = run_once(config,bus=bus)
        self.assertEqual(result[0]["status"],"PASS")
        self.assertEqual(len(bus.pushes),1)
        self.assertEqual(self.box.get(self.job)["state"],"PUBLISHED")

    def test_failed_publication_is_retried_without_execution(self):
        self.box.claim(self.job,self.sha)
        self.box.save(self.job,self.sha,self.receipt)
        repo = self.root/"repo"
        (repo/".git").mkdir(parents=True)
        config = RelayConfig(repo=repo,fleet_config=self.root/"missing.json",state_dir=self.root/"state")
        bus = fixtures.FakeBus({})
        with patch.object(bus,"push_result",side_effect=OSError("offline")):
            first = run_once(config,bus=bus)
        self.assertIn("result_push_error",first[0])
        self.assertEqual(self.box.get(self.job)["state"],"RESULT")
        self.assertEqual(run_once(config,bus=bus)[0]["status"],"PASS")
        self.assertEqual(len(bus.pushes),1)

    def test_nonterminal_acceptance_is_not_success(self):
        for state in ("QUEUED","RUNNING","CANCELLING"):
            self.assertEqual(receipt_status({"state":state}),"ACCEPTED")
        self.assertEqual(receipt_status({"state":"UNCERTAIN"}),"UNCERTAIN")
