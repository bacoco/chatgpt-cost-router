#!/usr/bin/env python3
"""Validate a pinned tracked source snapshot without changing an operator checkout."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('repo','revision','output'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    if os.getuid()==0 or not re.fullmatch('[0-9a-f]{40}',args.revision):
        raise ValueError('non-root operator and exact revision required')
    os.umask(0o077)
    output=Path(args.output).expanduser().resolve()
    if Path.home().resolve() not in output.parents:
        raise ValueError('validation output must be in the operator home')
    output.mkdir(parents=True,exist_ok=True,mode=0o700)
    roots=['chat_ops','fleet_operator','operation_contracts','cost_router','scripts','schemas','policy',
           'tests','examples','skills','requirements.txt','requirements-dev.txt','requirements-fleet-operator.txt',
           'pyproject.toml','setup.py','MANIFEST.in','README.md','docs','SPEC.md','.chatgpt','.github']
    raw=subprocess.check_output(['git','-C',args.repo,'archive','--format=tar',args.revision,*roots],timeout=60)
    if len(raw)>128*1024*1024: raise ValueError('snapshot exceeds validation bound')
    from fleet_operator.jobs.workspace import extract_snapshot
    with tempfile.TemporaryDirectory(prefix='source-',dir=output) as temp:
        source=Path(temp); extract_snapshot(raw,source)
        done=subprocess.run([sys.executable,str(source/'scripts/validate_ab.py'),'--output',str(output)],
                            capture_output=True,text=True,timeout=300)
        if not (output/'validation.json').is_file():
            raise RuntimeError('validation did not produce a report: '+done.stderr[-2000:])
        report=json.loads((output/'validation.json').read_text())
        summary={key:report[key] for key in ('tests_run','passed','failures','errors','skipped','successful')}
        summary['source_revision']=args.revision
        current=['README.md','docs/README.md','docs/INSTALLATION.md','docs/AB_USAGE.md',
                 'docs/ARCHITECTURE.md','docs/AB_VALIDATION.md','docs/ROADMAP.md','docs/DEPLOYMENT_STATUS.md',
                 'docs/FLEET_OPERATOR_RELAY.md','.chatgpt/CURRENT.md','.chatgpt/PROJECT.md']
        links=[]
        for name in current:
            path=source/name
            if not path.exists(): continue
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text()):
                target=target.split('#',1)[0]
                if not target or '://' in target or target.startswith('mailto:'): continue
                links.append({'file':name,'target':target,'exists':(path.parent/target).exists()})
        summary['relative_links_checked']=len(links)
        summary['broken_relative_links']=[link for link in links if not link['exists']]
        summary['exit_code']=done.returncode
        (output/'snapshot-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary))
        return 0 if report['successful'] and not summary['broken_relative_links'] else 1

if __name__=='__main__': sys.exit(main())
