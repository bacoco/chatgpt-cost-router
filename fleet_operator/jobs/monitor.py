"""Bounded logs, progress and cancellation of the child owned by this supervisor."""
import json
import os
import selectors
import signal
import time
from operation_contracts.common import number


def _progress(line):
    if not line.startswith(b"FLEET_PROGRESS "):
        return None
    try:
        data = json.loads(line[15:])
        if not isinstance(data,dict) or set(data) - {"current", "total", "message"}:
            return None
        number(data["total"], 1, 1e12)
        number(data["current"], 0, data["total"])
        if not isinstance(data.get("message", ""),str) or len(data.get("message", "")) > 256:
            return None
        return data
    except (KeyError, ValueError, TypeError):
        return None


def signal_child(process, sig):
    if process.poll() is None:
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass


def _heartbeat(journal, row, token, data):
    with journal.transaction() as db:
        current = journal.decode(db.execute("SELECT * FROM operations WHERE id=?", (row["id"],)).fetchone())
        if current["state"] not in {"RUNNING", "CANCELLING"} or current["data"].get("token") != token:
            return
        current["data"].update(data)
        db.execute("UPDATE operations SET data=?,updated=? WHERE id=?",
                   (json.dumps(current["data"], allow_nan=False), time.time(), row["id"]))


def monitor(process, journal, row, token, root, profile):
    selector, files = selectors.DefaultSelector(), {}
    sizes = {"stdout":0, "stderr":0}
    for name, stream in (("stdout",process.stdout), ("stderr",process.stderr)):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, name)
        files[name] = (root / (name+".log")).open("xb")
    until = min(row["request"]["deadline"], time.time()+profile["timeout_seconds"])
    stopped, stop_at, last_pulse, last_output = None, 0, 0, None
    progress, buffer, truncated, exit_at = None, b"", False, None
    try:
        while selector.get_map() or process.poll() is None:
            now = time.time()
            current = journal.get(row["principal"], row["project"], row["id"])
            if current["data"].get("token") != token or current["state"] == "UNCERTAIN":
                stopped = stopped or "UNCERTAIN"
            if stopped is None and current["state"] == "CANCELLING":
                stopped = "CANCELLED"
            if stopped is None and now >= until:
                stopped = "TIMED_OUT"
            if stopped and not stop_at:
                signal_child(process, signal.SIGTERM)
                stop_at = now
            if stop_at and now-stop_at >= 2:
                signal_child(process, signal.SIGKILL)
            for key, _ in selector.select(0.1):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                name = key.data
                room = max(0, profile["max_output_bytes"]-sizes[name])
                files[name].write(chunk[:room])
                files[name].flush()
                sizes[name] += min(len(chunk), room)
                truncated |= len(chunk) > room
                last_output = now
                if name == "stdout":
                    buffer = (buffer+chunk)[-16384:]
                    lines = buffer.split(b"\n")
                    buffer = lines.pop()
                    for line in lines:
                        progress = _progress(line) or progress
            if now-last_pulse >= 1:
                _heartbeat(journal,row,token,{"heartbeat":now,"last_output_at":last_output,"progress":progress})
                last_pulse = now
            if process.poll() is not None:
                exit_at = now if exit_at is None else exit_at
                if now-exit_at > 2 and selector.get_map():
                    stopped = "UNCERTAIN"
                    break
        process.wait(timeout=5)
        return {"state":stopped or ("SUCCEEDED" if process.returncode == 0 else "FAILED"),
                "exit_code":process.returncode, "output_truncated":truncated,
                "progress":progress, "last_output_at":last_output}
    finally:
        selector.close()
        for file in files.values():
            file.close()
        for stream in (process.stdout, process.stderr):
            if not stream.closed:
                stream.close()
        if process.poll() is None:
            signal_child(process, signal.SIGKILL)
            process.wait(timeout=5)
