"""Queue-revocation and SDK HTTP-start regressions; no owner-machine side effects."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from pydantic import BaseModel, ConfigDict
from fleet_operator.jobs.config import NodeConfig
from fleet_operator.jobs.service import Jobs
from operation_contracts.mcp_runtime import serve


class QueueRevocationTests(unittest.TestCase):
    def test_revoked_queued_project_does_not_block_next_valid_job(self):
        import sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            projects_path, config_path = root/'projects.json', root/'node.json'
            grant = {'members':['alice'],'nodes':['node'],'profiles':['smoke']}
            projects = {'version':1,'projects':{'revoked':grant,'valid':grant}}
            projects_path.write_text(json.dumps(projects))
            config_path.write_text(json.dumps({'version':1,'principal':'alice','node_id':'node',
                'state_dir':str(root/'state'),'projects_file':str(projects_path),
                'profiles':{'smoke':{'argv':[sys.executable,'-c','print("QUEUE_OK")'],
                    'isolation':'trusted-local','timeout_seconds':5,'max_output_bytes':1024}}}))
            old = Jobs(NodeConfig.from_file(config_path))
            def request(project):
                return {'version':1,'project_id':project,'node_id':'node','profile':'smoke',
                    'inputs':{},'idempotency_key':project,'deadline':time.time()+30}
            revoked = old.submit(request('revoked'))['run_id']
            del projects['projects']['revoked']
            projects_path.write_text(json.dumps(projects))
            current = Jobs(NodeConfig.from_file(config_path))
            valid = current.submit(request('valid'))['run_id']
            current.start_pending()
            self.assertEqual(current.journal.get('alice','revoked',revoked)['state'],'BLOCKED')
            deadline = time.monotonic()+10
            while current.status('valid',valid)['state'] in {'QUEUED','RUNNING'} and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertEqual(current.status('valid',valid)['state'],'SUCCEEDED')
            self.assertIn('QUEUE_OK',current.logs('valid',valid)['text'])

    def test_non_contract_errors_are_not_silently_masked(self):
        from unittest.mock import patch
        service = object.__new__(Jobs)
        service.config = SimpleNamespace(principal='alice')
        class DB:
            def __enter__(self): return self
            def __exit__(self,*_): pass
            def execute(self,*_): return self
            def fetchall(self): return [{'id':'run','project':'project'}]
        service.journal = SimpleNamespace(transaction=DB)
        with patch.object(service,'start',side_effect=OSError('storage unavailable')):
            with self.assertRaises(OSError): service.start_pending()


class SDKStartupTests(unittest.TestCase):
    def test_v2_has_settings_but_http_configuration_is_passed_to_run(self):
        class V2Settings(BaseModel):
            model_config = ConfigDict(extra='forbid',validate_assignment=True)
            debug: bool = False
        class V2:
            settings = V2Settings()
            def run(self,**kwargs): self.called = kwargs
        server = V2()
        serve(lambda _:server,['--config','fixture','--transport','streamable-http','--port','8822'])
        self.assertEqual(server.called,{'transport':'streamable-http','host':'127.0.0.1','port':8822,
            'streamable_http_path':'/mcp','stateless_http':True,'json_response':True})
        self.assertEqual(server.settings.model_dump(),{'debug':False})

    def test_v1_existing_transport_settings_remain_compatible(self):
        class V1:
            settings = SimpleNamespace(host='localhost',port=8000,stateless_http=False,
                                       json_response=False,streamable_http_path='/old')
            def run(self,transport): self.called = transport
        server = V1()
        serve(lambda _:server,['--config','fixture','--transport','streamable-http','--port','8822'])
        self.assertEqual(server.called,'streamable-http')
        self.assertEqual(server.settings.host,'127.0.0.1')
        self.assertEqual(server.settings.port,8822)
        self.assertEqual(server.settings.streamable_http_path,'/mcp')
        self.assertTrue(server.settings.json_response and server.settings.stateless_http)

    def test_stdio_does_not_attempt_http_configuration(self):
        class Stdio:
            def run(self,transport): self.called = transport
        server = Stdio()
        serve(lambda _:server,['--config','fixture'])
        self.assertEqual(server.called,'stdio')
