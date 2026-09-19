# Documentation index

Start with the repository [README](../README.md). Current source policy is defined by the repository README, `.chatgpt/CURRENT.md` and the current contracts. [Deployment status](DEPLOYMENT_STATUS.md) is the authority for the last observed installed-runtime evidence. Neither an older experiment log nor an old test count overrides current source policy.

| Current guide | Question answered |
| --- | --- |
| [Installation](INSTALLATION.md) | How do I install and deploy A, B or both? |
| [A/B usage](AB_USAGE.md) | How do I operate a workflow or machine job? |
| [Fleet relay](FLEET_OPERATOR_RELAY.md) | How does the native GitHub connector reach the fleet? |
| [Architecture](ARCHITECTURE.md) | Which module owns each responsibility and trust boundary? |
| [Validation](AB_VALIDATION.md) | What is tested and what needs live evidence? |
| [Roadmap](ROADMAP.md) | What remains? |
| [Current project state](../.chatgpt/CURRENT.md) | Where should the next Chat resume? |

## Historical material

T25–T38 documents, September 10 experiment logs, cost/quota studies, `BEGINNER_CLOUD_WORKFLOW.md`, `CLOUD_EXECUTION_LANE.md`, handoff/bootstrap kits and earlier validation snapshots record the project's evolution. They are retained for traceability, not recommended as the current installation path or proof of current availability. References there to Codex, Work, GitHub Actions or a paused deployment do not override the current A/B guides or the current no-Actions policy.

`SPEC.md` and routing schemas remain authoritative for the deterministic decision engine only. Optional mesh/provider-worker instructions are not prerequisites for ordinary A/B work. For WordPress operations use Cowboy, not WPVibe.
