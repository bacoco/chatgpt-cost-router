"""Best-effort local observations. Unknown measurements are never reported as zero."""
import os
import shutil
import time
from pathlib import Path


def process_metrics(pid):
    out = {"observed_at":time.time(), "cpu_seconds":None, "rss_bytes":None,
           "scope":"direct foreground process, not a container or descendant aggregate"}
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        out["cpu_seconds"] = (int(fields[11])+int(fields[12])) / os.sysconf("SC_CLK_TCK")
        out["rss_bytes"] = int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        pass
    return out


def node_health(service):
    disk = shutil.disk_usage(service.config.state_dir)
    try:
        load = list(os.getloadavg())
    except OSError:
        load = None
    with service.journal.transaction() as db:
        counts = {row[0]:row[1] for row in db.execute(
            "SELECT state,COUNT(*) FROM operations WHERE kind='process' AND principal=? GROUP BY state",
            (service.config.principal,))}
    return {"ok":True,"node_id":service.config.node_id,"observed_at":time.time(),
            "runtime_revision":service.config.document.get("runtime_revision"),
            "policy_revision":service.config.revision,"model_runtime_required":False,
            "cpu_count":os.cpu_count(),"load_average":load,"disk_free_bytes":disk.free,
            "max_concurrency":service.config.max_concurrency,"jobs_by_state":counts}
