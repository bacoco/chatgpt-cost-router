# Fleet Operator command queue

This branch is an execution-authority queue for the supervised Fleet Operator relay.

Only versioned JSON jobs matching `schemas/fleet-operator-job.schema.json` belong under `.fleet/jobs/`.
The relay executes only the supported action set, through its local per-host allowlists, and writes results to `fleet/results/<job_id>` branches.

Do not put credentials, SSH keys, tokens, passwords, or arbitrary shell scripts here.
