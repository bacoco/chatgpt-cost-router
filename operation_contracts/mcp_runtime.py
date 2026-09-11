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
    settings = getattr(server, "settings", None)
    known = getattr(type(settings), "model_fields", getattr(type(settings), "__fields__", {}))
    if "port" in known or hasattr(settings, "port"):
        server.settings.host = "127.0.0.1"
        server.settings.port = args.port
        server.settings.stateless_http = True
        server.settings.json_response = True
        server.run(transport="streamable-http")
    else:
        server.run(transport="streamable-http",host="127.0.0.1",port=args.port,
                   streamable_http_path="/mcp",stateless_http=True,json_response=True)
