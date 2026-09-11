import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from operation_contracts.common import ContractError
from fleet_operator.jobs.config import NodeConfig
from fleet_operator.jobs.service import Jobs
from fleet_operator.jobs.command import command


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.projects = self.root / "projects.json"
        self.projects.write_text(json.dumps({"version":1,"projects":{
            "alpha":{"members":["alice"],"nodes":["node-a"],"profiles":["run"]},
            "beta":{"members":["bob"],"nodes":["node-a"],"profiles":["run"]}}}))
        self.config_path = self.root / "node.json"

    def tearDown(self):
        self.tmp.cleanup()

    def service(self, code, timeout=5, limit=4096, source=None):
        profile = {"argv":[sys.executable,"-c",code],"isolation":"trusted-local",
                   "timeout_seconds":timeout,"max_output_bytes":limit,"artifacts":["answer.txt"]}
        doc = {"version":1,"node_id":"node-a","principal":"alice","state_dir":str(self.root/"state"),
               "projects_file":str(self.projects),"profiles":{"run":profile},"max_concurrency":2,
               "runtime_revision":"unit-test-revision"}
        if source:
            doc["repositories"] = {"alpha":{"slug":"example/alpha","path":str(source)}}
        self.config_path.write_text(json.dumps(doc))
        return Jobs(NodeConfig.from_file(self.config_path))

    def request(self):
        return {"version":1,"project_id":"alpha","idempotency_key":"one-run","node_id":"node-a",
                "profile":"run","inputs":{"answer":42},"deadline":time.time()+30}

    def wait(self, service, id_, states=None):
        states = states or {"SUCCEEDED","FAILED","CANCELLED","TIMED_OUT","BLOCKED","UNCERTAIN"}
        deadline = time.monotonic()+12
        while time.monotonic() < deadline:
            out = service.status("alpha",id_)
            if out["state"] in states:
                return out
            time.sleep(0.05)
        self.fail("bounded process test did not finish")

    def test_real_process_result_progress_and_deduplication(self):
        service = self.service('from pathlib import Path; print(\'FLEET_PROGRESS {"current":1,"total":1}\'); Path("answer.txt").write_text("42"); print("DONE")')
        request = self.request()
        run = service.submit(request)["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"SUCCEEDED")
        result = service.result("alpha",run)
        self.assertEqual(result["artifacts"][0]["name"],"answer.txt")
        self.assertTrue(result["receipt_digest"])
        self.assertIn("DONE",service.logs("alpha",run)["text"])
        self.assertTrue(service.submit(request)["deduplicated"])
        self.assertEqual(service.start("alpha",run)["state"],"SUCCEEDED")

    def test_real_timeout(self):
        service = self.service('import time; time.sleep(10)',timeout=1)
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"TIMED_OUT")

    def test_running_cancellation(self):
        service = self.service('import time; print("START",flush=True); time.sleep(10)')
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        time.sleep(0.25)
        service.cancel("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"CANCELLED")

    def test_cancel_before_start_does_not_spawn(self):
        service = self.service('raise RuntimeError("must not execute")')
        run = service.submit(self.request())["run_id"]
        self.assertEqual(service.cancel("alpha",run)["state"],"CANCELLED")
        self.assertEqual(service.start("alpha",run)["state"],"CANCELLED")
        self.assertFalse((service.config.state_dir/"runs"/run).exists())

    def test_logs_are_bounded(self):
        service = self.service('print("x"*20000)',limit=1024)
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"SUCCEEDED")
        self.assertEqual(len(service.logs("alpha",run)["text"]),1024)
        self.assertTrue(service.result("alpha",run)["output_truncated"])

    def test_paid_environment_is_not_inherited(self):
        service = self.service('import os; assert "OPENAI_API_KEY" not in os.environ; assert "ANTHROPIC_API_KEY" not in os.environ; print("CLEAN")')
        from unittest.mock import patch
        with patch.dict(os.environ,{"OPENAI_API_KEY":"test-only","ANTHROPIC_API_KEY":"test-only"}):
            run = service.submit(self.request())["run_id"]
            service.start("alpha",run)
            self.assertEqual(self.wait(service,run)["state"],"SUCCEEDED")

    def test_foreign_project_and_command_injection_rejected(self):
        service = self.service('print("OK")')
        request = self.request()
        request["project_id"] = "beta"
        with self.assertRaises(ContractError):
            service.submit(request)
        request = self.request()
        request["argv"] = ["sh","-c","echo forbidden"]
        with self.assertRaises(ContractError):
            service.submit(request)
        request = self.request()
        request["node_id"] = "other-node"
        with self.assertRaises(ContractError):
            service.submit(request)

    def test_fixed_sha_does_not_modify_dirty_checkout(self):
        repo = self.root / "repo"
        repo.mkdir()
        for args in [["init","-q"],["config","user.name","Fixture"],["config","user.email","fixture@localhost"],
                     ["remote","add","origin","https://github.com/example/alpha.git"]]:
            subprocess.run(["git",*args],cwd=repo,check=True,capture_output=True)
        (repo/"source.txt").write_text("pinned")
        subprocess.run(["git","add","."],cwd=repo,check=True)
        subprocess.run(["git","commit","-qm","fixture"],cwd=repo,check=True)
        sha = subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
        (repo/"source.txt").write_text("uncommitted")
        service = self.service('from pathlib import Path; assert Path("source.txt").read_text()=="pinned"',source=repo)
        request = self.request()
        request["source"] = {"repo":"example/alpha","sha":sha}
        run = service.submit(request)["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"SUCCEEDED")
        self.assertEqual((repo/"source.txt").read_text(),"uncommitted")

    def test_stale_claim_is_uncertain_not_replayed(self):
        service = self.service('print("MUST NOT EXECUTE")')
        run = service.submit(self.request())["run_id"]
        service.journal.transition(run,{"QUEUED"},"RUNNING",{"heartbeat":time.time()-300,"token":"old"})
        self.assertEqual(service.recover_stale(),[run])
        self.assertEqual(service.start("alpha",run)["state"],"UNCERTAIN")

    def test_log_path_is_not_a_request_parameter(self):
        service = self.service('print("OK")')
        run = service.submit(self.request())["run_id"]
        with self.assertRaises(ContractError):
            service.logs("alpha",run,"../../private")
