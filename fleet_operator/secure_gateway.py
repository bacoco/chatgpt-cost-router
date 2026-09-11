"""Public gateway policy layered over the retained low-level SSH transport."""
import json
import os
import time
from pathlib import PurePosixPath
from .core import FleetConfig, FleetError, FleetRunner as TransportRunner, ExecResult, validate_argv, _within_allowed_roots
from .command_policy import read_allowed, write_allowed
from .host_io import READ_HELPER, safe_environment


class SecureRunner(TransportRunner):
    def __init__(self, config, *, runtimes=None, **kwargs):
        super().__init__(config,**kwargs)
        self.runtime_bindings = runtimes or {}

    def _authorize(self, host, argv, mode, allow_destructive):
        args = validate_argv(argv)
        if mode not in {"read","write"}:
            raise FleetError("invalid execution mode")
        if host.transport == "ssh" and host.ssh_target.split("@",1)[0] == "root":
            raise FleetError("root SSH targets are not allowed")
        allowed = host.read_commands if mode == "read" else host.read_commands | host.write_commands
        if PurePosixPath(args[0]).name not in allowed:
            raise FleetError("command not allowlisted")
        if not (read_allowed(args) if mode == "read" else write_allowed(args)):
            raise FleetError("unbounded command refused; enroll an ordinary process profile")
        return args

    def _ssh_prefix(self, host):
        prefix = super()._ssh_prefix(host)
        return prefix[:1]+["-o","ForwardAgent=no","-o","ClearAllForwardings=yes","-o","PermitLocalCommand=no"]+prefix[1:]

    def execute(self, alias, argv, **kwargs):
        # Internal Git hooks/fsmonitor/text conversion are disabled for inspection.
        if argv and argv[0] == "git":
            self._authorize(self.host(alias),argv,kwargs.get("mode","write"),kwargs.get("allow_destructive",False))
            return self._git(alias,argv,**kwargs)
        return super().execute(alias,argv,**kwargs)

    def _git(self, alias, argv, cwd=None, timeout_seconds=None, **kwargs):
        host = self.host(alias)
        cwd = self._validate_cwd(host,cwd)
        if cwd is None:
            raise FleetError("Git inspection requires a confined repository cwd")
        command = ["git","-c","core.hooksPath=/dev/null","-c","core.fsmonitor=false",*argv[1:]]
        if argv[1] in {"diff","show"}:
            command[6:6] = ["--no-ext-diff","--no-textconv"]
        wire = command if host.transport == "local" else self._ssh_prefix(host)+[self._remote_command(command,cwd)]
        start = time.monotonic()
        result = self._run(wire,capture_output=True,text=False,check=False,timeout=min(timeout_seconds or 30,120),
                           env=safe_environment(os.environ),**({"cwd":cwd} if host.transport == "local" else {}))
        out, a = self._cap(result.stdout)
        err, b = self._cap(result.stderr)
        return ExecResult(alias,tuple(argv),cwd,result.returncode,out,err,time.monotonic()-start,False,a,b)

    def inventory(self):
        return [{"host":host.alias,"tags":list(host.tags),"transport":host.transport,"enabled":host.enabled,
                 "process_runtime_enrolled":host.alias in self.runtime_bindings} for host in self.config.hosts.values()]

    def read_file(self, alias, path, *, max_bytes=131072):
        host = self.host(alias)
        if type(max_bytes) is not int or not 1 <= max_bytes <= self.config.max_output_bytes:
            raise FleetError("invalid read limit")
        if not isinstance(path,str):
            raise FleetError("invalid path")
        parts = PurePosixPath(path).parts
        if any(part in {".ssh",".aws",".codex","secrets","auth.json"} or part.startswith(".env") for part in parts):
            raise FleetError("credential locations cannot be read through public tools")
        roots = [root for root in host.allowed_roots if _within_allowed_roots(path,[root])]
        if not roots:
            raise FleetError("path outside allowed roots")
        argv = ["python3","-I","-c",READ_HELPER,path,max(roots,key=len),str(max_bytes)]
        wire = argv if host.transport == "local" else self._ssh_prefix(host)+[self._remote_command(argv,None)]
        result = self._run(wire,capture_output=True,text=False,check=False,timeout=30,env=safe_environment(os.environ))
        out, trunc = self._cap(result.stdout)
        return {"host":alias,"exit_code":result.returncode,"stdout":out,"stderr":"" if result.returncode == 0 else "confined file read failed",
                "stdout_truncated":trunc,"timed_out":False}


def configured_runner(path):
    from pathlib import Path
    raw = json.loads(Path(path).expanduser().read_text())
    runtimes = {name:host["runtime"] for name,host in raw.get("hosts",{}).items() if "runtime" in host}
    return SecureRunner(FleetConfig.load(path),runtimes=runtimes)
