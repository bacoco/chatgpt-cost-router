#!/usr/bin/env python3
"""Activate separate A/B gateway and durable relay after node verification."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request, build_opener, ProxyHandler


def rpc(port, method, params):
    body={'jsonrpc':'2.0','id':1,'method':method,'params':params}
    request=Request(f'http://127.0.0.1:{port}/mcp',data=json.dumps(body).encode(),
        headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'})
    # Local service checks must not inherit an external HTTP proxy or system PAC.
    with build_opener(ProxyHandler({})).open(request,timeout=30) as response:
        data=json.loads(response.read(1048576))
    if 'error' in data: raise RuntimeError('MCP error: '+str(data['error']))
    return data['result']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rollout','legacy-config','repo']: p.add_argument('--'+name,required=True)
    args=p.parse_args(); os.umask(0o077)
    if os.getuid()==0: raise RuntimeError('requires non-root operator')
    rollout=json.loads(Path(args.rollout).read_text())
    nodes={name:data for name,data in rollout['nodes'].items() if data.get('checks',{}).get('artifact_verified')}
    local=nodes.get('macbook')
    if not local: raise RuntimeError('verified gateway node unavailable')
    root=Path(args.rollout).parent; source=Path(local['source']); python=local['python']
    sys.path.insert(0,str(source)); sys.path.insert(0,str(source/'scripts'))
    from operation_contracts.files import atomic_json
    from ab_host_install import install_service
    config=root/'config'; logs=root/'logs'
    legacy=json.loads(Path(args.legacy_config).read_text())
    gateway={key:value for key,value in legacy.items() if key!='hosts'}
    gateway['hosts']={}
    for alias,node in nodes.items():
        host=dict(legacy['hosts'][alias]); health=node['checks']['health']
        host['write_commands']=[]
        host['runtime']={'python':node['python'],'entrypoint':str(Path(node['source'])/'scripts/fleet_jobs.py'),
            'config':node['node_config'],'node_id':alias,'runtime_revision':node['revision'],
            'policy_revision':health['policy_revision']}
        gateway['hosts'][alias]=host
    path=config/'gateway.json'
    if path.exists() and json.loads(path.read_text())!=gateway:
        raise RuntimeError('gateway config drift; explicit update required')
    atomic_json(path,gateway)
    transport=root/'relay-repo'
    if not transport.exists():
        subprocess.run(['git','clone','--shared','--no-checkout',args.repo,str(transport)],check=True,capture_output=True,timeout=60)
        origin=subprocess.check_output(['git','-C',args.repo,'remote','get-url','origin'],text=True,timeout=15).strip()
        subprocess.run(['git','-C',str(transport),'remote','set-url','origin',origin],check=True,capture_output=True,timeout=15)
    relay={'version':1,'repo':str(transport),'fleet_config':str(path),'command_branch':'fleet/ab-commands',
        'poll_seconds':15,'result_branch_prefix':'fleet/ab-results/','state_dir':str(root/'relay-state')}
    relay_path=config/'relay.json'; atomic_json(relay_path,relay)
    services=[install_service([python,'-m','fleet_operator.mcp_server','--config',str(path),
                '--transport','streamable-http','--port','8813'],'pro.chatgpt-cost-router.ab-gateway',logs),
        install_service([python,str(source/'scripts/fleet_operator_relay.py'),'--config',str(relay_path)],
                'pro.chatgpt-cost-router.ab-relay',logs)]
    output={'revision':local['revision'],'nodes':list(nodes),'services':services,'ports':{},'checks':{},
            'command_branch':'fleet/ab-commands','result_prefix':'fleet/ab-results/','legacy_services_changed':False}
    for port,name in [(8812,'chat'),(8813,'gateway')]:
        for attempt in range(20):
            try:
                initialized=rpc(port,'initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'deployment-check','version':'1'}})
                tools=rpc(port,'tools/list',{})
                output['ports'][name]={'loopback_port':port,'protocol':initialized['protocolVersion'],
                                       'tools':[tool['name'] for tool in tools['tools']]}
                break
            except Exception:
                if attempt==19: raise
                time.sleep(.5)
    for alias in nodes:
        reply=rpc(8813,'tools/call',{'name':'fleet_node_health','arguments':{'host':alias}})
        if reply.get('isError'): raise RuntimeError('gateway node health failed: '+alias)
        output['checks'][alias]=reply
    atomic_json(root/'gateway-deployment.json',output); print(json.dumps(output))

if __name__=='__main__': main()
