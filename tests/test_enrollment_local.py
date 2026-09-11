"""Local temporary release/enrollment lifecycle. No real service installation."""
import json
import os
import plistlib
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from fleet_operator.enrollment import bindings, releases, services
from operation_contracts.common import ContractError, load
from operation_contracts.files import atomic_json
import test_fleet_jobs as fixtures


class EnrollmentTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request

    def stage(self):
        self.service('print("local release test")')
        source = Path(__file__).resolve().parents[1]
        repo = self.root / "source"
        repo.mkdir()
        for name in releases.ROOTS:
            if (source/name).exists():
                shutil.copytree(source/name, repo/name, ignore=shutil.ignore_patterns("__pycache__"))
        for args in (["init","-q"], ["config","user.name","Local test"],
                     ["config","user.email","fixture@localhost"], ["add","."], ["commit","-qm","source"]):
            subprocess.run(["git",*args], cwd=repo, check=True, capture_output=True)
        revision = subprocess.check_output(["git","rev-parse","HEAD"], cwd=repo, text=True).strip()
        store = self.root/"runtimes"
        release = releases.stage(repo,store,revision)
        return repo, store, revision, release

    def test_stage_verify_tamper_and_idempotent_stage(self):
        repo, store, rev, release = self.stage()
        self.assertEqual(releases.stage(repo,store,rev), release)
        path = Path(release["release_dir"])
        (path/"scripts/fleet_jobs.py").write_text("tampered")
        with self.assertRaises(ContractError):
            releases.verify(path)
        with self.assertRaises(ContractError):
            releases.stage(repo,store,rev)

    def test_activation_plan_apply_and_real_bootstrap_health(self):
        _, store, rev, _ = self.stage()
        plan = releases.activation(store,rev,self.config_path,sys.executable)
        self.assertFalse(plan["applied"])
        self.assertFalse((store/"active.json").exists())
        applied = releases.activation(store,rev,self.config_path,sys.executable,apply=True)
        self.assertTrue(applied["applied"])
        argv = releases.prepare_active(store/"active.json")
        out = subprocess.run([*argv,"health"], text=True, capture_output=True, check=True, timeout=15)
        reply = json.loads(out.stdout)
        self.assertEqual(reply["_node"]["runtime_revision"], rev)
        self.assertFalse(applied["services_reloaded"])

    def test_activation_refuses_queued_or_uncertain_jobs(self):
        _, store, rev, _ = self.stage()
        from fleet_operator.jobs.service import Jobs
        from fleet_operator.jobs.config import NodeConfig
        service = Jobs(NodeConfig.from_file(self.config_path))
        service.submit(self.request())
        with self.assertRaises(ContractError):
            releases.activation(store,rev,self.config_path,sys.executable,apply=True)
        self.assertFalse((store/"active.json").exists())

    def test_explicit_rollback_keeps_previous_revision(self):
        repo, store, first, _ = self.stage()
        releases.activation(store,first,self.config_path,sys.executable,apply=True)
        (repo/"scripts/revision.txt").write_text("second")
        subprocess.run(["git","add","."],cwd=repo,check=True)
        subprocess.run(["git","commit","-qm","second"],cwd=repo,check=True)
        second = subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
        releases.stage(repo,store,second)
        releases.activation(store,second,self.config_path,sys.executable,apply=True)
        rolled = releases.activation(store,first,self.config_path,sys.executable,apply=True)
        self.assertEqual(rolled["record"]["previous"],second)
        self.assertEqual(load(store/"active.json")["revision"], first)

    def gateway(self, rev):
        doc = load(self.config_path)
        doc["runtime_revision"] = rev
        atomic_json(self.config_path,doc)
        gateway = self.root/"gateway.json"
        atomic_json(gateway,{"version":1,"max_output_bytes":131072,"hosts":{
            "local":{"transport":"local","allowed_roots":[str(self.root)],"read_commands":["uname"],"write_commands":[]},
            "unchanged":{"transport":"local","allowed_roots":[str(self.root)],"read_commands":["uname"],"write_commands":[]}}})
        return gateway

    def test_plan_is_readonly_and_apply_changes_only_bound_alias(self):
        _, _, rev, release = self.stage()
        gateway = self.gateway(rev)
        before = gateway.read_bytes()
        plan = bindings.plan(gateway,"local",release["release_dir"],self.config_path,sys.executable)
        self.assertEqual(gateway.read_bytes(),before)
        result = bindings.apply(plan)
        after = load(gateway)
        self.assertEqual(after["hosts"]["unchanged"],json.loads(before)["hosts"]["unchanged"])
        self.assertEqual(after["hosts"]["local"]["runtime"]["runtime_revision"],rev)
        self.assertFalse(result["services_reloaded"])
        self.assertEqual(result["live_probe"],"NOT_RUN")

    def test_enrollment_detects_gateway_drift(self):
        _, _, rev, release = self.stage()
        gateway = self.gateway(rev)
        plan = bindings.plan(gateway,"local",release["release_dir"],self.config_path,sys.executable)
        current = load(gateway)
        current["max_output_bytes"] = 65536
        atomic_json(gateway,current)
        with self.assertRaises(ContractError):
            bindings.apply(plan)

    def test_user_service_rendering_never_installs_or_overwrites(self):
        command = [sys.executable,"/tmp/path with spaces/bootstrap.py","--config","/tmp/100%/$literal"]
        text = services.render(command,"org.fixture.fleet",platform="launchd",log_dir=str(self.root))
        self.assertEqual(plistlib.loads(text.encode())["ProgramArguments"],command)
        unit = services.render(command,"org.fixture.fleet",platform="systemd",log_dir=str(self.root))
        self.assertIn("100%%/$$literal",unit)
        self.assertIn("NoNewPrivileges=true",unit)
        out = self.root/"fixture.service"
        self.assertFalse(services.write_definition(out,unit)["installed"])
        with self.assertRaises(FileExistsError):
            services.write_definition(out,unit)
