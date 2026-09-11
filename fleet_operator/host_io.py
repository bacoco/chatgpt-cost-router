"""Fixed read helper: resolve every component without following symlinks."""
import json

READ_HELPER = r'''
import os,sys,stat
path,root,limit=sys.argv[1],sys.argv[2],int(sys.argv[3])
root=os.path.realpath(root)
relative=os.path.relpath(path,root)
if relative=='..' or relative.startswith('../') or os.path.isabs(relative):
    raise SystemExit(2)
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
    parts=relative.split('/')
    for part in parts[:-1]:
        new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
        os.close(fd);fd=new
    item=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
    try:
        if not stat.S_ISREG(os.fstat(item).st_mode):
            raise SystemExit(2)
        remaining=limit
        while remaining:
            raw=os.read(item,min(65536,remaining))
            if not raw:break
            sys.stdout.buffer.write(raw);remaining-=len(raw)
    finally:os.close(item)
finally:os.close(fd)
'''


def safe_environment(environment):
    blocked = {"OPENAI_API_KEY","ANTHROPIC_API_KEY","AZURE_OPENAI_API_KEY","GOOGLE_API_KEY",
               "PYTHONPATH","PYTHONHOME","NODE_OPTIONS","BASH_ENV","ENV","LD_PRELOAD","DYLD_INSERT_LIBRARIES"}
    return {key:value for key,value in environment.items() if key not in blocked and not key.startswith("GIT_CONFIG")}
