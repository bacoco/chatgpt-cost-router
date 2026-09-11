"""Conservative public gateway commands. General computation belongs in B profiles."""
from pathlib import PurePosixPath

SAFE_TOOLS = {"uname","hostname","whoami","id","sw_vers","uptime","df"}
VERSIONS = {"python","python3","node","npm","npx","brew","codex","claude"}
SYSTEM_DIRS = {"/bin","/usr/bin","/sbin","/usr/sbin","/usr/local/bin","/opt/homebrew/bin"}
GIT_READ = {"status","diff","log","show","rev-parse","ls-files","ls-tree"}
GIT_UNSAFE = {"--output","--ext-diff","--textconv","--exec-path","--paginate","-c","--config-env","--no-index","--filters","--pathspec-from-file","--exclude-from","--alternate-refs","--git-dir","--work-tree","--namespace","--super-prefix","--separate-git-dir","-C"}


def read_allowed(argv):
    path, args = PurePosixPath(argv[0]), list(argv[1:])
    if path.is_absolute() and str(path.parent) not in SYSTEM_DIRS:
        return False
    if not path.is_absolute() and ("/" in argv[0] or argv[0].startswith(".")):
        return False
    name = path.name
    if name in SAFE_TOOLS:
        if name in {"hostname", "whoami", "uptime"}:
            return not args
        if name == "id":
            return not args or args in [["-u"], ["-g"], ["-G"], ["-un"], ["-gn"]]
        if name == "uname":
            return not args or len(args) == 1 and args[0] in {"-a", "-s", "-r", "-m", "-n", "-p", "-v"}
        if name == "sw_vers":
            return not args or args in [["-productVersion"], ["-buildVersion"], ["-productName"]]
        return not args or args in [["-h"], ["-k"], ["-P"]]
    if name in VERSIONS:
        return args in [["--version"],["-V"]]
    if name == "git":
        return bool(args and args[0] in GIT_READ
                    and all(not value.startswith("/") and ".." not in value.split("/") for value in args[1:])
                    and not any(
            any(value == flag or value.startswith(flag+"=") for flag in GIT_UNSAFE) for value in args[1:]))
    if name == "tailscale":
        return args in [["status"],["status","--json"],["serve","status"],["serve","status","--json"],["version"]]
    if name == "launchctl":
        return len(args) == 2 and args[0] == "print" and args[1].startswith("gui/")
    return False


def write_allowed(argv):
    return read_allowed(argv) or list(argv) == ["git","pull","--ff-only"]
