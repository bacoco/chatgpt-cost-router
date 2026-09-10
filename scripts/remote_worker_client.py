#!/usr/bin/env python3
"""Tiny client for a Tailscale Serve remote worker endpoint."""
import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def request(base, path, payload=None):
    url = base.rstrip("/") + path
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("remote worker URL must use https")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    with urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv=None):
    p = argparse.ArgumentParser(description="Call a private Tailscale remote Codex worker")
    p.add_argument("--url", required=True, help="Tailscale Serve HTTPS base URL")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("workers")
    run = sub.add_parser("run")
    run.add_argument("--worker", default="auto")
    run.add_argument("--prompt", required=True)
    args = p.parse_args(argv)
    try:
        if args.command == "health":
            result = request(args.url, "/v1/health")
        elif args.command == "workers":
            result = request(args.url, "/v1/workers")
        else:
            result = request(args.url, "/v1/run", {"worker": args.worker, "prompt": args.prompt})
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, HTTPError, URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
