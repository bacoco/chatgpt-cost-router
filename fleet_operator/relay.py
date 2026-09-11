"""GitHub-backed command relay for Fleet Operator.

This is the compatibility path for ChatGPT contexts that can write GitHub but
cannot invoke custom MCP write actions.  Jobs live on a dedicated command branch;
execution occurs locally through the same FleetRunner policy as the MCP app.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .core import FleetConfig, FleetError, FleetRunner

JOB_RE = re.compile(r"^[A-Za-z0-9._-]{8,80}$")
ACTIONS = frozenset({"status", "exec_read", "exec_write", "read_file", "git_pull"})


class RelayError(FleetError):
    pass


@dataclass(frozen=True)
class RelayConfig:
    repo: Path
    fleet_config: Path
    command_branch: str = "fleet/commands"
    poll_seconds: int = 30
    result_branch_prefix: str = "fleet/results/"
    state_dir: Path = Path("~/.local/state/chatgpt-cost-router/fleet-relay")

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> "RelayConfig":
        p = Path(path).expanduser()
        try:
            data = json.loads(p.read_text())
        except FileNotFoundError as exc:
            raise RelayError(f"relay config not found: {p}") from exc
        except json.JSONDecodeError as exc:
            raise RelayError(f"invalid relay config JSON: {p}") from exc
        if data.get("version") != 1:
            raise RelayError("relay config version must be 1")
        cfg = cls(
            repo=Path(data["repo"]).expanduser().resolve(),
            fleet_config=Path(data["fleet_config"]).expanduser().resolve(),
            command_branch=str(data.get("command_branch", "fleet/commands")),
            poll_seconds=int(data.get("poll_seconds", 30)),
            result_branch_prefix=str(data.get("result_branch_prefix", "fleet/results/")),
            state_dir=Path(data.get("state_dir", "~/.local/state/chatgpt-cost-router/fleet-relay")).expanduser(),
        )
        if not (cfg.repo / ".git").exists():
            raise RelayError(f"relay repo is not a git checkout: {cfg.repo}")
        if not cfg.fleet_config.is_file():
            raise RelayError(f"fleet config not found: {cfg.fleet_config}")
        if not 15 <= cfg.poll_seconds <= 3600:
            raise RelayError("poll_seconds must be between 15 and 3600")
        if not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", cfg.command_branch):
            raise RelayError("invalid command_branch")
        if not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}/", cfg.result_branch_prefix):
            raise RelayError("result_branch_prefix must be a safe branch prefix ending in /")
        return cfg


class GitBus:
    def __init__(self, config: RelayConfig, *, run=subprocess.run):
        self.config = config
        self._run = run

    @property
    def remote_ref(self) -> str:
        return f"refs/remotes/origin/{self.config.command_branch}"

    def _git(self, args: list[str], *, input_text: str | None = None,
             env: Mapping[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
        proc = self._run(
            ["git", "-C", str(self.config.repo), *args], input=input_text,
            capture_output=True, text=True, env=dict(env) if env is not None else None,
            check=False,
        )
        if check and proc.returncode != 0:
            raise RelayError((proc.stderr or proc.stdout or f"git {' '.join(args)} failed").strip())
        return proc

    def fetch(self) -> None:
        refspec = f"+refs/heads/{self.config.command_branch}:{self.remote_ref}"
        self._git(["fetch", "--quiet", "origin", refspec])

    def list_jobs(self) -> list[str]:
        proc = self._git(["ls-tree", "-r", "--name-only", self.remote_ref, "--", ".fleet/jobs"])
        return sorted(x for x in proc.stdout.splitlines() if x.startswith(".fleet/jobs/") and x.endswith(".json"))

    def read_job(self, path: str) -> tuple[dict, str]:
        if not path.startswith(".fleet/jobs/") or not path.endswith(".json"):
            raise RelayError("invalid job path")
        content = self._git(["show", f"{self.remote_ref}:{path}"]).stdout
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RelayError(f"invalid job JSON: {path}") from exc
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return payload, sha

    def push_result(self, job_id: str, payload: Mapping) -> str:
        if not JOB_RE.fullmatch(job_id):
            raise RelayError("invalid job id")
        self._git(["fetch", "--quiet", "origin", "+refs/heads/main:refs/remotes/origin/main"])
        self.config.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        with tempfile.TemporaryDirectory(dir=self.config.state_dir) as td:
            idx = Path(td) / "index"
            env = os.environ.copy()
            env["GIT_INDEX_FILE"] = str(idx)
            env.setdefault("GIT_AUTHOR_NAME", "Fleet Operator")
            env.setdefault("GIT_AUTHOR_EMAIL", "fleet-operator@localhost")
            env.setdefault("GIT_COMMITTER_NAME", "Fleet Operator")
            env.setdefault("GIT_COMMITTER_EMAIL", "fleet-operator@localhost")
            self._git(["read-tree", "refs/remotes/origin/main"], env=env)
            body = json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"
            blob = self._git(["hash-object", "-w", "--stdin"], input_text=body, env=env).stdout.strip()
            result_path = f".fleet/results/{job_id}.json"
            self._git(["update-index", "--add", "--cacheinfo", f"100644,{blob},{result_path}"], env=env)
            tree = self._git(["write-tree"], env=env).stdout.strip()
            parent = self._git(["rev-parse", "refs/remotes/origin/main"]).stdout.strip()
            commit = self._git(["commit-tree", tree, "-p", parent], input_text=f"fleet: result {job_id}\n", env=env).stdout.strip()
            branch = self.config.result_branch_prefix + job_id
            self._git(["push", "--force-with-lease", "origin", f"{commit}:refs/heads/{branch}"], env=env)
            return branch


class Ledger:
    def __init__(self, path: Path):
        self.path = path.expanduser()

    def load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "completed": {}}
        data = json.loads(self.path.read_text())
        if data.get("version") != 1 or not isinstance(data.get("completed"), dict):
            raise RelayError("invalid relay ledger")
        return data

    def seen(self, job_id: str) -> str | None:
        return self.load()["completed"].get(job_id)

    def mark(self, job_id: str, job_sha: str) -> None:
        data = self.load()
        old = data["completed"].get(job_id)
        if old and old != job_sha:
            raise RelayError("job id replayed with different contents")
        data["completed"][job_id] = job_sha
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)
        os.chmod(self.path, 0o600)


# Historical entry points now share the canonical non-replaying runtime.
def validate_job(payload, *, path, now=None):
    from .relay_service import validate_job as implementation
    return implementation(payload, path=path, now=now)


def execute_job(runner, job):
    from .relay_service import execute_job as implementation
    return implementation(runner, job)


def run_once(config, *, bus=None, clock=time.time):
    from .relay_service import run_once as implementation
    return implementation(config, bus=bus, clock=clock)


def run_forever(config):
    from .relay_service import run_forever as implementation
    return implementation(config)
