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
            "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit", str(container["pids_limit"]),
            "--cpus", str(container["cpus"]), "--memory", str(container["memory_mb"])+"m",
            "--user", f"{os.getuid()}:{os.getgid()}", "--workdir", "/workspace",
            "--mount", f"type=bind,source={work},target=/workspace",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m", "--env", "HOME=/tmp",
            "--env", "FLEET_INPUT_FILE=/workspace/.fleet-runtime/input.json",
            "--env", f"FLEET_RUN_ID={run_id}", container["image"], *profile["argv"]]
    return argv, env
