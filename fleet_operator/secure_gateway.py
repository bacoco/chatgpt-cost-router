"""Public gateway policy layered over the retained low-level SSH transport."""
import json
import os
import subprocess
import time
from pathlib import PurePosixPath, Path
from .core import FleetConfig, FleetError, FleetRunner as TransportRunner, ExecResult, validate_argv, _within_allowed_roots
from .command_policy import read_allowed, write_allowed
from .host_io import READ_HELPER, EXEC_HELPER, safe_environment


class SecureRunner(TransportRunner):
    def __init__(self, config, *, runtimes=None, **kwargs):
        from .bounded_process import run
        from functools import partial
        kwargs.setdefault("run", partial(run, max_bytes=config.max_output_bytes))
        super().__init__(config,**kwargs)
        self.runtime_bindings = runtimes or {}

    def host(self, alias):
        host = super().host(alias)
        if host.transport == "ssh" and host.ssh_target.split("@",1)[0] == "root":
            raise FleetError("root SSH targets are not allowed")
        return host

    def _authorize(self, host, argv, mode, allow_destructive):
        args = validate_argv(argv)
        if allow_destructive:
            raise FleetError("destructive raw gateway execution is unavailable; use an approved profile")
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

    def _validate_cwd(self, host, cwd):
        cwd = super()._validate_cwd(host,cwd)
        if cwd is not None and host.transport == "local":
            actual = str(Path(cwd).resolve())
            roots = [str(Path(root).resolve()) for root in host.allowed_roots]
            if not _within_allowed_roots(actual,roots):
                raise FleetError("local cwd resolves outside allowed roots")
            return actual
        return cwd

    def _ssh_prefix(self, host):
        prefix = super()._ssh_prefix(host)
        return prefix[:1]+["-o","ForwardAgent=no","-o","ClearAllForwardings=yes","-o","PermitLocalCommand=no"]+prefix[1:]

    def execute(self, alias, argv, *, cwd=None, timeout_seconds=None, mode="write", allow_destructive=False):
        host = self.host(alias)
        args = self._authorize(host, argv, mode, allow_destructive)
        cwd = self._validate_cwd(host, cwd)
        timeout = self.config.default_timeout_seconds if timeout_seconds is None else timeout_seconds
        if type(timeout) is not int or not 1 <= timeout <= self.config.max_timeout_seconds:
            raise FleetError("invalid bounded execution timeout")
        command = list(args)
        if PurePosixPath(args[0]).name == "git":
            if cwd is None:
                raise FleetError("Git inspection requires a confined repository cwd")
            options = ["--no-pager", "--no-optional-locks", "-c", "core.hooksPath=/dev/null",
                       "-c", "core.fsmonitor=false", "-c", "core.pager=cat", "-c", "credential.helper="]
            command = [args[0], *options, *args[1:]]
            if args[1] in {"diff", "show", "log"}:
                command[len(options)+2:len(options)+2] = ["--no-ext-diff", "--no-textconv"]
        # The fixed helper resolves every cwd component on the target host without symlinks.
        payload = json.dumps([command, cwd, list(host.allowed_roots)])
        wire = ["python3", "-I", "-c", EXEC_HELPER, payload]
        if host.transport == "ssh":
            wire = self._ssh_prefix(host)+[self._remote_command(wire, None)]
        start = time.monotonic()
        timed_out = False
        try:
            result = self._run(wire, capture_output=True, text=False, check=False, timeout=timeout,
                               env=safe_environment(os.environ))
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out, code, stdout, stderr = True, 124, exc.stdout, exc.stderr
        out, a = self._cap(stdout)
        err, b = self._cap(stderr)
        return ExecResult(alias, args, cwd, code, out, err, time.monotonic()-start, timed_out, a, b)

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
        argv = ["python3","-I","-c",READ_HELPER,path,max(roots,key=len),str(max_bytes+1)]
        wire = argv if host.transport == "local" else self._ssh_prefix(host)+[self._remote_command(argv,None)]
        result = self._run(wire,capture_output=True,text=False,check=False,timeout=30,env=safe_environment(os.environ))
        raw = result.stdout if isinstance(result.stdout, bytes) else result.stdout.encode()
        out, trunc = raw[:max_bytes].decode(errors="replace"), len(raw) > max_bytes
        return {"host":alias,"exit_code":result.returncode,"stdout":out,"stderr":"" if result.returncode == 0 else "confined file read failed",
                "stdout_truncated":trunc,"timed_out":False}


def configured_runner(path):
    from pathlib import Path
    from operation_contracts.common import load
    raw = load(path)
    runtimes = {name:host["runtime"] for name,host in raw.get("hosts",{}).items() if "runtime" in host}
    return SecureRunner(FleetConfig.load(path),runtimes=runtimes)
