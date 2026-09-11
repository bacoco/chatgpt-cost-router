"""Fixed profiles with clean environments and optional real container containment."""
import os


def command(profile, root, work, home, run_id):
    env = {"PATH":"/usr/bin:/bin:/usr/sbin:/sbin", "LANG":"C.UTF-8", "TZ":"UTC",
           "HOME":str(home), "TMPDIR":str(root / "tmp"),
           "FLEET_INPUT_FILE":str(work / ".fleet-runtime/input.json"), "FLEET_RUN_ID":run_id,
           "PYTHONUNBUFFERED":"1", "PYTHONDONTWRITEBYTECODE":"1"}
    env.update(profile.get("environment", {}))
    (root / "tmp").mkdir(mode=0o700, exist_ok=True)
    if profile["isolation"] == "trusted-local":
        return list(profile["argv"]), env
    container = profile["container"]
    argv = [container["engine"], "run", "--rm", "--pull=never", "--network=none", "--read-only",
            "--cidfile", str(root / "container.cid"), "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit", str(container["pids_limit"]),
            "--cpus", str(container["cpus"]), "--memory", str(container["memory_mb"])+"m",
            "--user", f"{os.getuid()}:{os.getgid()}", "--workdir", "/workspace",
            "--mount", f"type=bind,source={work},target=/workspace",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m", "--env", "HOME=/tmp",
            "--env", "FLEET_INPUT_FILE=/workspace/.fleet-runtime/input.json",
            "--env", f"FLEET_RUN_ID={run_id}", container["image"], *profile["argv"]]
    from ..host_io import safe_environment
    # The engine uses the operator's image store; only explicit --env flags enter the container.
    return argv, safe_environment(os.environ)


def cleanup_container(profile, root):
    """The supervisor removes only the exact container ID created by its own engine run."""
    import re
    import subprocess
    from operation_contracts.common import ContractError
    path = root / "container.cid"
    if not path.exists():
        raise ContractError("container creation outcome has no owned ID; cleanup is uncertain")
    if path.is_symlink():
        raise ContractError("invalid owned container ID receipt")
    id_ = path.read_text().strip()
    if not re.fullmatch(r"[0-9a-f]{64}", id_):
        raise ContractError("invalid owned container ID")
    from ..host_io import safe_environment
    result = subprocess.run([profile["container"]["engine"], "rm", "--force", id_],
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=30, check=False, env=safe_environment(os.environ))
    if result.returncode != 0:
        # --rm may have removed it first. Check the engine's container ID list, not an error string.
        from ..bounded_process import run
        listed = run([profile["container"]["engine"], "ps", "--all", "--no-trunc", "--quiet"],
                     text=True, timeout=30, max_bytes=1048576, env=safe_environment(os.environ))
        if listed.returncode or len(listed.stdout.encode()) > 1048576 or id_ in listed.stdout.splitlines():
            raise ContractError("container removal could not be verified")
    return {"container_id":id_, "cleanup_verified":True}
