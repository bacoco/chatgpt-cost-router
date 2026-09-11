"""Keep an owned child unreaped until its process group has been cleaned up.

No PID is accepted from a request or restored journal. WNOWAIT retains kernel
ownership of a dead leader, preventing PID reuse during process-group cleanup.
"""
import os
import signal

_WAITABLE = all(hasattr(os, name) for name in ("waitid", "WNOWAIT", "P_PID", "WEXITED", "WNOHANG"))


def status(process):
    if process.returncode is not None:
        return process.returncode
    if not _WAITABLE:
        return process.poll()
    observed = os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    if observed is None:
        return None
    return observed.si_status if observed.si_code == os.CLD_EXITED else -observed.si_status


def signal_group(process, sig=signal.SIGKILL):
    if process.returncode is not None:
        return False
    try:
        if _WAITABLE:
            # A ChildProcessError means ownership has been lost: do not signal.
            os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        elif process.poll() is not None:
            return False
        os.killpg(process.pid, sig)
        return True
    except (ProcessLookupError, ChildProcessError):
        return False
