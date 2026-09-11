"""Bounded MCP Streamable HTTP client. No model API or browser-session scraping.

Supports JSON replies and correlated JSON-RPC replies in an SSE response stream.
Endpoints, account bindings, tool maps and optional headers are operator-owned.
"""
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from operation_contracts.common import ContractError, fields, loads


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ContractError("MCP redirects are refused")


class Client:
    def __init__(self, config, *, opener=None):
        fields(config,("url","account_ref","actions"),("headers_file",))
        parsed = urlparse(config["url"])
        loopback = parsed.hostname in {"127.0.0.1","localhost","::1"}
        if not parsed.hostname:
            raise ContractError("MCP endpoint requires a hostname")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ContractError("MCP URL cannot embed credentials/query/fragment")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
            raise ContractError("MCP requires HTTPS except on loopback")
        if not isinstance(config["actions"],dict):
            raise ContractError("MCP tool map must be operator configured")
        self.config, self.opener = config, opener or build_opener(NoRedirect())
        self.headers = {}
        if "headers_file" in config:
            path = Path(config["headers_file"]).expanduser()
            if path.stat().st_mode & 0o077 or path.is_symlink():
                raise ContractError("MCP header file must be private and not a symlink")
            data = loads(path.read_text())
            if not isinstance(data,dict) or any(not isinstance(k,str) or not isinstance(v,str) or "\n" in k+v or "\r" in k+v for k,v in data.items()):
                raise ContractError("invalid local MCP headers")
            if any(k.lower() not in {"authorization","x-api-key"} for k in data):
                raise ContractError("unsupported authentication header")
            self.headers = data
        self.session, self.protocol, self.sequence = None, "2025-11-25", 0
        self.initialized = False

    def _post(self, method, params, notify=False):
        self.sequence += 1
        request_id = self.sequence
        body = {"jsonrpc":"2.0","method":method,"params":params}
        if not notify:
            body["id"] = request_id
        headers = {**self.headers,"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
        if self.initialized:
            headers["MCP-Protocol-Version"] = self.protocol
        if self.session:
            headers["MCP-Session-Id"] = self.session
        request = Request(self.config["url"],data=json.dumps(body).encode(),headers=headers,method="POST")
        deadline = time.monotonic() + 30
        with self.opener.open(request,timeout=30) as response:
            self.session = response.headers.get("MCP-Session-Id",self.session)
            if notify:
                return None
            if "text/event-stream" in response.headers.get("Content-Type",""):
                total, data_lines = 0, []
                while True:
                    if time.monotonic() >= deadline:
                        raise ContractError("MCP response exceeded its wall-clock deadline")
                    line = response.readline(65537)
                    total += len(line)
                    if total > 1_048_576 or not line or time.monotonic() > deadline:
                        raise ContractError("no bounded correlated MCP response")
                    if line.startswith(b"data:"):
                        data_lines.append(line[5:].strip())
                    elif not line.strip() and data_lines:
                        value = loads(b"\n".join(data_lines).decode())
                        data_lines = []
                        if isinstance(value,dict) and value.get("id") == request_id:
                            break
            else:
                value = loads(response.read(1_048_577).decode())
        if not isinstance(value,dict) or value.get("jsonrpc") != "2.0" or value.get("id") != request_id:
            raise ContractError("uncorrelated MCP reply")
        if "error" in value or "result" not in value:
            raise ContractError("MCP tool returned a protocol error")
        return value["result"]

    def initialize(self):
        if self.initialized:
            return
        result = self._post("initialize",{"protocolVersion":self.protocol,"capabilities":{},
                                         "clientInfo":{"name":"chat-first-operations","version":"1.0.0"}})
        if result.get("protocolVersion") not in {"2025-11-25","2025-06-18","2025-03-26"}:
            raise ContractError("MCP protocol version not supported by this adapter")
        self.protocol = result["protocolVersion"]
        self.initialized = True
        self._post("notifications/initialized",{},notify=True)

    def tools(self):
        self.initialize()
        tools, params = {}, {}
        for _ in range(20):
            result = self._post("tools/list",params)
            for tool in result.get("tools",[]):
                tools[tool["name"]] = tool
            if not result.get("nextCursor"):
                return tools
            params = {"cursor":result["nextCursor"]}
        raise ContractError("MCP tool discovery pagination limit")

    def call(self, invocation):
        if invocation["account_ref"] != self.config["account_ref"] or self.config["actions"].get(invocation["action"]) != invocation["tool_name"]:
            raise ContractError("tool/account differs from local MCP action binding")
        tool = self.tools().get(invocation["tool_name"])
        if tool is None:
            raise ContractError("bound tool is not currently exposed")
        annotations = tool.get("annotations",{})
        readonly = annotations.get("readOnlyHint",annotations.get("read_only_hint",False))
        if invocation["read_only"] and readonly is not True:
            raise ContractError("read action is not backed by a read-only tool")
        from jsonschema import Draft202012Validator
        from referencing import Registry
        schema = tool.get("inputSchema")
        if not isinstance(schema, dict):
            raise ContractError("bound tool has no input schema")
        try:
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema, registry=Registry()).validate(invocation["arguments"])
        except Exception as exc:
            raise ContractError("arguments do not satisfy the discovered tool schema") from exc
        result = self._post("tools/call",{"name":invocation["tool_name"],"arguments":invocation["arguments"]})
        if result.get("isError") or result.get("is_error"):
            raise ContractError("MCP invocation returned an error; outcome requires reconciliation")
        if "structured_content" in result:
            return result["structured_content"]
        if "structuredContent" in result:
            return result["structuredContent"]
        content = result.get("content",[])
        if len(content) == 1 and content[0].get("type") == "text":
            try:
                return loads(content[0]["text"])
            except ContractError:
                return {"text":content[0]["text"]}
        return {"content":content}


class MCPTransport:
    def __init__(self, endpoints):
        if not isinstance(endpoints, dict):
            raise ContractError("MCP endpoints must be an operator-owned mapping")
        self.clients = {}
        for connector, bindings in endpoints.items():
            configs = bindings if isinstance(bindings, list) else [bindings]
            for config in configs:
                if not isinstance(config, dict):
                    raise ContractError("MCP endpoint binding must be an object")
                family = config.get("connector", connector)
                client = Client({key:val for key,val in config.items() if key != "connector"})
                key = (family, config["account_ref"])
                if key in self.clients:
                    raise ContractError("duplicate connector/account MCP binding")
                self.clients[key] = client

    def invoke(self, invocation):
        key = (invocation["connector"], invocation["account_ref"])
        if key not in self.clients:
            raise ContractError("no direct MCP adapter for this account; use the native Chat tool driver")
        return self.clients[key].call(invocation)
