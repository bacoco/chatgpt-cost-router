"""Synthetic, scoped observations for deterministic tests; never live evidence."""
import copy

from cost_router.validation import digest, policy_config

NOW = '2026-09-05T00:30:00Z'
OBSERVED = '2026-09-05T00:00:00Z'
EXPIRES = '2026-09-05T01:00:00Z'
SHA = 'a' * 40


def action(name='github.read', resource='bacoco/example'):
    return {'action': name, 'resource': resource}


def step(surface='CHAT', actions=None, cost=100, role='executor', session=None):
    return {'step_id': surface.lower() + '-' + role, 'role': role, 'surface': surface,
            'session_id': session or surface.lower() + '-1',
            'actions': copy.deepcopy(actions or [action()]),
            'cost': None if cost is None else {'execution': cost, 'transfer': 0, 'retry': 0, 'ci': 0},
            'duration_seconds': 10, 'delivery': 'manual', 'adapter_ref': None}


def plan(name, *steps):
    return {'plan_id': name, 'cost_unit': 'usd_micro', 'steps': list(steps)}


def request(plans=None, *, actions=None, recurring=False, current='CHAT'):
    plans = copy.deepcopy(plans or [plan('chat', step())])
    actions = copy.deepcopy(actions or [action()])
    observations = []
    seen = set()
    for p in plans:
        for s in p['steps']:
            for a in s['actions']:
                key = (s['surface'], s['session_id'], a['action'], a['resource'])
                if key not in seen:
                    seen.add(key)
                    observations.append({'surface': s['surface'], 'session_id': s['session_id'], **a,
                        'status': 'verified', 'observed_at': OBSERVED, 'expires_at': EXPIRES,
                        'evidence_ref': 'fixture:synthetic-permission-probe-' + str(len(seen)),
                        'method': 'permission-check'})
    return {'version': 1, 'task': {'task_id': 'fixture-task', 'goal': 'Complete the synthetic fixture',
            'current_surface': current, 'current_session_id': current.lower() + '-1',
            'required_actions': actions, 'authorized_actions': copy.deepcopy(actions),
            'authorization_ref': 'fixture:explicit-user-authorization', 'forbidden_surfaces': [],
            'recurring': recurring, 'max_cost_units': None, 'max_duration_seconds': None, 'transfer_count': 0},
            'capabilities': {'version': 1, 'manifest_id': 'fixture-manifest', 'captured_at': OBSERVED,
                             'observations': observations}, 'candidates': plans}


def handoff():
    policy = policy_config()
    return {'version': 2, 'task_id': 'fixture-task', 'handoff_id': 'handoff-1',
            'operation_id': 'fixture-task-review-1', 'parent_handoff_id': None,
            'direction': 'delegation', 'status': 'ready', 'from_surface': 'CHAT', 'from_session_id': 'chat-1',
            'recommended_surface': 'CODEX', 'target_session_id': 'codex-1',
            'policy_version': policy['version'], 'policy_sha256': digest(policy), 'created_at': OBSERVED,
            'goal': 'Review the pinned example repository', 'done': ['Repository identified'],
            'remaining': ['Review the requested file'], 'repo': 'bacoco/example', 'branch': 'main',
            'commit_sha': SHA, 'files': ['src/example.py'], 'constraints': ['Read-only review'],
            'actions': [action()], 'authorized_actions': [action()],
            'authorization_ref': 'fixture:explicit-user-authorization', 'forbidden_surfaces': [],
            'cost_unit': 'usd_micro', 'estimated_cost_units': 100, 'max_cost_units': 200,
            'evidence': [], 'tests': [], 'success_criteria': ['Requested review complete'],
            'verification': [], 'escalation_reason': 'Destination has the required scoped repository capability',
            'return_to_chat_when': ['Re-evaluate destination access and remaining work'], 'extensions': {}}


def destination_manifest():
    return request([plan('codex', step('CODEX'))])['capabilities']
