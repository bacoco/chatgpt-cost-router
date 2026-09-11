"""Public entry points must use the same guarded policy as the private relay."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from fleet_operator.command_policy import read_allowed, write_allowed
from fleet_operator.core import FleetConfig, FleetError, HostSpec
from fleet_operator.secure_gateway import SecureRunner
from fleet_operator.remote_jobs import call
from operation_contracts.common import ContractError


class Registry:
    def __init__(self):
        self.tools = {}

    def tool(self, **metadata):
        def register(function):
            self.tools[function.__name__] = function
            return function
        return register


class GatewayDeliveryTests(unittest.TestCase):
    def test_relative_and_unbounded_commands_refused(self):
        for argv in [['./uname'], ['../git','status'], ['/tmp/git','status'],
                     ['git','diff','--output=/tmp/x'], ['git','diff','--out=/tmp/x'],
                     ['git','log','--format=%H'], ['hostname','new-name'], ['python3','-c','print(1)']]:
            with self.subTest(argv=argv):
                self.assertFalse(read_allowed(argv))
        self.assertFalse(write_allowed(['git','pull','--ff-only']))
        self.assertTrue(read_allowed(['/usr/bin/git','status','--short','--branch']))

    def test_absolute_git_has_disabled_hooks_and_textconv(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = HostSpec('node', transport='local', allowed_roots=(tmp,), read_commands=frozenset({'git'}))
            launch = Mock(return_value=subprocess.CompletedProcess([],0,b'clean',b''))
            runner = SecureRunner(FleetConfig({'node':host}),run=launch)
            runner.execute('node',['/usr/bin/git','show','HEAD'],cwd=tmp,mode='read')
            argv = launch.call_args.args[0]
            self.assertIn('core.hooksPath=/dev/null',argv)
            self.assertIn('--no-textconv',argv)
            self.assertIn('--no-ext-diff',argv)

    def test_local_cwd_symlink_escape_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            (Path(tmp)/'escape').symlink_to(other,target_is_directory=True)
            runner = SecureRunner(FleetConfig({'n':HostSpec('n',transport='local',allowed_roots=(tmp,),read_commands=frozenset({'git'}))}))
            with self.assertRaises(FleetError):
                runner.execute('n',['git','status'],cwd=tmp+'/escape',mode='read')

    def test_default_mcp_uses_guarded_runner_and_typed_jobs(self):
        from fleet_operator import mcp_server
        registry, runner = Registry(), Mock()
        with patch.object(mcp_server,'new_server',return_value=registry), \
             patch.object(mcp_server,'annotations',return_value={}), \
             patch('fleet_operator.gateway_jobs.annotations',return_value={}), \
             patch.object(mcp_server,'configured_runner',return_value=runner) as configured:
            mcp_server.build_server('/operator/config.json')
            registry.tools['fleet_exec_read']('node',['uname'])
            configured.assert_called_with('/operator/config.json')
            self.assertTrue({'fleet_submit','fleet_start','fleet_status','fleet_cancel','fleet_artifact','fleet_reconcile'} <= registry.tools.keys())

    def test_lifecycle_denies_unenrolled_and_root_hosts(self):
        for host in [HostSpec('n',transport='local'),HostSpec('n',ssh_target='root@fixture')]:
            runner = SecureRunner(FleetConfig({'n':host}))
            with self.assertRaises(ContractError):
                call(runner,'n','node_health',{})

    def test_artifact_bytes_never_enter_github_relay(self):
        from fleet_operator.relay_service import ACTIONS, execute_job
        from fleet_operator.relay import RelayError
        self.assertNotIn('process_artifact',ACTIONS)
        with self.assertRaises(RelayError):
            execute_job(Mock(),{'host':'n','action':'process_artifact','args':{}})

    def test_supervisor_setup_error_cleans_owned_child(self):
        from fleet_operator.jobs.monitor import monitor
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.Popen(['/bin/sleep','15'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:
                with patch('fleet_operator.jobs.monitor.os.set_blocking',side_effect=OSError('fixture')):
                    with self.assertRaises(OSError):
                        monitor(proc,Mock(),{'request':{'deadline':1e12}},'token',Path(tmp),
                                {'timeout_seconds':20,'max_output_bytes':1024,'isolation':'trusted-local'})
                self.assertIsNotNone(proc.poll())
            finally:
                if proc.poll() is None:
                    proc.kill(); proc.wait()
                proc.stdout.close(); proc.stderr.close()
