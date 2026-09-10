#!/usr/bin/env python3
"""Tiny client for the private worker mesh control plane."""
import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def call(base, path, payload=None):
    url = base.rstrip("/") + path
    if urlparse(url).scheme != "https":
        raise ValueError("mesh URL must use https")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST" if data else "GET",
                  headers={"Content-Type": "application/json"} if data else {})
    with urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv=None):
    p = argparse.ArgumentParser(description="Call a private Tailscale worker mesh")
    p.add_argument("--url", required=True)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("nodes")
    sub.add_parser("workers")
    run = sub.add_parser("run")
    run.add_argument("--worker", default="auto")
    run.add_argument("--prompt", required=True)
    args = p.parse_args(argv)
    paths = {"health": "/v1/mesh/health", "nodes": "/v1/mesh/nodes", "workers": "/v1/mesh/workers"}
    try:
        if args.command == "run":
            result = call(args.url, "/v1/mesh/run", {"worker": args.worker, "prompt": args.prompt})
        else:
            result = call(args.url, paths[args.command])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, HTTPError, URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
