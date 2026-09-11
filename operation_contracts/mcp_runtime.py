"""Optional official MCP SDK compatibility; no SDK import for ordinary A/B CLI use."""
import argparse


def new_server(name, instructions):
    try:
        from mcp.server import MCPServer
        return MCPServer(name,instructions=instructions)
    except ImportError:
        from mcp.server.fastmcp import FastMCP
        return FastMCP(name,instructions=instructions)


def annotations(read_only, destructive=False):
    from mcp.types import ToolAnnotations
    known = getattr(ToolAnnotations,"model_fields",getattr(ToolAnnotations,"__fields__",{}))
    snake = "read_only_hint" in known
    values = {"read_only_hint" if snake else "readOnlyHint":read_only,
              "destructive_hint" if snake else "destructiveHint":destructive,
              "open_world_hint" if snake else "openWorldHint":True}
    return ToolAnnotations(**values)


def serve(builder, argv=None, default_port=8812):
    parser = argparse.ArgumentParser(description="Private A/B MCP tool interface")
    parser.add_argument("--config",required=True)
    parser.add_argument("--transport",choices=("stdio","streamable-http"),default="stdio")
    parser.add_argument("--port",type=int,default=default_port)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("invalid loopback port")
    server = builder(args.config)
    if args.transport == "stdio":
        server.run(transport="stdio")
        return

    # FastMCP SDK versions differ: some expose mutable settings fields, while
    # others reject host/port assignment because Settings is a strict model.
    # Prefer configuring supported settings; otherwise pass transport options
    # directly to run().  In every case the HTTP listener remains loopback-only.
    settings = getattr(server, "settings", None)
    fields = getattr(type(settings), "model_fields", getattr(type(settings), "__fields__", {})) if settings is not None else {}
    if settings is not None and {"host", "port"}.issubset(fields):
        settings.host = "127.0.0.1"
        settings.port = args.port
        if "stateless_http" in fields:
            settings.stateless_http = True
        if "json_response" in fields:
            settings.json_response = True
        server.run(transport="streamable-http")
        return

    server.run(transport="streamable-http",host="127.0.0.1",port=args.port,
               streamable_http_path="/mcp",stateless_http=True,json_response=True)
