#!/usr/bin/env python3
"""Loopback-only HTTP facade for the worker broker, intended for Tailscale Serve."""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fleet_operator.workers.remote_worker import (
    RemoteWorkerError,
    dispatch_remote,
    list_remote_workers,
    parse_request_body,
    policy_from_env,
    tailscale_identity,
)
from fleet_operator.workers.workers import WorkerError


class Handler(BaseHTTPRequestHandler):
    server_version = "cost-router-remote/0.1"

    def log_message(self, fmt, *args):
        # Keep standard access logging but do not log request bodies/prompts.
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), fmt % args))

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _identity(self):
        return tailscale_identity(self.headers, self.server.remote_policy)

    def do_GET(self):
        try:
            identity = self._identity()
            if self.path == "/v1/health":
                return self._json(200, {"ok": True, "transport": "tailscale-serve", "user": identity})
            if self.path == "/v1/workers":
                workers = list_remote_workers(
                    policy=self.server.remote_policy,
                    registry_path=self.server.registry_path,
                    codex_bin=self.server.codex_bin,
                )
                return self._json(200, {"workers": workers})
            return self._json(404, {"error": "not found"})
        except (RemoteWorkerError, WorkerError) as exc:
            return self._json(403, {"error": str(exc)})

    def do_POST(self):
        if self.path != "/v1/run":
            return self._json(404, {"error": "not found"})
        try:
            self._identity()
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise RemoteWorkerError("Content-Length is required")
            length = int(raw_length)
            if length < 0 or length > self.server.remote_policy.max_body_bytes:
                raise RemoteWorkerError("request body is too large")
            payload = parse_request_body(self.rfile.read(length), self.server.remote_policy)
            result = dispatch_remote(
                payload,
                policy=self.server.remote_policy,
                registry_path=self.server.registry_path,
                budget_state_path=self.server.budget_state_path,
                codex_bin=self.server.codex_bin,
            )
            return self._json(200 if result["exit_code"] == 0 else 502, result)
        except (RemoteWorkerError, WorkerError, OSError, ValueError) as exc:
            return self._json(400, {"error": str(exc)})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Loopback-only Tailscale remote worker endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--registry", default="examples/workers.json")
    parser.add_argument("--budget-state", default=None)
    parser.add_argument("--codex-bin", default="codex")
    args = parser.parse_args(argv)
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        parser.error("remote worker backend must listen on loopback only; put Tailscale Serve in front")

    try:
        policy = policy_from_env()
        policy.workspace_root.expanduser().mkdir(parents=True, exist_ok=True, mode=0o700)
    except (RemoteWorkerError, OSError) as exc:
        parser.error(str(exc))

    server = HTTPServer((args.host, args.port), Handler)
    server.remote_policy = policy
    server.registry_path = args.registry
    server.budget_state_path = args.budget_state
    server.codex_bin = args.codex_bin
    print(json.dumps({
        "listening": f"http://{args.host}:{args.port}",
        "transport": "tailscale-serve-required",
        "allowed_workers": sorted(policy.allowed_workers),
        "allowed_user_count": len(policy.allowed_users),
    }))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
