# MCP Plan

## machines-mcp
DGX Spark, Mac Studio, RTX 4090.
Tools: status, run_inference, run_benchmark, submit_job, job_status, fetch_result.

## media-mcp
ComfyUI/Sparky.
Tools: list_workflows, get_workflow, run_workflow, job_status, get_outputs.

## vps-mcp
Safe VPS operations.
Tools: status, docker_ps, service_logs, disk_usage, safe_exec, deploy_known_project.

## llm-router-mcp
Specialist delegation.
Tools: codex_task, claude_review, local_llm_task, compare_solutions.

Calling Codex/Claude through MCP does not make their underlying usage free; savings come from using them only for the specialist slice.

## universal-api-mcp
Authenticated APIs with allowlists, typed schemas, server-side secrets, rate limits and audit logs.
