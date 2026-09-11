#!/usr/bin/env python3
"""Restore two omitted tracked skill documents before completing an existing deployment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

FILES=('skills/capability-router/SKILL.md','skills/surface-handoff/SKILL.md')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('repo','root','revision','alias'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--finish',action='store_true')
    args=parser.parse_args(); os.umask(0o077)
    if os.getuid()==0 or not re.fullmatch(r'[0-9a-f]{40}',args.revision):
        raise ValueError('non-root operator and exact revision required')
    root=Path(args.root).expanduser().resolve()
    if Path.home().resolve() not in root.parents:
        raise ValueError('deployment must be in operator home')
    source=root/'source'/args.revision
    if not (source/'.archive-sha256').is_file():
        raise ValueError('existing staged deployment required')
    hashes={}
    for name in FILES:
        data=subprocess.check_output(['git','-C',args.repo,'show',args.revision+':'+name],timeout=20)
        if not data.startswith(b'---\n') or len(data)>131072:
            raise ValueError('unexpected skill metadata')
        path=source/name
        if path.is_symlink(): raise ValueError('skill path must not be a symlink')
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        if source.resolve() not in path.resolve().parents: raise ValueError('skill path escapes release')
        if path.exists():
            if path.read_bytes()!=data: raise ValueError('existing skill differs from the pinned commit')
        else:
            with path.open('xb') as stream: stream.write(data)
        hashes[name]=hashlib.sha256(data).hexdigest()
    proof={'revision':args.revision,'supplemental_files_sha256':hashes,
           'runtime_code_changed':False,'original_archive_digest':(source/'.archive-sha256').read_text()}
    (root/'supplemental-assets.json').write_text(json.dumps(proof,indent=2)+'\n')
    if args.finish:
        python=root/'venvs'/args.revision/'bin/python'
        subprocess.run([str(python),str(source/'scripts/ab_host_install.py'),'--root',str(root),
            '--revision',args.revision,'--alias',args.alias,'--gateway'],check=True,timeout=500)
        receipt=json.loads((root/'deployment.json').read_text())
        if receipt['revision']!=args.revision or receipt['alias']!=args.alias:
            raise ValueError('unexpected deployment receipt')
        rollout_path=root/'rollout.json'
        rollout=json.loads(rollout_path.read_text()); rollout['nodes'][args.alias]=receipt
        temporary=root/'rollout.next.json'
        temporary.write_text(json.dumps(rollout,indent=2)+'\n'); temporary.replace(rollout_path)
    print(json.dumps(proof))

if __name__=='__main__': main()
