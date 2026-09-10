#!/usr/bin/env python3
"""Loopback-only mesh control plane intended for Tailscale Serve."""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cost_router.mesh import MeshError, NodeRegistry, dispatch_mesh, parse_json_body, policy_from_env, tailscale_identity


class Handler(BaseHTTPRequestHandler):
    server_version = "cost-router-mesh/0.1"

    def log_message(self, fmt, *args):
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
        return tailscale_identity(self.headers, self.server.mesh_policy)

    def _body(self):
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise MeshError("Content-Length is required")
        length = int(raw_length)
        if length < 0 or length > self.server.mesh_policy.max_body_bytes:
            raise MeshError("request body is too large")
        return parse_json_body(self.rfile.read(length), self.server.mesh_policy)

    def do_GET(self):
        try:
            self._identity()
            if self.path == "/v1/mesh/health":
                return self._json(200, {"ok": True, "transport": "tailscale-serve", "authenticated": True})
            if self.path == "/v1/mesh/nodes":
                return self._json(200, {"nodes": self.server.registry.live_nodes()})
            if self.path == "/v1/mesh/workers":
                return self._json(200, {"workers": self.server.registry.workers()})
            return self._json(404, {"error": "not found"})
        except (MeshError, OSError, ValueError) as exc:
            return self._json(403, {"error": str(exc)})

    def do_POST(self):
        try:
            user = self._identity()
            payload = self._body()
            if self.path == "/v1/mesh/register":
                node = self.server.registry.register(payload, user)
                return self._json(200, {"registered": True, "node": node})
            if self.path == "/v1/mesh/run":
                result = dispatch_mesh(self.server.registry, payload)
                return self._json(200, result)
            return self._json(404, {"error": "not found"})
        except (MeshError, OSError, ValueError) as exc:
            return self._json(400, {"error": str(exc)})


def main(argv=None):
    p = argparse.ArgumentParser(description="Loopback-only worker mesh control plane")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8790)
    p.add_argument("--state", default="~/.local/state/chatgpt-cost-router/mesh/nodes.json")
    args = p.parse_args(argv)
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        p.error("mesh control plane must listen on loopback only; put Tailscale Serve in front")
    try:
        policy = policy_from_env()
        registry = NodeRegistry(args.state, policy)
    except (MeshError, OSError, ValueError) as exc:
        p.error(str(exc))
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.mesh_policy = policy
    server.registry = registry
    print(json.dumps({"listening": f"http://{args.host}:{args.port}", "ttl_seconds": policy.ttl_seconds}))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
