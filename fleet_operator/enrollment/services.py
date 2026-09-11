"""Generate user-level service definitions. This module never installs or reloads one."""
import json
import os
import plistlib
from pathlib import Path
from operation_contracts.common import ContractError


def render(command, label, *, platform, log_dir):
    if not label or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-" for c in label):
        raise ContractError("invalid user service label")
    if not isinstance(command, list) or not command or not Path(command[0]).is_absolute():
        raise ContractError("service requires a fixed absolute executable")
    if any(not isinstance(v, str) or any(c in v for c in "\0\r\n") for v in command):
        raise ContractError("invalid service argument")
    log = Path(log_dir).expanduser()
    if not log.is_absolute():
        raise ContractError("log directory must be absolute")
    if platform == "launchd":
        return plistlib.dumps({"Label":label,"ProgramArguments":command,"RunAtLoad":True,"KeepAlive":True,
                              "ThrottleInterval":10,"ProcessType":"Background","Umask":0o077,
                              "StandardOutPath":str(log/(label+".out.log")),
                              "StandardErrorPath":str(log/(label+".err.log")),
                              "EnvironmentVariables":{"PYTHONDONTWRITEBYTECODE":"1"}}).decode()
    if platform != "systemd":
        raise ContractError("unsupported user service format")
    # systemd has its own quoting and percent/variable expansion; no shell is involved.
    def quote(value):
        return json.dumps(value.replace("%", "%%").replace("$", "$$"), ensure_ascii=False)
    return ("[Unit]\nDescription=Fleet Operator "+label+"\nAfter=network-online.target\n\n"
            "[Service]\nType=simple\nExecStart="+" ".join(quote(v) for v in command)+"\n"
            "Restart=on-failure\nRestartSec=5\nKillMode=mixed\nTimeoutStopSec=15\nUMask=0077\n"
            "NoNewPrivileges=true\nEnvironment=PYTHONDONTWRITEBYTECODE=1\n\n"
            "[Install]\nWantedBy=default.target\n")


def write_definition(path, content):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as out:
        out.write(content)
    return {"definition":str(path),"installed":False,"loaded":False}
