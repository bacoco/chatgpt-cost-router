"""Local process and persistence failures; never enqueues work on the real fleet."""
import base64
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
import time
import unittest
from unittest.mock import patch
from operation_contracts.common import ContractError
from operation_contracts.journal import Journal
from fleet_operator.jobs.worker import execute
from fleet_operator.jobs.workspace import root_for
import test_fleet_jobs as fixtures


class ProcessRecoveryTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request
    wait = fixtures.ProcessTests.wait

    def claim(self, service):
        id_ = service.submit(self.request())["run_id"]
        service.journal.transition(id_, {"QUEUED"}, "RUNNING", {"token":"test-owner","heartbeat":time.time()})
        return id_

    def test_two_supervisors_cannot_spawn_the_same_job(self):
        marker = self.root / "count"
        service = self.service(f'from pathlib import Path; import time; time.sleep(.1); Path({str(marker)!r}).open("a").write("1")')
        run = self.claim(service)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _:execute(service.config,"alpha",run,"test-owner"),range(2)))
        self.assertEqual(results,[0,0])
        self.assertEqual(marker.read_text(),"1")
        self.assertEqual(service.status("alpha",run)["state"],"SUCCEEDED")

    def test_saved_process_receipt_recovers_sql_failure_without_rerun(self):
        service = self.service('from pathlib import Path; Path("answer.txt").write_text("42")')
        run = self.claim(service)
        original = Journal.transition
        def fail_once(journal, id_, expected, new, *args, **kwargs):
            if new == "SUCCEEDED":
                raise OSError("injected failure after receipt fsync")
            return original(journal,id_,expected,new,*args,**kwargs)
        with patch.object(Journal,"transition",new=fail_once):
            execute(service.config,"alpha",run,"test-owner")
        self.assertEqual(service.status("alpha",run)["state"],"UNCERTAIN")
        self.assertTrue((root_for(service.config,run)/"result.json").exists())
        self.assertEqual(service.reconcile("alpha",run)["state"],"SUCCEEDED")
        self.assertEqual(service.start("alpha",run)["state"],"SUCCEEDED")

    def test_artifact_chunks_and_digest_drift(self):
        service = self.service('from pathlib import Path; Path("answer.txt").write_text("0123456789")')
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"SUCCEEDED")
        chunk = service.artifact("alpha",run,"answer.txt",offset=2,limit=4)
        self.assertEqual(base64.b64decode(chunk["data"]),b"2345")
        self.assertEqual(chunk["next_offset"],6)
        self.assertFalse(chunk["eof"])
        (root_for(service.config,run)/"workspace/answer.txt").write_text("tampered")
        with self.assertRaises(ContractError):
            service.artifact("alpha",run,"answer.txt")

    def test_artifact_symlink_and_unknown_name_refused(self):
        service = self.service('from pathlib import Path; Path("answer.txt").write_text("ok")')
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        self.wait(service,run)
        with self.assertRaises(ContractError):
            service.artifact("alpha",run,"../../node.json")
        output = root_for(service.config,run)/"workspace/answer.txt"
        output.unlink()
        output.symlink_to(self.config_path)
        with self.assertRaises((ContractError,OSError)):
            service.artifact("alpha",run,"answer.txt")

    def test_concurrent_submission_is_idempotent(self):
        service = self.service('print("no automatic start")')
        request = self.request()
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(lambda _:service.submit(request),range(16)))
        self.assertEqual(len({row["run_id"] for row in rows}),1)
        self.assertEqual(sum(not row["deduplicated"] for row in rows),1)
        self.assertEqual(service.health()["jobs_by_state"]["QUEUED"],1)

    def test_stale_recovery_is_not_limited_to_last_200_jobs(self):
        service = self.service('print("must not run")')
        run = self.claim(service)
        service.journal.transition(run,{"RUNNING"},"RUNNING",{"heartbeat":time.time()-20})
        for n in range(205):
            service.submit({**self.request(),"idempotency_key":"later-"+str(n)})
        self.assertIn(run,service.recover_stale(age=5))
        self.assertEqual(service.status("alpha",run)["state"],"UNCERTAIN")

    def test_live_metrics_are_observed_and_node_capacity_is_reported(self):
        service = self.service('import time; print("START",flush=True); time.sleep(2)')
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        until = time.monotonic()+5
        while time.monotonic() < until:
            status = service.status("alpha",run)
            if status["metrics"] is not None:
                break
            time.sleep(.05)
        self.assertIsNotNone(status["metrics"])
        if sys.platform == "linux":
            self.assertGreaterEqual(status["metrics"]["rss_bytes"],0)
            self.assertGreaterEqual(status["metrics"]["cpu_seconds"],0)
        self.assertGreater(service.health()["disk_free_bytes"],0)
        service.cancel("alpha",run)
        self.wait(service,run)

    def test_foreground_parent_cannot_leave_pipe_holding_descendant(self):
        code = 'import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(20)"]); print(p.pid,flush=True)'
        service = self.service(code,timeout=6)
        run = service.submit(self.request())["run_id"]
        service.start("alpha",run)
        self.assertEqual(self.wait(service,run)["state"],"UNCERTAIN")
        child = int(service.logs("alpha",run)["text"].strip())
        if sys.platform == "linux":
            from pathlib import Path
            status = Path(f"/proc/{child}/stat")
            self.assertTrue(not status.exists() or status.read_text().rsplit(")",1)[1].split()[0] == "Z")

    def test_changed_policy_blocks_queued_execution(self):
        service = self.service('raise RuntimeError("must not run")')
        run = service.submit(self.request())["run_id"]
        current = json.loads(self.projects.read_text())
        current["projects"]["alpha"]["description"] = "policy revision"
        self.projects.write_text(json.dumps(current))
        from fleet_operator.jobs.service import Jobs
        from fleet_operator.jobs.config import NodeConfig
        changed = Jobs(NodeConfig.from_file(self.config_path))
        self.assertEqual(changed.start("alpha",run)["state"],"BLOCKED")
