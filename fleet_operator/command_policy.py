"""Conservative inspection only. Mutation requires an operator-owned B profile."""
import re
from pathlib import PurePosixPath

SYSTEM_DIRS = {'/bin', '/usr/bin', '/sbin', '/usr/sbin', '/usr/local/bin', '/opt/homebrew/bin'}
VERSIONS = {'python', 'python3', 'node', 'npm', 'npx', 'brew', 'codex', 'claude'}
SAFE_FLAGS = {
    'uname': {'-a','-s','-r','-v','-m','-n','-p','-i','-o'},
    'hostname': set(), 'whoami': set(), 'id': {'-u','-g','-G','-n','-un','-gn'},
    'sw_vers': {'-productName','-productVersion','-buildVersion'},
    'uptime': {'-p','-s'}, 'df': {'-h','-k','-P','-T','-i'},
}
GIT_FLAGS = {
    'status': {'--short', '--branch', '--porcelain', '--porcelain=v1', '--porcelain=v2', '-s', '-b'},
    'diff': {'--stat', '--name-only', '--name-status', '--numstat', '--shortstat', '--cached', '--staged', '--check'},
    'log': {'--oneline', '--stat', '--name-only', '--no-decorate'},
    'show': {'--stat', '--name-only', '--name-status', '--oneline'},
    'rev-parse': {'--verify', '--show-toplevel', '--is-inside-work-tree', '--short'},
    'ls-files': {'--stage', '--cached', '--modified', '--deleted'},
    'ls-tree': {'--name-only', '--long', '-r', '-t'},
}


def read_allowed(argv):
    path, args = PurePosixPath(argv[0]), list(argv[1:])
    if '/' in argv[0] and (not path.is_absolute() or str(path.parent) not in SYSTEM_DIRS):
        return False
    name = path.name
    if name in SAFE_FLAGS:
        return all(arg in SAFE_FLAGS[name] for arg in args)
    if name in VERSIONS:
        return args in [['--version'], ['-V']]
    if name == 'git':
        if not args or args[0] not in GIT_FLAGS:
            return False
        for arg in args[1:]:
            if arg in GIT_FLAGS[args[0]] or arg == '--':
                continue
            if args[0] == 'log' and re.fullmatch(r'-[0-9]{1,3}', arg):
                continue
            if (arg.startswith(('-', '/')) or '..' in arg.split('/')
                    or not re.fullmatch(r'[A-Za-z0-9_./:@{}^~+-]+', arg)):
                return False
        return True
    if name == 'tailscale':
        return args in [['status'], ['status','--json'], ['serve','status'], ['serve','status','--json'], ['version']]
    if name == 'launchctl':
        return len(args) == 2 and args[0] == 'print' and args[1].startswith('gui/')
    return False


def write_allowed(argv):
    # Preserve the legacy tool name without bypassing project-profile authorization.
    return read_allowed(argv)
