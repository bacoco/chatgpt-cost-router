# Remote operator goal

Objective: after a one-time host installation, ChatGPT can request bounded diagnostics/tests on registered machines through the GitHub repository as a durable command bus, and read machine-produced receipts back from GitHub without asking the user to copy/paste terminal commands.

Security boundary:
- no arbitrary shell from repository jobs;
- only versioned, allowlisted actions implemented by the local operator agent;
- jobs are read only from the default branch of this repository;
- each job is addressed to an explicit node id and unique id;
- replay is rejected through a local completed-job ledger;
- results are sanitized and written to a dedicated results path;
- paid API/model calls are never implicit;
- destructive actions require an action-specific explicit flag in the job schema;
- operator runs as the logged-in user via LaunchAgent, never root.

Planned initial actions: status, repository test suite, mesh status, LaunchAgent status, controlled service restart, Tailscale status, and bounded worker smoke. The last action must require explicit model-use authorization in the job.
