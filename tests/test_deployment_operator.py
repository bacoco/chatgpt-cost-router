"""Deployment boundaries that can be checked without contacting an owner machine."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import test_enrollment_local as fixtures
from fleet_operator.enrollment import releases

ROOT=Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    out=importlib.util.module_from_spec(spec); spec.loader.exec_module(out); return out

class DeploymentTests(unittest.TestCase):
    def test_all_python_sources_compile(self):
        for folder in ['scripts','fleet_operator','chat_ops','operation_contracts','cost_router']:
            for path in (ROOT/folder).rglob('*.py'):
                with self.subTest(path=path): compile(path.read_text(),str(path),'exec')
    def test_deployment_profiles_validate_and_real_smoke(self):
        import tempfile
        from fleet_operator.jobs.config import NodeConfig
        installer=module('ab_host_install')
        with tempfile.TemporaryDirectory() as temp:
            config=installer.configure(Path(temp),'a'*40,'fixture',Path(sys.executable))
            node=NodeConfig.from_file(config/'node.json')
            self.assertEqual(set(node.profiles),{'smoke','validate-release'})
            result=installer.smoke(config,'a'*40)
            self.assertTrue(result['artifact_verified'])
            self.assertEqual(result['cancel_state'],'CANCELLED')
    def test_unconfigured_host_refused(self):
        with self.assertRaises(KeyError): module('ab_fleet_deploy').wire({'hosts':{}},'unknown',['uname'])
    def test_root_host_refused(self):
        with self.assertRaises(ValueError):
            module('ab_fleet_deploy').wire({'hosts':{'node':{'ssh_target':'root@fixture'}}},'node',['uname'])
    def test_ssh_checks_host_key_and_disables_forwarding(self):
        argv=module('ab_fleet_deploy').wire({'hosts':{'node':{'ssh_target':'owner@fixture'}}},'node',['python3','/safe/script.py'])
        self.assertIn('StrictHostKeyChecking=yes',argv); self.assertIn('ForwardAgent=no',argv)
    def test_local_does_not_spawn_ssh(self):
        self.assertEqual(module('ab_fleet_deploy').wire({'hosts':{'node':{'transport':'local'}}},'node',['uname']),['uname'])
    def test_disabled_host_refused(self):
        with self.assertRaises(ValueError):
            module('ab_fleet_deploy').wire({'hosts':{'node':{'enabled':False}}},'node',['uname'])

class VirtualenvActivationTests(unittest.TestCase):
    setUp=fixtures.EnrollmentTests.setUp
    tearDown=fixtures.EnrollmentTests.tearDown
    service=fixtures.EnrollmentTests.service
    stage=fixtures.EnrollmentTests.stage
    def test_activation_keeps_virtualenv_symlink_path(self):
        _,store,revision,_=self.stage()
        executable=self.root/'venv/bin/python'; executable.parent.mkdir(parents=True)
        executable.symlink_to(sys.executable)
        result=releases.activation(store,revision,self.config_path,str(executable),apply=True)
        self.assertEqual(result['record']['python'],str(executable))
        self.assertEqual(releases.prepare_active(store/'active.json')[0],str(executable))
