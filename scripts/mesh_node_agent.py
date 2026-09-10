#!/usr/bin/env python3
"""Register/heartbeat a local worker node into a private mesh control plane."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cost_router.mesh import MeshError, build_local_registration, validate_endpoint


def tailscale_self():
    raw = subprocess.check_output(["tailscale", "status", "--json"], text=True)
    data = json.loads(raw)
    self_node = data.get("Self", {})
    dns = (self_node.get("DNSName") or "").rstrip(".")
    host = self_node.get("HostName") or dns.split(".")[0]
    if not dns.endswith(".ts.net"):
        raise MeshError("Tailscale Self.DNSName is unavailable; MagicDNS/tailnet DNS name required")
    safe_id = "".join(c.lower() if c.isalnum() or c in "._-" else "-" for c in host).strip("-")
    return safe_id[:64], dns


def post_json(url, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv=None):
    p = argparse.ArgumentParser(description="Heartbeat a worker node into the private mesh")
    p.add_argument("--control-url", required=True)
    p.add_argument("--node-id")
    p.add_argument("--node-url", help="Override this node's Tailscale Serve URL")
    p.add_argument("--worker-port", type=int, default=8443)
    p.add_argument("--registry", default="examples/workers.json")
    p.add_argument("--budget-state")
    p.add_argument("--workers", default=os.environ.get("COST_ROUTER_REMOTE_WORKERS", "openai-B"))
    p.add_argument("--location", choices=["local", "remote", "cloud"], default="remote")
    p.add_argument("--interval", type=int, default=30)
    p.add_argument("--codex-bin", default="codex")
    p.add_argument("--once", action="store_true")
    args = p.parse_args(argv)

    control = validate_endpoint(args.control_url)
    if args.interval < 15:
        p.error("--interval must be >= 15 seconds")
    node_id, dns = tailscale_self()
    node_id = args.node_id or node_id
    endpoint = validate_endpoint(args.node_url or f"https://{dns}:{args.worker_port}")
    workers = {x.strip() for x in args.workers.split(",") if x.strip()}
    if not workers:
        p.error("at least one --workers alias is required")

    while True:
        try:
            payload = build_local_registration(
                node_id=node_id,
                endpoint=endpoint,
                registry_path=args.registry,
                allowed_workers=workers,
                budget_state_path=args.budget_state,
                location=args.location,
                codex_bin=args.codex_bin,
            )
            result = post_json(control + "/v1/mesh/register", payload)
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({"error": str(exc), "node_id": node_id}), file=sys.stderr, flush=True)
            if args.once:
                return 2
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
