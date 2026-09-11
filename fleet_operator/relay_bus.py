"""Idempotent GitHub result publication without force-pushing existing evidence."""
import json
import os
import tempfile
from pathlib import Path
from .relay import GitBus, RelayError, JOB_RE
from .redaction import redact


class ReliableBus(GitBus):
    def _git(self, args, *, input_text=None, env=None, check=True):
        result = self._run(["git","-C",str(self.config.repo),*args],input=input_text,
                           capture_output=True,text=True,env=dict(env) if env is not None else None,
                           timeout=120,check=False)
        if check and result.returncode:
            raise RelayError("GitHub relay transport failed")
        return result

    def push_result(self, job_id, payload):
        if not JOB_RE.fullmatch(job_id):
            raise RelayError("invalid job id")
        branch = self.config.result_branch_prefix+job_id
        path = ".fleet/results/"+job_id+".json"
        safe = redact(dict(payload))
        body = json.dumps(safe,indent=2,sort_keys=True)+"\n"
        self._git(["fetch","--quiet","origin","+refs/heads/main:refs/remotes/origin/main"])
        self.config.state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
        with tempfile.TemporaryDirectory(dir=self.config.state_dir) as directory:
            env = os.environ.copy()
            env.update(GIT_INDEX_FILE=str(Path(directory)/"index"),GIT_AUTHOR_NAME="Fleet Operator",
                       GIT_AUTHOR_EMAIL="fleet-operator@localhost",GIT_COMMITTER_NAME="Fleet Operator",
                       GIT_COMMITTER_EMAIL="fleet-operator@localhost")
            self._git(["read-tree","refs/remotes/origin/main"],env=env)
            blob = self._git(["hash-object","-w","--stdin"],input_text=body,env=env).stdout.strip()
            self._git(["update-index","--add","--cacheinfo",f"100644,{blob},{path}"],env=env)
            tree = self._git(["write-tree"],env=env).stdout.strip()
            parent = self._git(["rev-parse","refs/remotes/origin/main"],env=env).stdout.strip()
            commit = self._git(["commit-tree",tree,"-p",parent],input_text="fleet: result "+job_id+" [skip ci]\n",env=env).stdout.strip()
            sent = self._git(["push","origin",f"{commit}:refs/heads/{branch}"],env=env,check=False)
            if sent.returncode:
                self._git(["fetch","--quiet","origin","refs/heads/"+branch])
                existing = self._git(["show","FETCH_HEAD:"+path]).stdout
                if json.loads(existing) != safe:
                    raise RelayError("existing result differs; refusing to overwrite evidence")
        return branch
