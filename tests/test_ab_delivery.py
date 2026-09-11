"""A/B integration with real local processes and the standalone B CLI."""
import base64
import json
import subprocess
import sys
import time
import unittest
from operation_contracts.journal import Journal
from operation_contracts.projects import Projects
from operation_contracts.common import ContractError
from chat_ops.engine import Operations
import test_fleet_jobs as fixtures
import test_chat_operations as chat_fixtures


class IntegrationTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request
    wait = fixtures.ProcessTests.wait

    def test_a_to_b_process_and_verified_artifact(self):
        jobs = self.service('from pathlib import Path; Path("answer.txt").write_text("42"); print(\'FLEET_PROGRESS {"current":1,"total":1}\')')
        projects = Projects({'version':1,'projects':{'alpha':{'members':['alice'],'resources':{
            'node':{'connector':'fleet','account_ref':'node-account','actions':['fleet.submit','fleet.status','fleet.artifact']}}}}})
        engine = Operations(projects,Journal(self.root/'chat.db'),'alice',session='integration')
        now = time.time()
        for action in ['fleet.submit','fleet.status','fleet.artifact']:
            engine.capabilities.observe('alice','alpha','node',action,engine.surface,engine.session,
                {'level':'invocable','connector':'fleet','account_ref':'node-account','tool_name':action,
                 'observed_at':now,'expires_at':now+300,'evidence_ref':'local-test-adapter'})
        workflow = {'version':1,'project_id':'alpha','idempotency_key':'integration','deadline':now+30,'steps':[
            {'id':'submit','resource':'node','action':'fleet.submit','arguments':{'request':self.request()},
             'verify':{'action':'fleet.status','arguments':{'run_id':{'$ref':'submit.run_id'}},'expect':{'state':'SUCCEEDED'}}},
            {'id':'file','resource':'node','action':'fleet.artifact','arguments':{'run_id':{'$ref':'submit.run_id'},'name':'answer.txt'}}]}
        calls, case = [], self
        class Adapter:
            def invoke(self, invocation):
                calls.append(invocation['action'])
                args = invocation['arguments']
                if invocation['action'] == 'fleet.submit':
                    out = jobs.submit(args['request']); jobs.start('alpha',out['run_id']); return out
                if invocation['action'] == 'fleet.status':
                    return case.wait(jobs,args['run_id'])
                return jobs.artifact('alpha',args['run_id'],args['name'])
        run = engine.submit(workflow)['run_id']
        self.assertEqual(engine.run('alpha',run,Adapter())['state'],'AWAITING_APPROVAL')
        engine.approve('alpha',run,'submit')
        self.assertEqual(engine.run('alpha',run,Adapter())['state'],'SUCCEEDED')
        outputs = engine.outputs(engine.row('alpha',run))
        self.assertEqual(base64.b64decode(outputs['file']['data_base64']),b'42')
        self.assertTrue(outputs['file']['verified'])
        self.assertEqual(calls.count('fleet.submit'),1)
        engine.run('alpha',run,Adapter())
        self.assertEqual(calls.count('fleet.submit'),1)

    def test_standalone_cli_submit_status_and_artifact(self):
        self.service('from pathlib import Path; Path("answer.txt").write_text("CLI_OK")')
        def cli(*args):
            result = subprocess.run([sys.executable,'-m','fleet_operator','--config',str(self.config_path),*args],
                                    capture_output=True,text=True,check=True,timeout=10)
            return json.loads(result.stdout)
        out = cli('submit','--request-json',json.dumps(self.request()),'--start')
        run = out['run_id']
        for _ in range(30):
            status = cli('status','--project','alpha','--run',run)
            if status['state'] not in {'QUEUED','RUNNING'}:
                break
            time.sleep(.05)
        self.assertEqual(status['state'],'SUCCEEDED')
        out = cli('artifact','--project','alpha','--run',run,'--name','answer.txt')
        self.assertEqual(base64.b64decode(out['data_base64']),b'CLI_OK')

    def test_artifact_rejects_foreign_project_and_unknown_name(self):
        jobs = self.service('from pathlib import Path; Path("answer.txt").write_text("42")')
        run = jobs.submit(self.request())['run_id']; jobs.start('alpha',run); self.wait(jobs,run)
        for project,name in [('beta','answer.txt'),('alpha','../answer.txt'),('alpha','missing.txt')]:
            with self.subTest(project=project,name=name), self.assertRaises(ContractError):
                jobs.artifact(project,run,name)
        with self.assertRaises(ContractError):
            jobs.artifact('alpha',run,'answer.txt',limit=65537)

    def test_receipt_tampering_and_symlink_rejected(self):
        jobs = self.service('from pathlib import Path; Path("answer.txt").write_text("42")')
        run = jobs.submit(self.request())['run_id']; jobs.start('alpha',run); self.wait(jobs,run)
        root = jobs.config.state_dir/'runs'/run
        path = root/'workspace'/'answer.txt'
        path.unlink(); path.symlink_to('/etc/hostname')
        with self.assertRaises(ContractError):
            jobs.artifact('alpha',run,'answer.txt')
        path.unlink(); path.write_text('42')
        receipt = root/'result.json'; doc=json.loads(receipt.read_text()); doc['run_id']='0'*32; receipt.write_text(json.dumps(doc))
        with self.assertRaises(ContractError):
            jobs.artifact('alpha',run,'answer.txt')


class NativeRecoveryTests(unittest.TestCase):
    setUp = chat_fixtures.ChatOperationsTests.setUp
    tearDown = chat_fixtures.ChatOperationsTests.tearDown
    workflow = chat_fixtures.ChatOperationsTests.workflow

    def test_other_session_cannot_record_pending_result(self):
        run=self.engine.submit(self.workflow())['run_id']; todo=self.engine.next('alpha',run)
        other=Operations(self.projects,self.engine.journal,'alice',session='other')
        with self.assertRaises(ContractError):
            other.record('alpha',run,'mail',todo['token'],{})
        self.assertEqual(self.engine.next('alpha',run)['state'],'AWAITING_RESULT')

    def test_lost_response_recovered_and_used_by_next_step(self):
        workflow=self.workflow()
        workflow['steps'][1]['verify']['recover_output']={'id':{'$ref':'verification.id'}}
        workflow['steps'].append({'id':'followup','resource':'repo','action':'github.read',
            'arguments':{'owner':'example','repo':'alpha','id':{'$ref':'issue.id'}}})
        tools=chat_fixtures.FakeTools();tools.fail_after_write=True
        run=self.engine.submit(workflow)['run_id'];self.engine.run('alpha',run,tools)
        self.engine.approve('alpha',run,'issue')
        self.assertEqual(self.engine.run('alpha',run,tools)['state'],'UNCERTAIN')
        todo=self.engine.reconcile('alpha',run,'issue')
        self.engine.record('alpha',run,'issue',todo['token'],tools.invoke(todo['invocation']))
        self.assertEqual(self.engine.run('alpha',run,tools)['state'],'SUCCEEDED')
        self.assertEqual(tools.calls[-1]['arguments']['id'],42)
        self.assertEqual(tools.writes,1)
