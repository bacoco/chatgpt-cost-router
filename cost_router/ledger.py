"""Durable local operation claims. Adapters must claim before any external effect.

No network calls occur here. Exactly-once external effects require provider-side
idempotency/reconciliation; uncertain outcomes are never automatically retried.
"""
import json
import sqlite3

from .handoff import validate_handoff
from .validation import clock, digest

TRANSITIONS = {'recommended': {'accepted', 'cancelled'}, 'accepted': {'running', 'cancelled'},
               'running': {'completed', 'failed', 'uncertain'},
               'uncertain': {'completed', 'failed'},
               'completed': set(), 'failed': set(), 'cancelled': set()}


class Ledger:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA journal_mode=WAL')
        self.connection.execute('PRAGMA synchronous=FULL')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS operations (
            operation_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
            packet TEXT NOT NULL, state TEXT NOT NULL, revision INTEGER NOT NULL,
            evidence_ref TEXT, result TEXT, updated_at TEXT NOT NULL)''')

    def close(self):
        self.connection.close()

    def get(self, operation_id):
        record = self.connection.execute('SELECT * FROM operations WHERE operation_id=?',
                                         (operation_id,)).fetchone()
        if record is None:
            raise KeyError(operation_id)
        return dict(record)

    def register(self, packet, *, now=None):
        now = clock(now)
        validate_handoff(packet, now=now)
        if packet['direction'] != 'delegation':
            raise ValueError('Only delegation envelopes register an operation')
        fingerprint = digest(packet)
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            self.connection.execute('''INSERT OR IGNORE INTO operations
                (operation_id,task_id,fingerprint,packet,state,revision,updated_at)
                VALUES (?,?,?,?,?,?,?)''', (packet['operation_id'], packet['task_id'], fingerprint,
                json.dumps(packet, sort_keys=True), 'recommended', 0, now.isoformat()))
            record = self.get(packet['operation_id'])
            if record['fingerprint'] != fingerprint:
                raise ValueError('Idempotency key reused with a different immutable request')
            self.connection.execute('COMMIT')
            return record
        except BaseException:
            self.connection.execute('ROLLBACK')
            raise

    def transition(self, operation_id, target, *, expected_revision, evidence_ref,
                   manifest=None, now=None, current_commit=None, result=None):
        if target not in TRANSITIONS or type(expected_revision) is not int or expected_revision < 0:
            raise ValueError('Invalid transition request')
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ValueError('Transition evidence is required')
        now = clock(now)
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            record = self.get(operation_id)
            # A repeated transition never issues a fresh execution grant.
            if record['revision'] != expected_revision:
                raise ValueError('Stale revision; inspect state before acting')
            if target not in TRANSITIONS[record['state']]:
                raise ValueError(f"Invalid transition: {record['state']} -> {target}")
            packet = json.loads(record['packet'])
            if target in ('accepted', 'running'):
                validate_handoff(packet, manifest=manifest, now=now, current_commit=current_commit, execution=True)
            if target == 'completed':
                if result is None:
                    raise ValueError('Completed state requires a verified return envelope')
                # Reconcile already-authorized work against its accepted policy.
                # A policy update must block new claims, not erase valid results.
                validate_handoff(result, now=now, current_commit=current_commit,
                                 accepted_policy_identity=(packet['policy_version'], packet['policy_sha256']))
                if result['direction'] != 'return' or result['status'] != 'completed':
                    raise ValueError('Completion requires a completed return envelope')
                if packet['repo'] is not None and current_commit is None:
                    raise ValueError('Verify the resulting repository commit')
                for field in ('task_id', 'operation_id', 'goal', 'success_criteria', 'constraints',
                              'authorized_actions', 'authorization_ref', 'forbidden_surfaces',
                              'max_cost_units', 'repo', 'branch', 'policy_sha256', 'policy_version'):
                    if result[field] != packet[field]:
                        raise ValueError('Return envelope changed ' + field)
                if result['parent_handoff_id'] != packet['handoff_id']:
                    raise ValueError('Return envelope belongs to another handoff')
                if {t['command'] for t in result['tests']} != {t['command'] for t in packet['tests']}:
                    raise ValueError('Return envelope changed the required tests')
                if (result['from_surface'], result['from_session_id']) != (
                        packet['recommended_surface'], packet['target_session_id']):
                    raise ValueError('Return envelope came from another execution context')
            elif result is not None:
                raise ValueError('Only completed transitions accept a result envelope')
            self.connection.execute('''UPDATE operations SET state=?, revision=revision+1,
                evidence_ref=?, result=?, updated_at=? WHERE operation_id=?''',
                (target, evidence_ref, json.dumps(result) if result is not None else None,
                 now.isoformat(), operation_id))
            updated = self.get(operation_id)
            self.connection.execute('COMMIT')
            return updated
        except BaseException:
            self.connection.execute('ROLLBACK')
            raise
