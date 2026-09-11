#!/usr/bin/env python3
"""Bounded ordinary process for real deployment checks; no model or network call."""
import json
import os
from pathlib import Path
import platform
import time


def main():
    inputs=json.loads(Path(os.environ['FLEET_INPUT_FILE']).read_text())
    seconds=inputs.get('seconds',0)
    if type(seconds) not in (int,float) or not 0<=seconds<=30:
        raise ValueError('seconds must be in [0,30]')
    print('FLEET_PROGRESS {"current":0,"total":1}',flush=True)
    time.sleep(seconds)
    Path('result.json').write_text(json.dumps({'ok':True,'platform':platform.system(),'model_calls':0}))
    print('FLEET_PROGRESS {"current":1,"total":1}',flush=True)

if __name__=='__main__': main()
