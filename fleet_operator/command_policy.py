"""Conservative public gateway commands. General computation belongs in B profiles."""
from pathlib import PurePosixPath

SAFE_TOOLS = {"uname","hostname","whoami","id","sw_vers","uptime","df"}
VERSIONS = {"python","python3","node","npm","npx","brew","codex","claude"}
SYSTEM_DIRS = {"/bin","/usr/bin","/sbin","/usr/sbin","/usr/local/bin","/opt/homebrew/bin"}
GIT_READ = {"status","diff","log","show","rev-parse","ls-files","ls-tree"}
GIT_UNSAFE = {"--output","--ext-diff","--textconv","--exec-path","--paginate","-c","--config-env"}


def read_allowed(argv):
    path, args = PurePosixPath(argv[0]), list(argv[1:])
    if path.is_absolute() and str(path.parent) not in SYSTEM_DIRS:
        return False
    name = path.name
    if name in SAFE_TOOLS:
        return name != "hostname" or not args
    if name in VERSIONS:
        return args in [["--version"],["-V"]]
    if name == "git":
        return bool(args and args[0] in GIT_READ and not any(
            any(value == flag or value.startswith(flag+"=") for flag in GIT_UNSAFE) for value in args[1:]))
    if name == "tailscale":
        return args in [["status"],["status","--json"],["serve","status"],["serve","status","--json"],["version"]]
    if name == "launchctl":
        return len(args) == 2 and args[0] == "print" and args[1].startswith("gui/")
    return False


def write_allowed(argv):
    return read_allowed(argv) or list(argv) == ["git","pull","--ff-only"]
