"""macOS LaunchAgent helpers for the private worker mesh.

This module only renders/writes per-user configuration and plists. It never
stores credentials in the repository and never requires root privileges.
"""
from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
from pathlib import Path
from typing import Mapping, Sequence


class LaunchdError(ValueError):
    """Safe configuration/install error."""


LABELS = {
    "control": "pro.chatgpt-cost-router.mesh-control",
    "remote-worker": "pro.chatgpt-cost-router.remote-worker",
    "mesh-node": "pro.chatgpt-cost-router.mesh-node",
}


def private_json(path: Path, payload: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    os.chmod(path, 0o600)


def launchagent_plist(label: str, python_bin: str, runner: Path, role: str,
                      config: Path, log_dir: Path) -> dict:
    if role not in LABELS:
        raise LaunchdError(f"unknown service role: {role}")
    if label != LABELS[role]:
        raise LaunchdError("label/role mismatch")
    return {
        "Label": label,
        "ProgramArguments": [python_bin, str(runner), role, "--config", str(config)],
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
        "ProcessType": "Background",
        "StandardOutPath": str(log_dir / f"{role}.out.log"),
        "StandardErrorPath": str(log_dir / f"{role}.err.log"),
    }


def write_plist(path: Path, payload: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        plistlib.dump(dict(payload), handle, sort_keys=True)
    os.chmod(path, 0o600)


def executable(name: str) -> str:
    value = shutil.which(name)
    if not value:
        raise LaunchdError(f"required executable not found: {name}")
    return str(Path(value).resolve())


def validate_repo(repo: Path) -> Path:
    repo = repo.expanduser().resolve()
    required = [
        repo / "scripts" / "mesh_service_runner.py",
        repo / "scripts" / "mesh_control_server.py",
        repo / "scripts" / "remote_worker_server.py",
        repo / "scripts" / "mesh_node_agent.py",
        repo / "examples" / "workers.json",
    ]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise LaunchdError("repository is missing required files: " + ", ".join(missing))
    return repo


def bootstrap_agent(plist: Path, label: str, *, dry_run: bool = False,
                    run=subprocess.run, uid: int | None = None) -> None:
    uid = os.getuid() if uid is None else uid
    domain = f"gui/{uid}"
    service = f"{domain}/{label}"
    if dry_run:
        return
    run(["launchctl", "bootout", service], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, check=False)
    result = run(["launchctl", "bootstrap", domain, str(plist)], capture_output=True, text=True)
    if result.returncode != 0:
        raise LaunchdError((result.stderr or result.stdout or "launchctl bootstrap failed").strip())
    run(["launchctl", "kickstart", "-k", service], check=True)


def bootout_agent(label: str, *, dry_run: bool = False,
                  run=subprocess.run, uid: int | None = None) -> None:
    uid = os.getuid() if uid is None else uid
    if dry_run:
        return
    run(["launchctl", "bootout", f"gui/{uid}/{label}"], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, check=False)


def install_control(*, repo: Path, home: Path, allowed_users: str,
                    dry_run: bool = False) -> list[Path]:
    if not allowed_users.strip():
        raise LaunchdError("at least one allowed Tailscale user is required")
    repo = validate_repo(repo)
    python_bin = executable("python3")
    tailscale_bin = executable("tailscale")
    config = home / ".config/chatgpt-cost-router/mesh-control.json"
    logs = home / ".local/state/chatgpt-cost-router/launchd"
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_json(config, {
        "version": 1,
        "repo": str(repo),
        "allowed_users": allowed_users,
        "tailscale_bin": tailscale_bin,
        "https_port": 8444,
        "backend_port": 8790,
    })
    label = LABELS["control"]
    plist = home / "Library/LaunchAgents" / f"{label}.plist"
    write_plist(plist, launchagent_plist(label, python_bin,
        repo / "scripts/mesh_service_runner.py", "control", config, logs))
    bootstrap_agent(plist, label, dry_run=dry_run)
    return [config, plist]


def install_worker_node(*, repo: Path, home: Path, control_url: str,
                        allowed_users: str, workers: str,
                        dry_run: bool = False) -> list[Path]:
    if not control_url.startswith("https://") or ".ts.net" not in control_url:
        raise LaunchdError("control_url must be a private Tailscale Serve https URL")
    if not allowed_users.strip():
        raise LaunchdError("at least one allowed Tailscale user is required")
    if not workers.strip():
        raise LaunchdError("at least one worker alias is required")
    repo = validate_repo(repo)
    python_bin = executable("python3")
    tailscale_bin = executable("tailscale")
    codex_bin = executable("codex")
    logs = home / ".local/state/chatgpt-cost-router/launchd"
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    remote_config = home / ".config/chatgpt-cost-router/remote-worker.json"
    node_config = home / ".config/chatgpt-cost-router/mesh-node.json"
    private_json(remote_config, {
        "version": 1,
        "repo": str(repo),
        "allowed_users": allowed_users,
        "workers": workers,
        "tailscale_bin": tailscale_bin,
        "codex_bin": codex_bin,
        "https_port": 8443,
        "backend_port": 8787,
    })
    private_json(node_config, {
        "version": 1,
        "repo": str(repo),
        "control_url": control_url.rstrip("/"),
        "workers": workers,
        "tailscale_bin": tailscale_bin,
        "codex_bin": codex_bin,
        "worker_port": 8443,
        "heartbeat_seconds": 30,
    })
    created = [remote_config, node_config]
    for role, config in (("remote-worker", remote_config), ("mesh-node", node_config)):
        label = LABELS[role]
        plist = home / "Library/LaunchAgents" / f"{label}.plist"
        write_plist(plist, launchagent_plist(label, python_bin,
            repo / "scripts/mesh_service_runner.py", role, config, logs))
        bootstrap_agent(plist, label, dry_run=dry_run)
        created.append(plist)
    return created


def remove(role: str, *, home: Path, dry_run: bool = False,
           run=subprocess.run) -> list[Path]:
    roles: Sequence[str]
    configs: Sequence[Path]
    if role == "control":
        roles = ["control"]
        configs = [home / ".config/chatgpt-cost-router/mesh-control.json"]
    elif role == "worker-node":
        roles = ["mesh-node", "remote-worker"]
        configs = [home / ".config/chatgpt-cost-router/mesh-node.json",
                   home / ".config/chatgpt-cost-router/remote-worker.json"]
    else:
        raise LaunchdError(f"unknown uninstall role: {role}")
    removed = []
    for item in roles:
        label = LABELS[item]
        bootout_agent(label, dry_run=dry_run, run=run)
        plist = home / "Library/LaunchAgents" / f"{label}.plist"
        if plist.exists():
            if not dry_run:
                plist.unlink()
            removed.append(plist)
    for config in configs:
        if config.exists():
            if not dry_run:
                config.unlink()
            removed.append(config)
    return removed
