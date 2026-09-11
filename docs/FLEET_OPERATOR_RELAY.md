# Fleet access from Chat through GitHub

This compatibility path uses the authorized GitHub connector and a user-level relay, not a new model call, Codex task or GitHub Actions runner. Consult [deployment status](DEPLOYMENT_STATUS.md) to see whether the new relay is live.

```text
Chat + authorized GitHub connector
    -> fleet/ab-commands : .fleet/jobs/<job-id>.json
    -> separate A/B relay -> enrolled node / named profile
    -> fleet/ab-results/<job-id> : .fleet/results/<job-id>.json
```

The older `fleet/commands` and `fleet/results/` branches belong to the retained historical relay. **Never submit the same operation to both queues.** Source belongs on `main`; queue write access is execution authority.

## Job contract

Use a unique 8–80 character safe ID, a configured host alias and a future Unix expiry no more than 24 hours away. Filename and job ID must match. This example deliberately has an expired timestamp until prepared for a real execution:

```json
{
  "version": 1,
  "job_id": "job-owner-health-unique",
  "host": "macbook",
  "action": "node_health",
  "args": {},
  "expires_at_unix": 0
}
```

For `process_submit`, arguments contain a `request` and optional boolean `start`. The request contains version, project_id, node_id, profile, inputs, idempotency_key and deadline. The node checks its own private project/profile policy.

Typed actions include node_health, process_profiles, process_list, process_submit, process_start, process_status, process_cancel, process_logs, process_result, process_events and process_reconcile. `fleet_operator/remote_jobs.py` and `relay_service.py` define exact arguments. Raw mutation, including unrestricted exec_write or Git pull, is refused by the new guarded policy; use approved profiles.

## Completion and private results

A commit proves submission, not execution. Read the exact result branch. An ACCEPTED/running reply is not completion; use its run ID with a new bounded status/result read and inspect the terminal state and receipt. Retrieve logs/events independently.

Artifact bytes use the private CLI/MCP transport, not GitHub. They are returned as data_base64 with full-file sha256, verified, offsets and EOF. Assemble and verify the file locally. Do not publish private bytes to make retrieval easier.

## Failure and replay

The relay claims durably, saves the private result and uses a publication outbox. A publication failure retries delivery of that saved result without executing the operation again, even if the original command is no longer listed. An interrupted claim without a completion receipt remains uncertain. Conflicting reuse of a job ID is rejected; differing existing result evidence is not overwritten.

Credentials and raw SSH destinations stay on the gateway. Restrict command-branch writes as carefully as deployment access. An issue, PR or untrusted document does not grant execution authority by itself.
