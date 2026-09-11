"""B MCP interface with a configured principal, not a caller-supplied identity."""
from operation_contracts.mcp_runtime import new_server, annotations, serve
from .config import NodeConfig
from .service import Jobs


def build_server(path):
    server = new_server("Fleet Jobs",
        "Run and monitor project-bound ordinary processes. Callers never provide shell commands, "
        "working directories, credentials or a principal. Profiles and grants are operator-owned. "
        "A successful submit does not mean a task is complete. Inspect status, logs and result.")

    def service():
        return Jobs(NodeConfig.from_file(path))

    @server.tool(annotations=annotations(True))
    def fleet_node_health() -> dict:
        return service().health()

    @server.tool(annotations=annotations(True))
    def fleet_profiles(project_id: str) -> dict:
        return {"profiles":service().profiles(project_id)}

    @server.tool(annotations=annotations(False))
    def fleet_submit(request: dict, start: bool = False) -> dict:
        jobs = service()
        result = jobs.submit(request)
        return jobs.start(request["project_id"],result["run_id"]) if start else result

    @server.tool(annotations=annotations(False))
    def fleet_start(project_id: str, run_id: str) -> dict:
        return service().start(project_id,run_id)

    @server.tool(annotations=annotations(False,destructive=True))
    def fleet_cancel(project_id: str, run_id: str) -> dict:
        return service().cancel(project_id,run_id)

    @server.tool(annotations=annotations(True))
    def fleet_status(project_id: str, run_id: str) -> dict:
        return service().status(project_id,run_id)

    @server.tool(annotations=annotations(True))
    def fleet_logs(project_id: str, run_id: str, stream: str = "stdout", offset: int = 0, limit: int = 32768) -> dict:
        return service().logs(project_id,run_id,stream,offset,limit)

    @server.tool(annotations=annotations(True))
    def fleet_result(project_id: str, run_id: str) -> dict:
        return service().result(project_id,run_id)

    @server.tool(annotations=annotations(False))
    def fleet_reconcile(project_id: str, run_id: str) -> dict:
        return service().reconcile(project_id,run_id)

    @server.tool(annotations=annotations(True))
    def fleet_events(project_id: str, run_id: str, after: int = 0) -> dict:
        jobs = service()
        jobs.row(project_id,run_id)
        return {"events":jobs.journal.events(jobs.config.principal,project_id,run_id,after)}

    @server.tool(annotations=annotations(True))
    def fleet_artifact(project_id: str, run_id: str, name: str, offset: int = 0, limit: int = 65536) -> dict:
        return service().artifact(project_id, run_id, name, offset, limit)

    @server.tool(annotations=annotations(True))
    def fleet_jobs(project_id: str) -> dict:
        jobs = service()
        jobs.config.projects.project(jobs.config.principal, project_id)
        return {"jobs":[jobs.status(project_id, row["id"]) for row in
                        jobs.journal.list(jobs.config.principal, project_id, "process")]}

    return server


def main(argv=None):
    serve(build_server,argv=argv,default_port=8813)


if __name__ == "__main__":
    main()
