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
    item=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
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
    allowed = {"HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TZ", "SSH_AUTH_SOCK", "XDG_RUNTIME_DIR"}
    return {"PATH":"/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin",
            **{key:value for key,value in environment.items() if key in allowed}}


EXEC_HELPER = r'''import os,sys,json
argv,cwd,roots=json.loads(sys.argv[1])
if cwd is not None:
    matches=[r for r in roots if cwd==r or cwd.startswith(r.rstrip('/')+'/')]
    if not matches:raise SystemExit(2)
    root=max(matches,key=len)
    relative=os.path.relpath(cwd,root)
    if relative=='..' or relative.startswith('../'):raise SystemExit(2)
    fd=os.open(os.path.realpath(root),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in relative.split('/'):
            if part=='.':continue
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
        os.fchdir(fd)
    finally:os.close(fd)
allowed={'HOME','USER','LOGNAME','LANG','LC_ALL','TZ','SSH_AUTH_SOCK','XDG_RUNTIME_DIR'}
env={k:v for k,v in os.environ.items() if k in allowed}
env['PATH']='/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin'
os.execvpe(argv[0],argv,env)
'''
