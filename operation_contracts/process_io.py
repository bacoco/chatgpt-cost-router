"""Bounded POSIX subprocess capture for gateway protocol calls, not a shell API."""
import os
import selectors
import signal
import subprocess
import time
from .owned_process import status, signal_group


def run(argv, *, capture_output=True, text=False, timeout=30, check=False, env=None, cwd=None, limit=1048577):
    if not capture_output or check:
        raise ValueError("bounded runner requires captured output and explicit return-code handling")
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd=cwd, env=env, start_new_session=True)
    output = {"stdout": bytearray(), "stderr": bytearray()}
    selector = selectors.DefaultSelector()
    for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, name)
    deadline = time.monotonic() + timeout
    try:
        while selector.get_map() or status(process) is None:
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(argv, timeout, bytes(output["stdout"]), bytes(output["stderr"]))
            for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                room = max(0, limit - len(output[key.data]))
                output[key.data].extend(chunk[:room])
        values = [bytes(output[key]) for key in ("stdout", "stderr")]
        if text:
            values = [value.decode("utf-8", errors="replace") for value in values]
        signal_group(process)
        process.wait(timeout=5)
        return subprocess.CompletedProcess(argv, process.returncode, *values)
    finally:
        selector.close()
        signal_group(process)
        process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()
