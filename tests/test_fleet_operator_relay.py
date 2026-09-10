import json
import tempfile
import unittest
from pathlib import Path

from fleet_operator.core import FleetConfig, FleetRunner
from fleet_operator.relay import RelayConfig, RelayError, execute_job, run_once, validate_job


class FakeBus:
    def __init__(self,jobs): self.jobs=jobs; self.pushes=[]
    def fetch(self): pass
    def list_jobs(self): return list(self.jobs)
    def read_job(self,path): return self.jobs[path],"a"*64
    def push_result(self,job_id,payload): self.pushes.append((job_id,payload)); return "fleet/results/"+job_id


class RelayTests(unittest.TestCase):
    def test_job_filename_and_expiry_are_enforced(self):
        job={"version":1,"job_id":"job-12345678","host":"h","action":"status","args":{},"expires_at_unix":1100}; validate_job(job,path=".fleet/jobs/job-12345678.json",now=1000)
        with self.assertRaises(RelayError): validate_job(job,path=".fleet/jobs/other.json",now=1000)
        with self.assertRaises(RelayError): validate_job({**job,"expires_at_unix":999},path=".fleet/jobs/job-12345678.json",now=1000)
        with self.assertRaises(RelayError): validate_job({**job,"expires_at_unix":91000},path=".fleet/jobs/job-12345678.json",now=1000)

    def test_exec_read_cannot_smuggle_destructive_flag(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fleet.json"; p.write_text(json.dumps({"version":1,"hosts":{"local":{"transport":"local","read_commands":["uname"],"write_commands":[]}}})); runner=FleetRunner(FleetConfig.load(p)); job={"host":"local","action":"exec_read","args":{"argv":["uname","-a"],"allow_destructive":True}}
            with self.assertRaises(RelayError): execute_job(runner,job)

    def test_run_once_executes_and_replay_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo=root/"repo"; (repo/".git").mkdir(parents=True); fleet=root/"fleet.json"; fleet.write_text(json.dumps({"version":1,"max_output_bytes":4096,"hosts":{"local":{"transport":"local","read_commands":["uname"],"write_commands":[]}}})); rcfg=RelayConfig(repo=repo,fleet_config=fleet,poll_seconds=30,state_dir=root/"state"); path=".fleet/jobs/job-abcdefgh.json"; bus=FakeBus({path:{"version":1,"job_id":"job-abcdefgh","host":"local","action":"status","args":{},"expires_at_unix":1100}}); events=run_once(rcfg,bus=bus,clock=lambda:1000); self.assertEqual(len(events),1); self.assertEqual(events[0]["status"],"PASS"); self.assertEqual(events[0]["result_branch"],"fleet/results/job-abcdefgh"); self.assertTrue((root/"state/results/job-abcdefgh.json").is_file()); self.assertEqual(run_once(rcfg,bus=bus,clock=lambda:1000),[]); self.assertEqual(len(bus.pushes),1)

    def test_bad_action_returns_error_result_not_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo=root/"repo"; (repo/".git").mkdir(parents=True); fleet=root/"fleet.json"; fleet.write_text(json.dumps({"version":1,"hosts":{"local":{"transport":"local","read_commands":["uname"]}}})); rcfg=RelayConfig(repo=repo,fleet_config=fleet,state_dir=root/"state"); path=".fleet/jobs/job-badbad99.json"; bus=FakeBus({path:{"version":1,"job_id":"job-badbad99","host":"local","action":"shell","args":{},"expires_at_unix":1100}}); events=run_once(rcfg,bus=bus,clock=lambda:1000); self.assertEqual(events[0]["status"],"ERROR"); self.assertIn("unknown relay action",events[0]["error"])


if __name__ == "__main__": unittest.main()
