"""Release regressions: operator enrollment and actual, verified result retrieval."""
import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from operation_contracts.common import ContractError
from fleet_operator.core import FleetConfig, HostSpec
from fleet_operator.secure_gateway import SecureRunner
from fleet_operator.remote_jobs import call
import test_fleet_jobs as fixtures


class ArtifactDeliveryTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request
    wait = fixtures.ProcessTests.wait


def test_verified_content(self):
    jobs = self.service('from pathlib import Path; Path("answer.txt").write_text("42")')
    run = jobs.submit(self.request())["run_id"]
    jobs.start("alpha", run)
    self.assertEqual(self.wait(jobs, run)["state"], "SUCCEEDED")
    output = jobs.artifact("alpha", run, "answer.txt", limit=1)
    self.assertEqual(base64.b64decode(output["data_base64"]), b"4")
    self.assertEqual(output["sha256"], hashlib.sha256(b"42").hexdigest())
    self.assertEqual(output["next_offset"], 1)
    self.assertFalse(output["eof"])
    self.assertEqual(base64.b64decode(jobs.artifact("alpha", run, "answer.txt", offset=1)["data_base64"]), b"2")
    self.assertTrue(jobs.artifact("alpha", run, "answer.txt", offset=2)["eof"])
    (jobs.config.state_dir / "runs" / run / "workspace" / "answer.txt").write_text("43")
    with self.assertRaises(ContractError):
        jobs.artifact("alpha", run, "answer.txt")

ArtifactDeliveryTests.test_verified_content = test_verified_content


class EnrollmentTests(unittest.TestCase):
    def test_enrolled_runtime_uses_gateway_mapping(self):
        host = HostSpec(alias="node", transport="local")
        launch = Mock(return_value=subprocess.CompletedProcess([], 0, '{"ok":true}', ''))
        runner = SecureRunner(FleetConfig({"node": host}), run=launch, runtimes={
            "node": {"python":sys.executable,"entrypoint":"/opt/fleet/fleet_jobs.py","config":"/opt/fleet/node.json"}})
        self.assertEqual(call(runner, "node", "node_health", {}), {"ok":True})
        self.assertEqual(launch.call_args.args[0][-1], "health")
