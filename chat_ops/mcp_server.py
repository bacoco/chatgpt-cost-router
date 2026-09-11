"""Private A MCP app. The native Chat client retains its existing connectors."""
import uuid
from typing import Any
from operation_contracts.common import identifier
from operation_contracts.mcp_runtime import new_server, annotations, serve
from .config import configured


def build_server(path):
    server = new_server("Chat-first Operations",
        "Operate across authorized Gmail, GitHub, Cowboy and other connectors from Chat. "
        "Use current-context discovery evidence, explicit write approval and actual read-back. "
        "next returns a single native tool instruction; it does not call another model. "
        "Never call record with invented tool output. Recorded native evidence is caller-observed.")

    def engine(session_id=None):
        e = configured(path)[0]
        if session_id is not None:
            e.session = identifier(session_id,"session")
        return e

    @server.tool(annotations=annotations(False))
    def chat_begin_session() -> dict:
        return {"session_id":uuid.uuid4().hex,"surface":engine().surface,
                "instruction":"Keep this identifier in this conversation only; observe its actual tools afresh."}

    @server.tool(annotations=annotations(True))
    def chat_projects() -> dict:
        e = engine()
        return {"projects":e.projects.list(e.principal)}

    @server.tool(annotations=annotations(True))
    def chat_action_catalog() -> dict:
        return {"actions":engine().catalog.list()}

    @server.tool(annotations=annotations(False))
    def chat_observe_capability(project_id: str, resource: str, action: str, evidence: dict, session_id: str) -> dict:
        e = engine(session_id)
        e.projects.project(e.principal,project_id)
        e.capabilities.observe(e.principal,project_id,resource,action,e.surface,e.session,evidence)
        return {"recorded":True,"source":"caller-observed-discovery"}

    @server.tool(annotations=annotations(False))
    def chat_submit(workflow: dict) -> dict:
        return engine().submit(workflow)

    @server.tool(annotations=annotations(False))
    def chat_approve(project_id: str, run_id: str, step_id: str) -> dict:
        return engine().approve(project_id,run_id,step_id)

    @server.tool(annotations=annotations(False))
    def chat_next(project_id: str, run_id: str, session_id: str) -> dict:
        return engine(session_id).next(project_id,run_id)

    @server.tool(annotations=annotations(False))
    def chat_record(project_id: str, run_id: str, step_id: str, token: str, output: Any, session_id: str, error: bool = False) -> dict:
        return engine(session_id).record(project_id,run_id,step_id,token,output,error=error)

    @server.tool(annotations=annotations(False))
    def chat_reconcile(project_id: str, run_id: str, step_id: str, session_id: str) -> dict:
        return engine(session_id).reconcile(project_id,run_id,step_id)

    @server.tool(annotations=annotations(True))
    def chat_status(project_id: str, run_id: str) -> dict:
        return engine().status(project_id,run_id)

    @server.tool(annotations=annotations(True))
    def chat_result(project_id: str, run_id: str) -> dict:
        e = engine()
        return {**e.status(project_id,run_id),"outputs":e.outputs(e.row(project_id,run_id))}

    @server.tool(annotations=annotations(False))
    def chat_cancel(project_id: str, run_id: str) -> dict:
        return engine().cancel(project_id, run_id)

    @server.tool(annotations=annotations(True))
    def chat_events(project_id: str, run_id: str, after: int = 0) -> dict:
        return engine().events(project_id, run_id, after)

    @server.tool(annotations=annotations(True))
    def chat_list(project_id: str) -> dict:
        return engine().list(project_id)

    return server


if __name__ == "__main__":
    serve(build_server,default_port=8812)
