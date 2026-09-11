# Strategic split: Chat orchestration and Fleet Operator

Date: 2026-09-11.
Status: documentation-only strategic pause. Owner scope correction: A covers complete operations through Chat and all authorized apps/connectors, not only issues or coding deliverables.
Repository reviewed: `bacoco/chatgpt-cost-router`, `main` at `4772e01b2bf13ccf4e07af4f6a232b0e8223070d`.

## Decision and scope

There are two independent needs, not one mandatory Chat-to-Codex cluster pipeline.

**A — Chat-first Operations:** accomplish as much real work as possible entirely from the normal Chat surface and its authorized plugins/connectors, using the capability already included in the user's subscription. Chat reasons, reads, writes, sends, publishes, coordinates workflows and verifies outcomes. Gmail, GitHub, WordPress/Cowboy and the other existing or future authorized apps are first-class capabilities. An issue is one possible action, not A's product definition or sole acceptance criterion. Avoid switching to Work or invoking Codex/Claude/model APIs when Chat plus tools can complete the request.

**B — Fleet Operator:** access machines, submit bounded processes, manage their lifecycle, monitor progress and resources, and retrieve results. Placement across machines is optional; reliable access and process supervision come first. Models, GPUs and subscription workers are optional execution capabilities.

A must work without B for connector-only work. B must work without Chat through a CLI, API or other authorized client. Separate logical products now; separate repositories only after their contracts and packaging are agreed. Keep the current repository and historical receipts intact during this design phase.

## A: full Chat-only operations, tools and acceptance

The fundamental requirement is operational, not merely informational: the user stays in Chat to complete authorized work through available tools. Do not reduce A to researching code, creating an issue, preparing a handoff, or asking another agent to do the actual work. Direct connector actions are the primary execution lane; B is optional when a machine/process capability is needed.

Illustrative scope (not a claim that every action is already verified on every surface):

| Connected resource | Intended work from Chat |
| --- | --- |
| Gmail | Search and read messages, prepare/read drafts, send authorized messages, and manage mail using actions actually exposed. |
| GitHub | Read/analyze repositories, create or modify files, commit changes, manage branches/issues/PRs and authorized merges, and verify exact results. |
| WordPress via Cowboy | Read content, prepare or update pages/articles, publish when authorized, and verify the resulting site. Do not substitute WPVibe. |
| Other authorized plugins/connectors | Use their verified document, calendar, contact, publishing or other capabilities without making a second agent mandatory. |
| Several connected systems | Complete a user-authorized workflow across apps, carrying the correct project/context and verifying each external effect. |

Chat owns intent interpretation, context gathering, planning, tool selection, authorized invocation, result verification, failure reporting and project/account separation. Publication, sending, editing and other state changes are part of A, subject to the user's scope and required confirmations; A is not read-only by definition.

Serena is an optional MCP tool for targeted code context and, if appropriately configured, editing. It is neither A's central component nor a prerequisite for using Gmail, GitHub or other apps. Avoid redundant tools and select the cheapest verified path that achieves the actual requested outcome.

The economic requirement is **Chat-only first**: no paid model API, extra Codex/Claude inference, or switch to Work by default. A connector call or an ordinary remote process must not silently hide another model call. This is the owner's routing objective, not a claim that all providers, transports, compute or Chat usage are unlimited or unmetered. Do not restart the deliberately stopped quota-burn experiment.

Maintain an action-level capability inventory for each distinct surface: ChatGPT.com Chat, Codex Mac Chat, Work, CLI and Scheduled Tasks are not interchangeable. Record app name, authenticated scope/project, action, visible/invocable/executed/effect-verified state, evidence/date and known or unknown usage class. Reuse existing receipts rather than erasing yesterday's plugin tests or unnecessarily repeating them. For example, historical Gmail search/read/draft/send evidence belongs to Codex Mac Chat with built-in Gmail; it does not automatically validate Gmail Developer MCP in web Chat or Scheduled Tasks. A prior blocked context is not a universal current product ban either.

Acceptance must cover representative completed outcomes, not one GitHub issue:

- Mail: search/read the permitted messages and produce the requested verified draft or authorized send, with deduplication and no unnecessary model delegation.
- GitHub: perform a requested repository operation and read back the exact file/commit/PR state; an issue is only one variant.
- Publication/other apps: perform the requested authorized change through the appropriate connector and verify the external result.
- Multi-app/multiproject: complete a scoped workflow without mixing recipients, accounts, projects or permissions and without automatically invoking a coding worker.

These are acceptance categories for the design, not new executions. During the pause, do not send mail, publish pages, create test issues or dispatch machine jobs just to demonstrate the scope. Already verified actions keep their scoped evidence. Unavailable operations are reported explicitly, with an alternative or a proposed delegation rather than silently switching modes.

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
Chat + all authorized apps [A] -> Gmail / GitHub / Cowboy / other systems
          |
          | optional project-scoped execution request
          v
Fleet service [B] <-------------- CLI / API / other clients
          |
          +-- ordinary processes and supervised services
          +-- optional Codex / Claude worker adapters
          +-- optional PAIR -> local inference engines
```

Do not use a shared mutable "active project" for concurrent chats. Each request binds an explicit project or user-authorized task context; repository identity and SHA apply when the operation concerns code, not to every email or document. Proposed minimum contract:

- Request: requester identity, project/task context, operation/profile, inputs, allowed hosts/resources, deadline and idempotency key; repository owner/name and immutable base SHA where applicable.
- Optional model use: provider/account reference, allowed usage class and budget; no token, password or private key in the request.
- Return: run ID, lifecycle state, resolved node/workspace and software version, exit status, bounded diagnostics, artifact references and verification evidence.

Project rules may restrict execution but cannot grant permissions that the service administrator did not authorize. Repository permissions, OS identity and provider account identity are separate. Aggregate provider usage per account across all projects/machines rather than counting each worker as a separate quota. Measure monetary/API spend, model usage and compute resources separately; use unknown rather than invented provider counters.

## Existing components: proposed ownership

| Existing capability | Owner after logical split |
| --- | --- |
| Complete Chat-first operations through Gmail, GitHub, Cowboy and other authorized apps; single-app and cross-app workflows | A |
| Optional Serena code retrieval | A, hosted on a verified checkout |
| Host access and bounded execution via Fleet Operator | B |
| Node registration, heartbeat, supervision and process monitoring | B |
| Codex/Claude account workers and health/quarantine | B adapters; A decides whether delegation is useful |
| Local inference routed by PAIR | Optional B adapter |
| GitHub relay | Transitional B transport/fallback, not a required A workflow |
| Project/run contract and evidence format | Shared, versioned, minimal |

## Next decisions, not an execution order

Preserve the owner's broad A scope and the independent B scope. Consolidate existing per-surface plugin/action evidence and map the remaining gaps; do not replace A's scope with a single issue-producing test. Plan representative mail, repository, publication and cross-app outcomes for A, and a bounded process-lifecycle outcome for B. Evaluate Serena only where code context/editing adds value; evaluate PAIR separately for local inference. Reuse historical evidence and compare existing tools before extending the custom runtime. No new execution is ordered by this review.

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
