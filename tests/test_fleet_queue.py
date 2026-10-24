"""Queue authorization regressions using only temporary state and local Python jobs."""
import json
import unittest
from unittest.mock import patch

from fleet_operator.jobs.config import NodeConfig
from fleet_operator.jobs.service import Jobs
from fleet_operator.jobs.workspace import root_for
from operation_contracts.common import ContractError
import test_fleet_jobs as fixtures


class QueueTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request
    wait = fixtures.ProcessTests.wait

    def revoked_queue(self, revoke):
        projects = json.loads(self.projects.read_text())
        projects["projects"]["beta"]["members"].append("alice")
        self.projects.write_text(json.dumps(projects))
        service = self.service('from pathlib import Path; Path("answer.txt").write_text("42")')
        stale = service.submit({**self.request(), "project_id": "beta"})["run_id"]
        revoke(projects["projects"])
        self.projects.write_text(json.dumps(projects))
        changed = Jobs(NodeConfig.from_file(self.config_path))
        valid = changed.submit(self.request())["run_id"]
        return changed, stale, valid

    def assert_queue_continues(self, service, stale, valid, reason):
        service.start_pending()
        row = service.journal.get("alice", "beta", stale)
        self.assertEqual(row["state"], "BLOCKED")
        self.assertEqual(row["data"]["reason"], reason)
        self.assertFalse(root_for(service.config, stale).exists())
        self.assertEqual(self.wait(service, valid)["state"], "SUCCEEDED")
        self.assertEqual(service.result("alpha", valid)["artifacts"][0]["name"], "answer.txt")
        service.start_pending()
        self.assertEqual(service.journal.get("alice", "beta", stale), row)

    def assert_project_revocation(self, revoke):
        service, stale, valid = self.revoked_queue(revoke)
        for method in (service.row, service.start):
            with self.assertRaises(ContractError):
                method("beta", stale)
        self.assertEqual(service.journal.get("alice", "beta", stale)["state"], "QUEUED")
        self.assert_queue_continues(service, stale, valid, "project authorization revoked before start")
        for method in (service.row, service.start):
            with self.assertRaises(ContractError):
                method("beta", stale)

    def test_removed_project_does_not_block_later_valid_job(self):
        self.assert_project_revocation(lambda projects: projects.pop("beta"))

    def test_revoked_membership_does_not_block_later_valid_job(self):
        self.assert_project_revocation(lambda projects: projects["beta"]["members"].remove("alice"))

    def test_revoked_node_uses_existing_policy_block(self):
        service, stale, valid = self.revoked_queue(lambda projects: projects["beta"]["nodes"].clear())
        self.assert_queue_continues(service, stale, valid, "operator policy changed")

    def test_revoked_profile_uses_existing_policy_block(self):
        service, stale, valid = self.revoked_queue(lambda projects: projects["beta"]["profiles"].clear())
        self.assert_queue_continues(service, stale, valid, "operator policy changed")

    def test_start_errors_propagate(self):
        service = self.service('raise RuntimeError("must not run")')
        run = service.submit(self.request())["run_id"]
        for error in (RuntimeError("start failure"), ContractError("unrelated contract failure")):
            with self.subTest(error=type(error).__name__):
                with patch.object(service, "start", side_effect=error) as start:
                    with self.assertRaises(type(error)) as caught:
                        service.start_pending()
                self.assertIs(caught.exception, error)
                start.assert_called_once_with("alpha", run)
                self.assertEqual(service.row("alpha", run)["state"], "QUEUED")

    def test_quarantine_storage_errors_propagate(self):
        service, stale, valid = self.revoked_queue(lambda projects: projects.pop("beta"))
        for error in (OSError("journal failure"), ContractError("journal contract failure")):
            with self.subTest(error=type(error).__name__):
                with patch.object(service.journal, "transition", side_effect=error) as transition:
                    with self.assertRaises(type(error)) as caught:
                        service.start_pending()
                self.assertIs(caught.exception, error)
                transition.assert_called_once_with(stale, {"QUEUED"}, "BLOCKED",
                                                   {"reason": "project authorization revoked before start"})
                self.assertEqual(service.journal.get("alice", "beta", stale)["state"], "QUEUED")
                self.assertEqual(service.row("alpha", valid)["state"], "QUEUED")
