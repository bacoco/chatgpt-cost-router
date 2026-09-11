"""Safe SSH execution core for the Fleet Operator MCP app.

The MCP client never supplies SSH destinations.  It addresses local aliases only;
this module resolves those aliases from a local, untracked configuration file.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import PurePosixPath, Path
from typing import Iterable, Mapping, Sequence


class FleetError(ValueError):
    """A configuration or policy error safe to return to the caller."""


ALIAS_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
TARGET_RE = re.compile(r"^(?:[A-Za-z0-9._-]+@)?[A-Za-z0-9._:-]+$")

# These are intentionally unavailable through Fleet Operator even when a host's
# write allow-list is broad.  Root/admin work remains a deliberate local action.
HARD_BLOCKED_COMMANDS = frozenset({
    "sudo", "su", "doas", "shutdown", "reboot", "halt", "poweroff",
    "diskutil", "dd", "mkfs", "fdisk", "csrutil", "nvram", "passwd",
})

DESTRUCTIVE_COMMANDS = frozenset({"rm", "kill", "pkill"})
DESTRUCTIVE_GIT_SUBCOMMANDS = frozenset({"clean", "reset"})
DESTRUCTIVE_LAUNCHCTL_SUBCOMMANDS = frozenset({"bootout", "remove"})

# Read mode is semantic, not merely an executable allow-list. Some otherwise
# useful binaries can mutate state depending on subcommands or embedded code.
# Keep interpreters/build tools out of read mode and constrain multi-purpose
# CLIs to explicitly read-only subcommands.
READ_MODE_INTERPRETERS = frozenset({
    "python", "python3", "node", "npm", "npx", "make",
    "bash", "zsh", "sh", "perl", "ruby",
})
SAFE_GIT_READ_SUBCOMMANDS = frozenset({
    "status", "diff", "log", "show", "rev-parse", "rev-list", "ls-files",
    "ls-tree", "branch", "tag", "remote", "describe", "show-ref",
    "merge-base", "name-rev", "cat-file", "for-each-ref",
})
SAFE_TAILSCALE_READ_SUBCOMMANDS = frozenset({"status", "ping", "whois", "version"})
SAFE_LAUNCHCTL_READ_SUBCOMMANDS = frozenset({"print", "print-disabled", "list"})
SAFE_BREW_READ_SUBCOMMANDS = frozenset({"list", "info", "config", "doctor", "--prefix", "--version"})
FORBIDDEN_FIND_ACTIONS = frozenset({
    "-delete", "-exec", "-execdir", "-ok", "-okdir",
    "-fprint", "-fprint0", "-fprintf", "-fls",
})


def validate_read_only_argv(argv: Sequence[str]) -> tuple[str, ...]:
    """Reject argv forms that can mutate state while claiming read mode."""
    args = validate_argv(argv)
    program = _basename(args[0])
    if program in READ_MODE_INTERPRETERS:
        raise FleetError(f"read execution forbids interpreter/build tool: {program}")
    if program == "git":
        if len(args) < 2 or args[1] not in SAFE_GIT_READ_SUBCOMMANDS:
            raise FleetError("git subcommand is not allowed in read mode")
        # `git branch` and `git tag` mutate when passed operands. Permit only
        # clearly informational flag-only forms.
        if args[1] in {"branch", "tag"} and any(not x.startswith("-") for x in args[2:]):
            raise FleetError(f"git {args[1]} with operands is not read-only")
        if args[1] == "remote" and len(args) > 2 and args[2] not in {"-v", "--verbose", "show", "get-url"}:
            raise FleetError("git remote mutation is not allowed in read mode")
    elif program == "tailscale":
        if len(args) < 2 or args[1] not in SAFE_TAILSCALE_READ_SUBCOMMANDS:
            raise FleetError("tailscale subcommand is not allowed in read mode")
    elif program == "launchctl":
        if len(args) < 2 or args[1] not in SAFE_LAUNCHCTL_READ_SUBCOMMANDS:
            raise FleetError("launchctl subcommand is not allowed in read mode")
    elif program == "brew":
        if len(args) < 2 or args[1] not in SAFE_BREW_READ_SUBCOMMANDS:
            raise FleetError("brew subcommand is not allowed in read mode")
    elif program == "find":
        if any(x in FORBIDDEN_FIND_ACTIONS for x in args[1:]):
            raise FleetError("find mutation/execution actions are not allowed in read mode")
    return args


@dataclass(frozen=True)
class HostSpec:
    alias: str
    ssh_target: str = ""
    transport: str = "ssh"
    port: int = 22
    allowed_roots: tuple[str, ...] = ()
    read_commands: frozenset[str] = frozenset()
    write_commands: frozenset[str] = frozenset()
    tags: tuple[str, ...] = ()
    enabled: bool = True

    def __post_init__(self) -> None:
        if not ALIAS_RE.fullmatch(self.alias):
            raise FleetError(f"invalid host alias: {self.alias!r}")
        if self.transport not in {"ssh", "local"}:
            raise FleetError(f"invalid transport for {self.alias}: {self.transport}")
        if self.transport == "ssh" and not TARGET_RE.fullmatch(self.ssh_target):
            raise FleetError(f"invalid SSH target for {self.alias}")
        if self.transport == "local" and self.ssh_target:
            raise FleetError(f"local host {self.alias} must not define ssh_target")
        if not (1 <= int(self.port) <= 65535):
            raise FleetError(f"invalid SSH port for {self.alias}")
        for root in self.allowed_roots:
            if not root.startswith("/"):
                raise FleetError(f"allowed_roots must be absolute for {self.alias}")


@dataclass(frozen=True)
class FleetConfig:
    hosts: Mapping[str, HostSpec]
    ssh_bin: str = "/usr/bin/ssh"
    connect_timeout_seconds: int = 10
    default_timeout_seconds: int = 60
    max_timeout_seconds: int = 900
    max_output_bytes: int = 256 * 1024

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> "FleetConfig":
        p = Path(path).expanduser()
        try:
            raw = json.loads(p.read_text())
        except FileNotFoundError as exc:
            raise FleetError(f"fleet config not found: {p}") from exc
        except json.JSONDecodeError as exc:
            raise FleetError(f"invalid fleet config JSON: {p}") from exc
        if raw.get("version") != 1:
            raise FleetError("fleet config version must be 1")
        host_data = raw.get("hosts")
        if not isinstance(host_data, dict) or not host_data:
            raise FleetError("fleet config requires at least one host")
        hosts: dict[str, HostSpec] = {}
        for alias, item in host_data.items():
            if not isinstance(item, dict):
                raise FleetError(f"host {alias!r} must be an object")
            hosts[alias] = HostSpec(
                alias=alias,
                ssh_target=str(item.get("ssh_target", "")),
                transport=str(item.get("transport", "ssh")),
                port=int(item.get("port", 22)),
                allowed_roots=tuple(item.get("allowed_roots", [])),
                read_commands=frozenset(str(x) for x in item.get("read_commands", [])),
                write_commands=frozenset(str(x) for x in item.get("write_commands", [])),
                tags=tuple(str(x) for x in item.get("tags", [])),
                enabled=bool(item.get("enabled", True)),
            )
        cfg = cls(
            hosts=hosts,
            ssh_bin=str(raw.get("ssh_bin", "/usr/bin/ssh")),
            connect_timeout_seconds=int(raw.get("connect_timeout_seconds", 10)),
            default_timeout_seconds=int(raw.get("default_timeout_seconds", 60)),
            max_timeout_seconds=int(raw.get("max_timeout_seconds", 900)),
            max_output_bytes=int(raw.get("max_output_bytes", 256 * 1024)),
        )
        if cfg.connect_timeout_seconds < 1 or cfg.max_timeout_seconds < 1:
            raise FleetError("timeouts must be positive")
        if not 1 <= cfg.default_timeout_seconds <= cfg.max_timeout_seconds:
            raise FleetError("default timeout must be within max timeout")
        if not 1024 <= cfg.max_output_bytes <= 4 * 1024 * 1024:
            raise FleetError("max_output_bytes must be between 1 KiB and 4 MiB")
        return cfg


@dataclass(frozen=True)
class ExecResult:
    host: str
    argv: tuple[str, ...]
    cwd: str | None
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool = False
    stdout_truncated: bool = False
    stderr_truncated: bool = False

    def as_dict(self) -> dict:
        return {
            "host": self.host,
            "argv": list(self.argv),
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "timed_out": self.timed_out,
            "stdout_truncated": self.stdout_truncated,
            "stderr_truncated": self.stderr_truncated,
        }


def _basename(command: str) -> str:
    return command.rsplit("/", 1)[-1]


def validate_argv(argv: Sequence[str]) -> tuple[str, ...]:
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence):
        raise FleetError("argv must be an array of strings")
    if not 1 <= len(argv) <= 128:
        raise FleetError("argv must contain between 1 and 128 elements")
    normalized: list[str] = []
    total = 0
    for item in argv:
        if not isinstance(item, str):
            raise FleetError("every argv element must be a string")
        if "\x00" in item or "\n" in item or "\r" in item:
            raise FleetError("argv elements must not contain NUL/newlines")
        total += len(item)
        if total > 32768:
            raise FleetError("argv is too large")
        normalized.append(item)
    return tuple(normalized)


def is_destructive(argv: Sequence[str]) -> bool:
    args = validate_argv(argv)
    program = _basename(args[0])
    if program in DESTRUCTIVE_COMMANDS:
        return True
    if program == "git" and len(args) > 1 and args[1] in DESTRUCTIVE_GIT_SUBCOMMANDS:
        return True
    if program == "launchctl" and len(args) > 1 and args[1] in DESTRUCTIVE_LAUNCHCTL_SUBCOMMANDS:
        return True
    return False


def _within_allowed_roots(path: str, roots: Iterable[str]) -> bool:
    target = PurePosixPath(path)
    if not target.is_absolute():
        return False
    # PurePosixPath does not resolve symlinks remotely; the server-side config is
    # therefore the primary boundary.  Reject explicit .. traversal here.
    if ".." in target.parts:
        return False
    for root in roots:
        base = PurePosixPath(root)
        if target == base or base in target.parents:
            return True
    return False


class FleetRunner:
    def __init__(self, config: FleetConfig, *, run=subprocess.run):
        self.config = config
        self._run = run

    def host(self, alias: str) -> HostSpec:
        host = self.config.hosts.get(alias)
        if not host or not host.enabled:
            raise FleetError(f"unknown or disabled host: {alias}")
        return host

    def inventory(self) -> list[dict]:
        return [
            {
                "host": h.alias,
                "tags": list(h.tags),
                "transport": h.transport,
                "enabled": h.enabled,
                "allowed_roots": list(h.allowed_roots),
                "read_commands": sorted(h.read_commands),
                "write_commands": sorted(h.write_commands),
            }
            for h in sorted(self.config.hosts.values(), key=lambda x: x.alias)
        ]

    def _authorize(self, host: HostSpec, argv: Sequence[str], mode: str,
                   allow_destructive: bool) -> tuple[str, ...]:
        args = validate_argv(argv)
        program = _basename(args[0])
        if program in HARD_BLOCKED_COMMANDS:
            raise FleetError(f"command is blocked by Fleet Operator policy: {program}")
        if mode == "read":
            if program not in host.read_commands:
                raise FleetError(f"command is not allowlisted for read execution on {host.alias}: {program}")
            args = validate_read_only_argv(args)
        elif mode == "write":
            if program not in (host.read_commands | host.write_commands):
                raise FleetError(f"command is not allowlisted for execution on {host.alias}: {program}")
        else:
            raise FleetError("mode must be read or write")
        if is_destructive(args) and not allow_destructive:
            raise FleetError("destructive command requires allow_destructive=true")
        return args

    def _validate_cwd(self, host: HostSpec, cwd: str | None) -> str | None:
        if cwd is None:
            return None
        if not host.allowed_roots:
            raise FleetError(f"host {host.alias} has no allowed_roots; cwd is unavailable")
        if not _within_allowed_roots(cwd, host.allowed_roots):
            raise FleetError(f"cwd is outside allowed_roots for {host.alias}")
        return cwd

    def _ssh_prefix(self, host: HostSpec) -> list[str]:
        return [
            self.config.ssh_bin,
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=yes",
            "-o", f"ConnectTimeout={self.config.connect_timeout_seconds}",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=2",
            "-p", str(host.port),
            host.ssh_target,
            "--",
        ]

    def _remote_command(self, argv: Sequence[str], cwd: str | None) -> str:
        command = "exec " + shlex.join(list(argv))
        if cwd is not None:
            command = f"cd -- {shlex.quote(cwd)} && {command}"
        return command

    def _cap(self, value: str | bytes | None) -> tuple[str, bool]:
        if value is None:
            return "", False
        if isinstance(value, bytes):
            raw = value
        else:
            raw = value.encode("utf-8", errors="replace")
        truncated = len(raw) > self.config.max_output_bytes
        if truncated:
            raw = raw[: self.config.max_output_bytes]
        return raw.decode("utf-8", errors="replace"), truncated

    def execute(self, alias: str, argv: Sequence[str], *, cwd: str | None = None,
                timeout_seconds: int | None = None, mode: str = "write",
                allow_destructive: bool = False) -> ExecResult:
        host = self.host(alias)
        args = self._authorize(host, argv, mode, allow_destructive)
        cwd = self._validate_cwd(host, cwd)
        timeout = self.config.default_timeout_seconds if timeout_seconds is None else int(timeout_seconds)
        if not 1 <= timeout <= self.config.max_timeout_seconds:
            raise FleetError(f"timeout must be between 1 and {self.config.max_timeout_seconds} seconds")
        if host.transport == "local":
            cmd = list(args)
            run_kwargs = {"cwd": cwd}
        else:
            cmd = self._ssh_prefix(host) + [self._remote_command(args, cwd)]
            run_kwargs = {}
        started = time.monotonic()
        try:
            proc = self._run(cmd, capture_output=True, text=False, timeout=timeout, check=False, **run_kwargs)
            elapsed = time.monotonic() - started
            stdout, out_trunc = self._cap(proc.stdout)
            stderr, err_trunc = self._cap(proc.stderr)
            return ExecResult(host.alias, args, cwd, int(proc.returncode), stdout, stderr,
                              elapsed, False, out_trunc, err_trunc)
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            stdout, out_trunc = self._cap(exc.stdout)
            stderr, err_trunc = self._cap(exc.stderr)
            return ExecResult(host.alias, args, cwd, 124, stdout, stderr,
                              elapsed, True, out_trunc, err_trunc)

    def execute_many(self, aliases: Sequence[str], argv: Sequence[str], *,
                     cwd_by_host: Mapping[str, str] | None = None,
                     timeout_seconds: int | None = None, mode: str = "write",
                     allow_destructive: bool = False, max_parallel: int = 8) -> list[dict]:
        if not aliases:
            raise FleetError("at least one host is required")
        if len(set(aliases)) != len(aliases):
            raise FleetError("duplicate hosts are not allowed")
        if not 1 <= max_parallel <= 32:
            raise FleetError("max_parallel must be between 1 and 32")
        cwd_by_host = cwd_by_host or {}
        for alias in aliases:
            self.host(alias)
        results: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=min(max_parallel, len(aliases))) as pool:
            futures = {
                pool.submit(
                    self.execute, alias, argv, cwd=cwd_by_host.get(alias),
                    timeout_seconds=timeout_seconds, mode=mode,
                    allow_destructive=allow_destructive,
                ): alias
                for alias in aliases
            }
            for future in as_completed(futures):
                alias = futures[future]
                try:
                    results[alias] = future.result().as_dict()
                except Exception as exc:  # keep fan-out failures isolated per host
                    results[alias] = {"host": alias, "error": str(exc)}
        return [results[a] for a in aliases]

    def read_file(self, alias: str, path: str, *, max_bytes: int = 131072) -> dict:
        host = self.host(alias)
        if not 1 <= max_bytes <= self.config.max_output_bytes:
            raise FleetError(f"max_bytes must be between 1 and {self.config.max_output_bytes}")
        if not _within_allowed_roots(path, host.allowed_roots):
            raise FleetError(f"path is outside allowed_roots for {alias}")
        # `head` must be explicitly read-allowlisted on the host.
        result = self.execute(alias, ["head", "-c", str(max_bytes), "--", path],
                              mode="read", timeout_seconds=60)
        payload = result.as_dict()
        payload["path"] = path
        return payload

    def host_status(self, alias: str) -> dict:
        # Keep status intentionally boring/read-only; more diagnostics can use
        # fleet_exec_read with the host's explicit read allow-list.
        result = self.execute(alias, ["uname", "-a"], mode="read", timeout_seconds=20)
        return result.as_dict()
