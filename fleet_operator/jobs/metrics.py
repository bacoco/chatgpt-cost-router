"""Best-effort direct-child measurements, never guessed progress or fleet totals."""
import os
from pathlib import Path
import subprocess
import sys
import time


def sample(process):
    if process.returncode is not None:
        return {"available": False, "reason": "child exited"}
    try:
        if sys.platform.startswith("linux"):
            fields = Path(f"/proc/{process.pid}/stat").read_text().rsplit(")", 1)[1].split()
            cpu = (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")
            rss = int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
        elif sys.platform == "darwin":
            proc = subprocess.run(["/bin/ps", "-p", str(process.pid), "-o", "rss=", "-o", "time="],
                                  capture_output=True, text=True, timeout=1, check=True)
            memory, stamp = proc.stdout.split()
            parts = stamp.replace("-", ":").split(":")
            cpu = sum(float(value) * factor for value, factor in zip(reversed(parts), (1, 60, 3600, 86400)))
            rss = int(memory) * 1024
        else:
            return {"available": False, "reason": "platform has no sampler"}
        return {"available": True, "scope": "owned-direct-child", "rss_bytes": rss,
                "cpu_seconds": cpu, "measured_at": time.time()}
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return {"available": False, "reason": "measurement unavailable"}
