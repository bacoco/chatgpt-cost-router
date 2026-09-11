"""Real loopback HTTP protocol exchanges; no live provider or SDK required."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from operation_contracts.common import ContractError
from chat_ops.mcp_transport import Client, MCPTransport


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.calls, self.mode = [], "json"
        fixture = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                fixture.calls.append(body)
                method = body["method"]
                if fixture.mode == "redirect":
                    self.send_response(302)
                    self.send_header("Location", "/other")
                    self.end_headers()
                    return
                if method == "notifications/initialized":
                    self.send_response(202)
                    self.end_headers()
                    return
                if method == "initialize":
                    result = {"protocolVersion":"2025-11-25", "capabilities":{"tools":{}},
                              "serverInfo":{"name":"local-fixture", "version":"1"}}
                elif method == "tools/list":
                    tool = {"name":"read_item", "inputSchema":{"type":"object"},
                            "annotations":{"readOnlyHint":fixture.mode != "unsafe"}}
                    result = {"tools":[tool, tool] if fixture.mode == "duplicate" else [tool]}
                else:
                    result = {"structuredContent":{"item":42}}
                    if fixture.mode == "tool-error":
                        result["isError"] = True
                response = {"jsonrpc":"2.0", "id":body["id"], "result":result}
                if fixture.mode == "bad-id":
                    response["id"] = True
                raw = json.dumps(response).encode()
                if fixture.mode == "oversize":
                    raw += b" " * 1_048_576
                self.send_response(200)
                self.send_header("MCP-Session-Id", "local-fixture-session")
                self.send_header("Content-Type", "text/event-stream" if fixture.mode == "sse" else "application/json")
                self.end_headers()
                if fixture.mode == "sse":
                    raw = b'data: {"jsonrpc":"2.0","method":"notifications/progress"}\n\n' + b"data: " + raw + b"\n\n"
                self.wfile.write(raw)
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.config = {"url":f"http://127.0.0.1:{self.http.server_port}/mcp", "account_ref":"local",
                       "actions":{"github.read":"read_item"}, "connector":"GitHub"}
        self.invocation = {"connector":"GitHub", "resource":"repo", "account_ref":"local",
                           "action":"github.read", "tool_name":"read_item", "arguments":{}, "read_only":True}

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)

    def test_real_json_discovery_and_call(self):
        self.assertEqual(Client(self.config).call(self.invocation), {"item":42})
        self.assertEqual([c["method"] for c in self.calls],
                         ["initialize", "notifications/initialized", "tools/list", "tools/call"])

    def test_real_sse_skips_notification_and_correlates_response(self):
        self.mode = "sse"
        self.assertEqual(Client(self.config).call(self.invocation), {"item":42})

    def test_protocol_discovery_and_error_fail_closed(self):
        for mode in ("duplicate", "unsafe", "bad-id", "oversize", "redirect", "tool-error"):
            with self.subTest(mode=mode):
                self.mode = mode
                with self.assertRaises(ContractError):
                    Client(self.config).call(self.invocation)
        self.assertEqual(sum(c["method"] == "tools/call" for c in self.calls), 1)

    def test_wrong_account_cannot_call_remote_tool(self):
        with self.assertRaises(ContractError):
            Client(self.config).call({**self.invocation, "account_ref":"other"})
        self.assertEqual(self.calls, [])

    def test_multi_account_and_resource_binding(self):
        other = {**self.config, "account_ref":"other"}
        transport = MCPTransport({"one":self.config,"two":other})
        self.assertEqual(transport.invoke(self.invocation), {"item":42})
        with self.assertRaises(ContractError):
            MCPTransport({"one":self.config,"two":self.config})

    def test_unsafe_endpoints_are_rejected(self):
        for url in ("http://example.com/mcp", "https://user:secret@example.com/mcp",
                    "https://example.com/mcp?secret=x", "https:///mcp"):
            with self.subTest(url=url), self.assertRaises(ContractError):
                Client({**self.config,"url":url})

    def test_disjoint_resources_can_share_connector_and_account(self):
        config = {**self.config,"resource":"repo"}
        other = {**self.config,"resource":"other-repo"}
        self.assertEqual(MCPTransport({"one":config,"two":other}).invoke(self.invocation),{"item":42})
