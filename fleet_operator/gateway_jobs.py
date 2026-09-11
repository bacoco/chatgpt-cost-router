"""Typed private gateway operations, routed only to operator-enrolled runtimes."""
from operation_contracts.mcp_runtime import annotations
from .remote_jobs import call


def register(server, runner):
    @server.tool(annotations=annotations(True))
    def fleet_node_health(host: str) -> dict:
        return call(runner(), host, 'node_health', {})

    @server.tool(annotations=annotations(True))
    def fleet_profiles(host: str, project_id: str) -> dict:
        return call(runner(), host, 'process_profiles', {'project_id': project_id})

    @server.tool(annotations=annotations(False))
    def fleet_submit(host: str, request: dict, start: bool = False) -> dict:
        return call(runner(), host, 'process_submit', {'request': request, 'start': start})

    @server.tool(annotations=annotations(False))
    def fleet_start(host: str, project_id: str, run_id: str) -> dict:
        return call(runner(), host, 'process_start', {'project_id': project_id, 'run_id': run_id})

    @server.tool(annotations=annotations(False, destructive=True))
    def fleet_cancel(host: str, project_id: str, run_id: str) -> dict:
        return call(runner(), host, 'process_cancel', {'project_id': project_id, 'run_id': run_id})

    @server.tool(annotations=annotations(True))
    def fleet_status(host: str, project_id: str, run_id: str) -> dict:
        return call(runner(), host, 'process_status', {'project_id': project_id, 'run_id': run_id})

    @server.tool(annotations=annotations(True))
    def fleet_logs(host: str, project_id: str, run_id: str, stream: str = 'stdout', offset: int = 0, limit: int = 32768) -> dict:
        return call(runner(), host, 'process_logs', {'project_id': project_id, 'run_id': run_id,
                    'stream': stream, 'offset': offset, 'limit': limit})

    @server.tool(annotations=annotations(True))
    def fleet_result(host: str, project_id: str, run_id: str) -> dict:
        return call(runner(), host, 'process_result', {'project_id': project_id, 'run_id': run_id})

    @server.tool(annotations=annotations(True))
    def fleet_artifact(host: str, project_id: str, run_id: str, name: str, offset: int = 0, limit: int = 65536) -> dict:
        return call(runner(), host, 'process_artifact', {'project_id': project_id, 'run_id': run_id,
                    'name': name, 'offset': offset, 'limit': limit})

    @server.tool(annotations=annotations(False))
    def fleet_reconcile(host: str, project_id: str, run_id: str) -> dict:
        return call(runner(), host, 'process_reconcile', {'project_id': project_id, 'run_id': run_id})

    @server.tool(annotations=annotations(True))
    def fleet_events(host: str, project_id: str, run_id: str, after: int = 0) -> dict:
        return call(runner(), host, 'process_events', {'project_id': project_id, 'run_id': run_id, 'after': after})
