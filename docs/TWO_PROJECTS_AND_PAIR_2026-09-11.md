# Strategic split: Chat orchestration and Fleet Operator

Date: 2026-09-11.
Status: design proposal following the owner's correction; no deployment or new test.
Repository reviewed: `bacoco/chatgpt-cost-router`, `main` at `4772e01b2bf13ccf4e07af4f6a232b0e8223070d`.

## Decision and scope

There are two independent needs, not one mandatory Chat-to-Codex cluster pipeline.

**A — Chat Orchestration:** maximize useful reasoning, research and authorized actions from the Chat surface already included in the user's plan. Code analysis, issues and PRs are important examples, not the whole product. Avoid an additional Codex/Claude/API invocation when Chat plus tools can accomplish the objective.

**B — Fleet Operator:** access machines, submit bounded processes, manage their lifecycle, monitor progress and resources, and retrieve results. Placement across machines is optional; reliable access and process supervision come first. Models, GPUs and subscription workers are optional execution capabilities.

A must work without B for connector-only work. B must work without Chat through a CLI, API or other authorized client. Separate logical products now; separate repositories only after their contracts and packaging are agreed. Keep the current repository and historical receipts intact during this design phase.

## A: scope, tools and acceptance

A owns project selection, evidence collection, reasoning, task/specification drafting, review, authorized GitHub or other connector actions, and the decision to request execution.

Use existing GitHub MCP actions for repository/issue/PR operations. Serena is an optional MCP code-understanding tool: symbol lookup, references and targeted retrieval can provide better evidence before Chat writes an issue or proposes a change. Serena is not required for every repository and is not the GitHub publishing authority. Initially prefer a read-oriented Serena configuration with a verified checkout/SHA; disable overlapping execution tools if B owns that responsibility.

The proposed acceptance case is a useful project deliverable: inspect a real problem, identify code locations and supporting sources, publish an issue or prepare a reviewed change, then read it back. Do not require an extra model, a GPU, or a fleet deployment merely to create this deliverable. Do not create an empty PR as a substitute for a specification.

Chat web, desktop Chat, desktop Work and CLI remain distinct capability/usage contexts. Preserve observed evidence per surface; do not infer universal availability or billing from an app name. This split does not restart the stopped quota-burn experiment. "Chat first" is an economic preference, not a claim of unlimited zero-cost automated model access.

## B: scope, execution and monitoring

B owns enrollment, machine identity, authorization, capability inventory, runtime isolation, job submission, supervision, cancellation, logs/results and health/resource monitoring. Placement and load balancing are secondary capabilities, not admission requirements for a new node.

A process can be a test/build, script, data/image pipeline, long-running service, authorized coding-agent task, or local inference. CPU-only machines remain useful. Running a process does not inherently require a model invocation.

Expose structured operations such as inventory, submit, status, logs, cancel and result through a stable service; MCP is an interface to that service. SSH/Tailscale, local execution and OS supervision are implementation choices below it. A browser or CLI can use B without Chat. An already-submitted process can continue while Chat is inactive; that does not imply continued LLM reasoning.

Target monitoring distinguishes host reachable, supervisor loaded, process running, process making progress, job complete, and result verified. Use stable run identifiers, bounded output, timeouts and durable outcomes. An uncertain result must not be blindly rerun. Monitor in the runtime rather than repeatedly invoking an LLM to poll.

Target enrollment is install a pinned package, authorize/pair the node, register its capabilities, assign allowed projects/resource limits, and execute a bounded diagnostic. A node can serve several projects without installing a separate orchestrator per project. Credentials stay on the authorized machine or in an appropriate secret store. OS isolation, not a worktree or risk flag alone, contains jobs.

## PAIR: identified project and actual fit

The corrected reference is **NVIDIA Personal AI Router (PAIR)**, repository `NVIDIA/Personal-AI-Router` [1]. The comparison below is documentation-based; PAIR has not been installed or tested on this fleet by this review.

PAIR is a local inference router with Ollama-compatible and OpenAI-compatible endpoints. It discovers paired nodes and their engines/models, routes each independent request to an eligible node, and exposes workload/resource visibility. It routes a complete request to one machine: no pooled VRAM, no model sharding, and no migration of an in-flight request [1, 2].

Its installation/pairing model, stable node identities, desktop/terminal interfaces, engine management and jobs view are relevant references for B's enrollment and monitoring experience. PAIR nodes are peers rather than dependents of a mandatory primary controller [2].

PAIR does not provide the general contract we need for arbitrary scripts, builds, application deployments, GitHub project isolation, or Codex/Claude subscription-account budgets. It can be an optional local-inference backend within B, not a replacement for B or for A. Its JSON-RPC control layer and HTTP inference layer are not a pre-existing ChatGPT fleet MCP app [3].

Current routing gates candidates on engine/model availability and ranks with pending work and a coarse GPU-pressure signal. The architecture documentation says GPU model, available VRAM, latency, request cost and model warmness are not used for full capacity-aware placement. Do not describe this as an optimal heterogeneous hardware scheduler [3]. The known-issues page still describes job-count-only scheduling, so pin a release and verify behavior before adoption rather than treating every document as synchronized [4].

PAIR is LAN-first. Pairing uses a short-lived PIN to establish certificate trust; inter-node mTLS has a limited scope, and some metadata is not covered. The local inference endpoints are loopback-only. Do not expose these publicly or assume cross-home/VPN discovery, multi-user isolation or durable authorization is solved by pairing alone [5].

NVIDIA lists RTX 20-series and later, DGX Spark/GB10 and Mac M4-or-later configurations on the product page. The repository describes broader OS/architecture support and delegates actual inference compatibility to engines/models. The user's two M1 Ultra Mac Studios are therefore **not validated by this review**, not automatically unsupported. Qualify them separately; DGX Spark and RTX 4090 fit the named hardware families, but actual fleet execution remains untested [1, 6].

The known-issues page also distinguishes restart-on-exit from detection of an unresponsive live service. Keep our progress/stall-monitoring requirement instead of assuming PAIR's restart behavior covers it [4].

## Relationship and shared contract

```text
Chat + authorized apps [A] -----> GitHub / other systems
          |
          | optional project-scoped execution request
          v
Fleet service [B] <-------------- CLI / API / other clients
          |
          +-- ordinary processes and supervised services
          +-- optional Codex / Claude worker adapters
          +-- optional PAIR -> local inference engines
```

Do not use a shared mutable "active project" for concurrent chats. Each request binds an explicit project and run context. Proposed minimum contract:

- Request: requester identity, project ID, repository owner/name and immutable base SHA, operation/profile, inputs, allowed hosts/resources, deadline and idempotency key.
- Optional model use: provider/account reference, allowed usage class and budget; no token, password or private key in the request.
- Return: run ID, lifecycle state, resolved node/workspace and software version, exit status, bounded diagnostics, artifact references and verification evidence.

Project rules may restrict execution but cannot grant permissions that the service administrator did not authorize. Repository permissions, OS identity and provider account identity are separate. Aggregate provider usage per account across all projects/machines rather than counting each worker as a separate quota. Measure monetary/API spend, model usage and compute resources separately; use unknown rather than invented provider counters.

## Existing components: proposed ownership

| Existing capability | Owner after logical split |
| --- | --- |
| Cloud-first workflow, GitHub context, specifications, issues/PRs | A |
| Optional Serena code retrieval | A, hosted on a verified checkout |
| Host access and bounded execution via Fleet Operator | B |
| Node registration, heartbeat, supervision and process monitoring | B |
| Codex/Claude account workers and health/quarantine | B adapters; A decides whether delegation is useful |
| Local inference routed by PAIR | Optional B adapter |
| GitHub relay | Transitional B transport/fallback, not a required A workflow |
| Project/run contract and evidence format | Shared, versioned, minimal |

## Next decisions, not an execution order

Approve the A/B boundary, choose one independent acceptance case for each, and compare the missing B functions with existing process-management tools before extending the custom runtime. Evaluate Serena for a real information-to-issue task; evaluate PAIR separately only for a genuine local-inference need. Neither requires restarting every historical smoke test.

T01-T37 remain historical proofs with their recorded limitations. T38/write-lane hardening remains unfinished and paused; the broad write-lane risk is not resolved by this design document. Do not install packages, change services, invoke paid APIs, submit fleet jobs or physically split repositories during the pause.

## Primary sources reviewed

[1] https://github.com/NVIDIA/Personal-AI-Router
[2] https://github.com/NVIDIA/Personal-AI-Router/blob/main/docs/overview.mdx
[3] https://github.com/NVIDIA/Personal-AI-Router/blob/main/docs/architecture.mdx
[4] https://github.com/NVIDIA/Personal-AI-Router/blob/main/docs/known-issues.mdx
[5] https://github.com/NVIDIA/Personal-AI-Router/blob/main/SECURITY.md
[6] https://www.nvidia.com/en-eu/ai-on-rtx/personal-ai-router/
[7] https://github.com/oraios/serena
[8] https://developers.openai.com/api/docs/guides/developer-mode
[9] https://help.openai.com/en/articles/12584461

Serena's retrieval/configuration statements above derive from [7]. OpenAI's developer guide and Help Center do not currently present an identical eligibility matrix; preserve that uncertainty and validate tools in the actual chosen client/workspace, rather than claiming a universal Pro write ban or universal write access [8, 9]. No direct MCP connection was validated in this review.
