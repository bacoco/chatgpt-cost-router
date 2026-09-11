#!/usr/bin/env python3
"""Owner-authorized rollout to aliases already present in a private gateway config."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOTS=['chat_ops','fleet_operator','operation_contracts','cost_router','scripts','schemas','policy',
       'tests','examples','requirements.txt','requirements-dev.txt','requirements-fleet-operator.txt',
       'pyproject.toml','setup.py','MANIFEST.in','README.md']
PROBE="""import json,os,pathlib,subprocess,sys,shutil,glob
home=pathlib.Path.home()
candidates=[home/'.local/share/chatgpt-cost-router/fleet-operator-venv-py311/bin/python',pathlib.Path('/opt/homebrew/bin/python3.11'),pathlib.Path('/opt/homebrew/opt/python@3.11/bin/python3.11'),pathlib.Path('/opt/homebrew/bin/python3'),pathlib.Path('/usr/bin/python3'),pathlib.Path(sys.executable)]
candidates.extend(pathlib.Path(v) for name in ['python3.14','python3.13','python3.12','python3.11'] for v in [shutil.which(name)] if v)
for pattern in ['/opt/homebrew/opt/python@*/bin/python3.*',str(home/'.local/share/uv/python/*/bin/python3'),str(home/'.pyenv/versions/*/bin/python3'),'/opt/anaconda3/bin/python3']:
 candidates.extend(pathlib.Path(v) for v in glob.glob(pattern))
found=[]
for p in candidates:
 if p.is_file():
  r=subprocess.run([str(p),'-c','import sys; print(int(sys.version_info >= (3,11)))'],capture_output=True,text=True,timeout=15)
  if r.returncode==0 and r.stdout.strip()=='1': found.append(str(p))
print(json.dumps({'home':str(home),'python':found[0] if found else None,'uid':os.getuid()}))
"""
RECEIVE="""import gzip,hashlib,io,json,os,pathlib,subprocess,sys,tarfile
root,rev,expected,alias,python,gateway=sys.argv[1:]
os.umask(0o077)
root=pathlib.Path(root); root.mkdir(parents=True,exist_ok=True,mode=0o700)
raw=sys.stdin.buffer.read(8*1024*1024+1)
if len(raw)>8*1024*1024 or hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('archive integrity mismatch')
source=root/'source'/rev
if not source.exists():
 source.mkdir(parents=True,mode=0o700)
 with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as arc:
  for member in arc.getmembers():
   p=pathlib.PurePosixPath(member.name)
   if p.is_absolute() or '..' in p.parts or not (member.isfile() or member.isdir()): raise ValueError('unsafe archive member')
   target=source/member.name
   if member.isdir(): target.mkdir(parents=True,exist_ok=True,mode=0o700)
   else:
    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with arc.extractfile(member) as stream, target.open('xb') as out: out.write(stream.read())
    target.chmod(0o700 if member.mode & 0o111 else 0o600)
 (source/'.archive-sha256').write_text(expected)
if (source/'.archive-sha256').read_text()!=expected: raise ValueError('existing release differs')
command=[python,str(source/'scripts/ab_host_install.py'),'--root',str(root),'--revision',rev,'--alias',alias]
if gateway=='yes': command.append('--gateway')
p=subprocess.run(command,check=False)
sys.exit(p.returncode)
"""


def wire(config, alias, argv):
    host=config['hosts'][alias]
    if host.get('enabled',True) is not True: raise ValueError('disabled host')
    if host.get('transport','ssh')=='local': return argv
    target=host.get('ssh_target','')
    if not re.fullmatch(r'(?:[A-Za-z0-9._-]+@)?[A-Za-z0-9._:-]+',target) or target.startswith('root@'):
        raise ValueError('invalid or root SSH target')
    return [config.get('ssh_bin','/usr/bin/ssh'),'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
            '-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','PermitLocalCommand=no',
            '-o','ConnectTimeout=10','-p',str(host.get('port',22)),target,shlex.join(argv)]


def execute(command, data=None, timeout=30):
    p=subprocess.run(command,input=data,capture_output=True,timeout=timeout)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[-2000:] or 'remote command failed')
    return json.loads(p.stdout)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['repo','revision','gateway-config','hosts']: p.add_argument('--'+name,required=True)
    args=p.parse_args()
    if os.getuid()==0: raise RuntimeError('non-root operator required')
    if not re.fullmatch('[0-9a-f]{40}',args.revision): raise ValueError('exact commit required')
    cfg=json.loads(Path(args.gateway_config).expanduser().read_text())
    hosts=args.hosts.split(',')
    if len(hosts)!=len(set(hosts)) or any(h not in cfg['hosts'] for h in hosts): raise ValueError('unknown or duplicate alias')
    raw=subprocess.check_output(['git','-C',args.repo,'archive','--format=tar',args.revision,*ROOTS],timeout=60)
    packed=gzip.compress(raw,mtime=0); sha=hashlib.sha256(packed).hexdigest()
    results={}
    for alias in hosts:
        try:
            info=execute(wire(cfg,alias,['python3','-c',PROBE]))
            if info['uid']==0 or not info['python']: raise RuntimeError('non-root Python 3.11+ unavailable')
            base=info['home']+'/.local/share/chatgpt-cost-router/ab'
            argv=[info['python'],'-c',RECEIVE,base,args.revision,sha,alias,info['python'],
                  'yes' if cfg['hosts'][alias].get('transport')=='local' else 'no']
            results[alias]=execute(wire(cfg,alias,argv),packed,timeout=600)
        except Exception as exc:
            results[alias]={'alias':alias,'state':'BLOCKED','error':str(exc)[-2500:]}
    output={'version':1,'revision':args.revision,'archive_sha256':sha,'nodes':results,'legacy_services_changed':False}
    path=Path.home()/'.local/share/chatgpt-cost-router/ab/rollout.json'
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    path.write_text(json.dumps(output,indent=2)+'\n'); path.chmod(0o600)
    print(json.dumps(output))

if __name__=='__main__': main()
