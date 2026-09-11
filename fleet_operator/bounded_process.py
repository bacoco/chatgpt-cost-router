"""Bounded foreground gateway transport, compatible with subprocess.run injection."""
import os
import selectors
import signal
import subprocess
import time
from .host_io import safe_environment
from .jobs.monitor import signal_child, exited


def run(argv, *, capture_output=True, text=False, timeout=60, check=False, max_bytes=1048576, **kwargs):
    kwargs["env"] = safe_environment(kwargs.get("env", os.environ))
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True, close_fds=True, **kwargs)
    selector = selectors.DefaultSelector()
    streams = {"stdout":bytearray(), "stderr":bytearray()}
    deadline, ended, timed_out = time.monotonic()+timeout, None, False
    try:
        for name in streams:
            stream = getattr(process, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map() or not exited(process):
            now = time.monotonic()
            if now >= deadline:
                timed_out = True
                signal_child(process, signal.SIGKILL)
                break
            for key, _ in selector.select(min(0.1, max(0, deadline-now))):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                room = max(0, max_bytes+1-len(streams[key.data]))
                streams[key.data].extend(chunk[:room])
            if exited(process):
                ended = ended or now
                if now-ended > 1:
                    timed_out = True
                    break
        signal_child(process, signal.SIGKILL)
        process.wait(timeout=5)
    finally:
        selector.close()
        for name in streams:
            getattr(process, name).close()
        if process.returncode is None:
            signal_child(process, signal.SIGKILL)
            process.wait(timeout=5)
    output = {k:(bytes(v).decode(errors="replace") if text else bytes(v)) for k,v in streams.items()}
    if timed_out:
        raise subprocess.TimeoutExpired(argv, timeout, output=output["stdout"], stderr=output["stderr"])
    if check and process.returncode:
        raise subprocess.CalledProcessError(process.returncode, argv, output=output["stdout"], stderr=output["stderr"])
    return subprocess.CompletedProcess(argv, process.returncode, **output)
