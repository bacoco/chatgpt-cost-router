# ChatGPT project workspace

Project: `bacoco/chatgpt-cost-router`

Purpose: validate and develop the ChatGPT Cost & Capability Router and its cloud-first project workflow.

Canonical source kit: this repository itself.
Source-kit revision used for this bootstrap: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`.

Durable-state rule: GitHub is the source of truth. Chat and scheduler-local files are workspaces only.

Primary execution order:
1. normal ChatGPT;
2. ChatGPT + authorized Developer MCPs;
3. Scheduled Task only for automatic start/repetition or project-workspace entry;
4. ChatGPT local Python/shell verification when sufficient;
5. GitHub Actions only when runner quota/capacity is available;
6. Codex only after a concrete capability boundary;
7. paid API only by explicit exception.

Relevant Developer MCPs in the reference profile:
- `GitHub — bacoco TEST`
- `GitHub Actions — bacoco TEST` (optional; runner capacity is a separate gate)

Do not silently broaden repository, merge, release, deployment, secret, or paid-API permissions.