"""macOS LaunchAgent packaging for Fleet Operator and Secure MCP Tunnel."""
from __future__ import annotations

import json
import os
import plistlib
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Mapping

from .core import FleetError

SERVER_LABEL = "pro.chatgpt-cost-router.fleet-operator"
TUNNEL_LABEL = "pro.chatgpt-cost-router.fleet-tunnel"
RELAY_LABEL = "pro.chatgpt-cost-router.fleet-relay"
TUNNEL_ID_RE = re.compile(r"^tunnel_[0-9a-f]{32}$")


class InstallError(FleetError):
    pass


def _write_private(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data)
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    os.chmod(path, 0o600)


def write_json_private(path: Path, payload: Mapping) -> None:
    _write_private(path, json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")


def write_plist(path: Path, payload: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        plistlib.dump(dict(payload), fh, sort_keys=True)
    os.chmod(path, 0o600)


def launch_plist(label: str, argv: list[str], log_dir: Path, environment: Mapping[str, str] | None = None) -> dict:
    payload = {"Label": label, "ProgramArguments": argv, "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False}, "ProcessType": "Background", "StandardOutPath": str(log_dir / f"{label}.out.log"), "StandardErrorPath": str(log_dir / f"{label}.err.log")}
    if environment:
        payload["EnvironmentVariables"] = dict(environment)
    return payload


def _bootstrap(plist: Path, label: str, *, dry_run: bool = False, run=subprocess.run, uid: int | None = None) -> None:
    if dry_run:
        return
    uid = os.getuid() if uid is None else uid
    domain = f"gui/{uid}"
    service = f"{domain}/{label}"
    run(["launchctl", "bootout", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    proc = run(["launchctl", "bootstrap", domain, str(plist)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise InstallError((proc.stderr or proc.stdout or "launchctl bootstrap failed").strip())
    run(["launchctl", "kickstart", "-k", service], check=True)


MIN_MCP_PYTHON = (3, 10)


def _candidate_pythons() -> list[str]:
    """Return likely Python executables, preferring modern Homebrew versions."""
    candidates: list[str] = []
    for base in ("/opt/homebrew/bin", "/usr/local/bin"):
        for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3.10", "python3"):
            path = str(Path(base) / name)
            if Path(path).is_file():
                candidates.append(path)
    for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3.10", "python3"):
        value = shutil.which(name)
        if value:
            candidates.append(value)
    candidates.append(sys.executable)
    return list(dict.fromkeys(str(Path(x).resolve()) for x in candidates if x))


def compatible_python(*, run=subprocess.run) -> tuple[str, tuple[int, int]]:
    """Find Python >= 3.10, required by the current MCP Python SDK."""
    for binary in _candidate_pythons():
        proc = run(
            [binary, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            continue
        try:
            major, minor = (int(x) for x in proc.stdout.strip().split(".", 1))
        except (TypeError, ValueError):
            continue
        if (major, minor) >= MIN_MCP_PYTHON:
            return binary, (major, minor)
    raise InstallError(
        "Fleet Operator MCP server requires Python >= 3.10. "
        "Install a modern Python (for example Homebrew python@3.11+) or run relay-only."
    )


def _venv_python(home: Path, version: tuple[int, int]) -> Path:
    tag = f"py{version[0]}{version[1]}"
    return home / f".local/share/chatgpt-cost-router/fleet-operator-venv-{tag}/bin/python"


def install_server(*, repo: Path, home: Path, config: Path, port: int = 8810, install_dependencies: bool = True, dry_run: bool = False, run=subprocess.run) -> list[Path]:
    repo = repo.expanduser().resolve()
    config = config.expanduser().resolve()
    required = [repo / "scripts/fleet_operator_server.py", repo / "fleet_operator/core.py", repo / "fleet_operator/mcp_server.py", repo / "requirements-fleet-operator.txt", config]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise InstallError("missing Fleet Operator files: " + ", ".join(missing))
    if not 1024 <= int(port) <= 65535:
        raise InstallError("Fleet Operator port must be between 1024 and 65535")
    if dry_run:
        version = MIN_MCP_PYTHON
        source_python = sys.executable
    else:
        source_python, version = compatible_python(run=run)
    python = _venv_python(home, version)
    if not dry_run and install_dependencies:
        venv_dir = python.parents[1]
        if not python.exists():
            run([source_python, "-m", "venv", str(venv_dir)], check=True)
        run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(repo / "requirements-fleet-operator.txt")], check=True)
    if not dry_run and not python.exists():
        raise InstallError(f"Fleet Operator venv Python not found: {python}")
    logs = home / ".local/state/chatgpt-cost-router/fleet-operator"
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    plist = home / "Library/LaunchAgents" / f"{SERVER_LABEL}.plist"
    env = {"FLEET_OPERATOR_CONFIG": str(config), "FLEET_OPERATOR_HOST": "127.0.0.1", "FLEET_OPERATOR_PORT": str(port)}
    write_plist(plist, launch_plist(SERVER_LABEL, [str(python), str(repo / "scripts/fleet_operator_server.py")], logs, env))
    _bootstrap(plist, SERVER_LABEL, dry_run=dry_run, run=run)
    return [plist]


def tunnel_yaml(*, tunnel_id: str, key_file: Path, mcp_port: int = 8810, health_port: int = 8811) -> str:
    if not TUNNEL_ID_RE.fullmatch(tunnel_id):
        raise InstallError("invalid tunnel id")
    key_file = key_file.expanduser().resolve()
    if not 1024 <= int(mcp_port) <= 65535 or not 1024 <= int(health_port) <= 65535:
        raise InstallError("invalid local tunnel port")
    return f"""config_version: 1
control_plane:
  tunnel_id: {tunnel_id}
  api_key: file:{key_file}
mcp:
  server_urls:
    - channel: main
      url: http://127.0.0.1:{mcp_port}/mcp
health:
  listen_addr: 127.0.0.1:{health_port}
admin_ui:
  open_browser: false
log:
  level: info
  format: json
"""


def install_tunnel(*, home: Path, tunnel_id: str, key_file: Path, mcp_port: int = 8810, health_port: int = 8811, tunnel_client: str | None = None, dry_run: bool = False, run=subprocess.run) -> list[Path]:
    binary = tunnel_client or shutil.which("tunnel-client")
    if not binary:
        raise InstallError("tunnel-client not found; install with: brew install openai/tools/tunnel-client")
    key_file = key_file.expanduser().resolve()
    if not dry_run:
        if not key_file.is_file():
            raise InstallError(f"runtime API key file not found: {key_file}")
        mode = key_file.stat().st_mode & 0o777
        if mode & 0o077:
            raise InstallError("runtime API key file must not be group/world accessible (use chmod 600)")
    config = home / ".config/chatgpt-cost-router/fleet-tunnel.yaml"
    _write_private(config, tunnel_yaml(tunnel_id=tunnel_id, key_file=key_file, mcp_port=mcp_port, health_port=health_port))
    logs = home / ".local/state/chatgpt-cost-router/fleet-operator"
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    plist = home / "Library/LaunchAgents" / f"{TUNNEL_LABEL}.plist"
    write_plist(plist, launch_plist(TUNNEL_LABEL, [str(Path(binary).resolve()), "run", "--config", str(config)], logs))
    _bootstrap(plist, TUNNEL_LABEL, dry_run=dry_run, run=run)
    return [config, plist]


def launchd_status(home: Path, *, run=subprocess.run, uid: int | None = None) -> dict:
    uid = os.getuid() if uid is None else uid
    out = {}
    for name, label in (("server", SERVER_LABEL), ("tunnel", TUNNEL_LABEL), ("relay", RELAY_LABEL)):
        plist = home / "Library/LaunchAgents" / f"{label}.plist"
        proc = run(["launchctl", "print", f"gui/{uid}/{label}"], capture_output=True, text=True)
        out[name] = {"installed": plist.exists(), "loaded": proc.returncode == 0}
    return out


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


DEFAULT_READ_COMMANDS = ["uname", "hostname", "whoami", "id", "sw_vers", "uptime", "df", "du", "ps", "pgrep", "ls", "stat", "cat", "head", "tail", "grep", "find", "git", "python3", "python", "pytest", "node", "npm", "npx", "tailscale", "launchctl", "brew", "make"]
DEFAULT_WRITE_COMMANDS = ["git", "python3", "python", "bash", "zsh", "sh", "launchctl", "kill", "pkill", "mkdir", "touch", "cp", "mv", "rm", "sed", "perl", "npm", "npx", "node", "make", "brew"]


def init_fleet_config(*, path: Path, local_host: tuple[str, str] | None, ssh_hosts: list[tuple[str, str, str]]) -> Path:
    hosts = {}
    if local_host is not None:
        alias, root = local_host
        hosts[alias] = {"transport": "local", "allowed_roots": [str(Path(root).expanduser().resolve())], "read_commands": DEFAULT_READ_COMMANDS, "write_commands": DEFAULT_WRITE_COMMANDS, "tags": ["gateway", "local"]}
    for alias, target, root in ssh_hosts:
        if alias in hosts:
            raise InstallError(f"duplicate fleet host alias: {alias}")
        hosts[alias] = {"transport": "ssh", "ssh_target": target, "allowed_roots": [root], "read_commands": DEFAULT_READ_COMMANDS, "write_commands": DEFAULT_WRITE_COMMANDS, "tags": ["remote", "ssh"]}
    if not hosts:
        raise InstallError("at least one local or SSH host is required")
    payload = {"version": 1, "ssh_bin": shutil.which("ssh") or "/usr/bin/ssh", "connect_timeout_seconds": 10, "default_timeout_seconds": 60, "max_timeout_seconds": 900, "max_output_bytes": 262144, "hosts": hosts}
    path = path.expanduser().resolve()
    write_json_private(path, payload)
    return path


def install_relay(*, repo: Path, home: Path, fleet_config: Path, command_branch: str = "fleet/commands", poll_seconds: int = 30, dry_run: bool = False, run=subprocess.run) -> list[Path]:
    repo = repo.expanduser().resolve()
    fleet_config = fleet_config.expanduser().resolve()
    required = [repo / "scripts/fleet_operator_relay.py", repo / "fleet_operator/relay.py", fleet_config]
    missing = [str(x) for x in required if not x.is_file()]
    if missing:
        raise InstallError("missing relay files: " + ", ".join(missing))
    if not (repo / ".git").exists():
        raise InstallError("relay requires a git checkout of chatgpt-cost-router")
    if not 15 <= int(poll_seconds) <= 3600:
        raise InstallError("poll_seconds must be between 15 and 3600")
    config = home / ".config/chatgpt-cost-router/fleet-relay.json"
    state = home / ".local/state/chatgpt-cost-router/fleet-relay"
    write_json_private(config, {"version": 1, "repo": str(repo), "fleet_config": str(fleet_config), "command_branch": command_branch, "poll_seconds": int(poll_seconds), "result_branch_prefix": "fleet/results/", "state_dir": str(state)})
    logs = home / ".local/state/chatgpt-cost-router/fleet-operator"
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    plist = home / "Library/LaunchAgents" / f"{RELAY_LABEL}.plist"
    write_plist(plist, launch_plist(RELAY_LABEL, [sys.executable, str(repo / "scripts/fleet_operator_relay.py"), "--config", str(config)], logs))
    _bootstrap(plist, RELAY_LABEL, dry_run=dry_run, run=run)
    return [config, plist]
