#!/usr/bin/env python3
"""Explicit owner-run A/B installation. Never changes legacy services or checkouts."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from operation_contracts.files import atomic_json
from fleet_operator.jobs.config import NodeConfig
from fleet_operator.jobs.service import Jobs
from fleet_operator.enrollment.services import render


def run(argv, log, timeout=300):
    with log.open('ab') as output:
        done = subprocess.run(list(map(str, argv)), stdout=output, stderr=output,
                              timeout=timeout, check=False)
    if done.returncode:
        raise RuntimeError('command failed; inspect private log ' + str(log))


def install_service(command, label, logs):
    """Install only this deployment's new user service; refuse an existing definition."""
    mac = sys.platform == 'darwin'
    folder = Path.home()/('Library/LaunchAgents' if mac else '.config/systemd/user')
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/(label + ('.plist' if mac else '.service'))
    text = render(command, label, platform='launchd' if mac else 'systemd', log_dir=str(logs))
    if path.exists() and path.read_text() != text:
        raise RuntimeError('existing service differs; explicit upgrade/rollback required: '+str(path))
    if not path.exists():
        path.write_text(text); path.chmod(0o600)
    if mac:
        target = f'gui/{os.getuid()}/{label}'
        check = subprocess.run(['launchctl','print',target],capture_output=True,timeout=15)
        if check.returncode:
            run(['launchctl','bootstrap',f'gui/{os.getuid()}',path], logs/'install.log', 30)
        check = subprocess.run(['launchctl','print',target],capture_output=True,text=True,timeout=15)
        state = check.returncode == 0 and 'state = running' in check.stdout
    else:
        run(['systemctl','--user','daemon-reload'], logs/'install.log', 30)
        run(['systemctl','--user','enable','--now',path.name], logs/'install.log', 30)
        check = subprocess.run(['systemctl','--user','is-active',path.name],capture_output=True,text=True,timeout=15)
        state = check.returncode == 0 and check.stdout.strip() == 'active'
    return {'label':label, 'definition':str(path), 'running':state}


def configure(root, revision, alias, python):
    config = root/'config'; config.mkdir(parents=True, exist_ok=True, mode=0o700)
    project = 'chatgpt-cost-router'
    resource = {'connector':'github','account_ref':'bacoco',
                'actions':['github.read','github.write'],
                'bindings':{'owner':'bacoco','repo':project}}
    project_policy = {'members':['loic'],'nodes':[alias],
                      'profiles':['smoke','validate-release'],'resources':{'repo':resource}}
    projects = {'version':1,'projects':{project:project_policy}}
    node = {'version':1,'node_id':alias,'principal':'loic','state_dir':str(root/'node-state'),
        'projects_file':str(config/'projects.json'),'runtime_revision':revision,'max_concurrency':2,
        'profiles':{'smoke':{'argv':[str(python),str(SOURCE/'scripts/ab_smoke_task.py')],
        'isolation':'trusted-local','timeout_seconds':45,'max_output_bytes':16384,'artifacts':['result.json']},
        'validate-release':{'argv':[str(python),str(SOURCE/'scripts/validate_ab.py'),'--output','validation'],
        'isolation':'trusted-local','timeout_seconds':600,'max_output_bytes':65536,
        'artifacts':['validation/validation.json','validation/unittest.log']}}}
    chat = {'version':1,'principal':'loic','projects_file':str(config/'projects.json'),
        'state_dir':str(root/'chat-state'),'surface':'chatgpt-web-chat','session':'needs-live-session'}
    for name, value in [('projects',projects),('node',node),('chat',chat)]:
        path = config/(name+'.json')
        if path.exists() and json.loads(path.read_text()) != value:
            raise RuntimeError('configuration already exists and differs: '+str(path))
        atomic_json(path, value)
    return config


def smoke(config, revision):
    jobs = Jobs(NodeConfig.from_file(config/'node.json'))
    def request(key, seconds=0):
        return {'version':1,'node_id':jobs.config.node_id,'project_id':'chatgpt-cost-router',
            'profile':'smoke','idempotency_key':key,'inputs':{'seconds':seconds},'deadline':time.time()+90}
    def wait(id_, limit=30):
        until=time.monotonic()+limit
        while time.monotonic()<until:
            status=jobs.status('chatgpt-cost-router',id_)
            if status['state'] not in {'QUEUED','RUNNING','CANCELLING'}: return status
            time.sleep(.1)
        raise RuntimeError('smoke did not finish within bound')
    key='deployment-'+revision[:12]+'-'+str(time.time_ns())
    normal=jobs.submit(request(key))['run_id']; jobs.start('chatgpt-cost-router',normal)
    done=wait(normal)
    if done['state']!='SUCCEEDED': raise RuntimeError('smoke failed: '+done['state'])
    artifact=jobs.artifact('chatgpt-cost-router',normal,'result.json')
    data=base64.b64decode(artifact['data_base64'])
    if not artifact['verified'] or json.loads(data)['ok'] is not True: raise RuntimeError('bad smoke artifact')
    cancelled=jobs.submit(request(key+'-cancel',20))['run_id']; jobs.start('chatgpt-cost-router',cancelled)
    time.sleep(.7); jobs.cancel('chatgpt-cost-router',cancelled)
    stopped=wait(cancelled)
    if stopped['state']!='CANCELLED': raise RuntimeError('cancellation not verified: '+stopped['state'])
    return {'job':normal,'state':done['state'],'artifact_verified':True,'artifact_sha256':artifact['sha256'],
            'cancel_job':cancelled,'cancel_state':stopped['state'],'health':jobs.health()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True); p.add_argument('--revision',required=True)
    p.add_argument('--alias',required=True); p.add_argument('--gateway',action='store_true')
    args=p.parse_args()
    os.umask(0o077)
    if os.getuid()==0 or sys.version_info<(3,11): raise RuntimeError('requires non-root Python 3.11+')
    if not re.fullmatch('[0-9a-f]{40}',args.revision) or not re.fullmatch('[a-zA-Z0-9_.-]{1,64}',args.alias):
        raise RuntimeError('invalid revision or alias')
    root=Path(args.root).expanduser().absolute(); root.mkdir(parents=True,exist_ok=True,mode=0o700)
    if Path.home().resolve() not in root.resolve().parents: raise RuntimeError('installation must stay in user home')
    logs=root/'logs'; logs.mkdir(exist_ok=True,mode=0o700)
    venv=root/'venvs'/args.revision
    if not (venv/'bin/python').exists(): run([sys.executable,'-m','venv',venv],logs/'install.log')
    python=venv/'bin/python'
    run([python,'-m','pip','install','--disable-pip-version-check',str(SOURCE)+('[mcp]' if args.gateway else '')],logs/'install.log')
    run([python,'-m','pip','install','--disable-pip-version-check','PyYAML==6.0.2'],logs/'install.log')
    config=configure(root,args.revision,args.alias,python)
    # Run the checks under the installed virtualenv, not the bootstrap interpreter.
    check=subprocess.run([python,'-c','import json,sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from ab_host_install import smoke; print(json.dumps(smoke(Path(sys.argv[2]),sys.argv[3])))',str(SOURCE/'scripts'),str(config),args.revision],capture_output=True,text=True,timeout=100)
    if check.returncode: raise RuntimeError('node checks failed: '+check.stderr[-2500:])
    evidence=json.loads(check.stdout)
    if args.gateway:
        run([python,SOURCE/'scripts/validate_ab.py','--output',root/'validation'],logs/'validation-command.log',300)
        report=json.loads((root/'validation/validation.json').read_text())
        evidence['tests']={k:report[k] for k in ('tests_run','passed','failures','errors','skipped','successful')}
    services=[install_service([str(python),str(SOURCE/'scripts/fleet_jobs.py'),'--config',str(config/'node.json'),'serve-queue'],
                              'pro.chatgpt-cost-router.ab-node',logs)]
    if args.gateway:
        services.append(install_service([str(python),'-m','chat_ops.mcp_server','--config',str(config/'chat.json'),
            '--transport','streamable-http','--port','8812'],'pro.chatgpt-cost-router.ab-chat',logs))
    result={'version':1,'alias':args.alias,'revision':args.revision,'source':str(SOURCE),'python':str(python),
        'node_config':str(config/'node.json'),'checks':evidence,'services':services,'legacy_services_changed':False}
    atomic_json(root/'deployment.json',result); print(json.dumps(result))

if __name__=='__main__': main()
