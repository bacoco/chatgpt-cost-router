"""Deterministic feasibility filtering followed by marginal cost comparison."""
import copy

from .capabilities import action_set, capability_reason, check_manifest
from .validation import clock, digest, policy_config, validate


def transfers(plan, task):
    # Every change of execution context has a cost, including a new session on
    # the same surface. Scheduler steps are independent triggers, not a hop.
    previous = (task['current_surface'], task['current_session_id'])
    count = 0
    for step in plan['steps']:
        if step['role'] == 'executor':
            current = (step['surface'], step['session_id'])
            count += current != previous
            previous = current
    return count


def plan_cost(plan):
    return sum(sum(s['cost'].values()) for s in plan['steps'])


def plan_rejections(plan, request, policy, now):
    task, manifest = request['task'], request['capabilities']
    reasons = []
    required, authorized = action_set(task['required_actions']), action_set(task['authorized_actions'])
    planned = action_set(a for step in plan['steps'] for a in step['actions'])
    if planned != required:
        reasons.append('actions-do-not-match-task')
    if not planned <= authorized:
        reasons.append('action-not-authorized')
    if len({s['step_id'] for s in plan['steps']}) != len(plan['steps']):
        reasons.append('duplicate-step-id')
    flattened = [(a['action'], a['resource']) for s in plan['steps'] for a in s['actions']]
    if len(flattened) != len(set(flattened)):
        reasons.append('duplicate-planned-action')
    scheduler_count = sum(s['role'] == 'scheduler' for s in plan['steps'])
    if scheduler_count != int(task['recurring']):
        reasons.append('recurrence-not-covered')
    if scheduler_count and plan['steps'][0]['role'] != 'scheduler':
        reasons.append('scheduler-must-precede-execution')
    if any((a['action'] == 'schedule.create') != (s['role'] == 'scheduler')
           for s in plan['steps'] for a in s['actions']):
        reasons.append('scheduler-action-role-mismatch')
    if not any(s['role'] == 'executor' for s in plan['steps']):
        reasons.append('executor-missing')
    if plan['cost_unit'] != policy['cost_unit']:
        reasons.append('incomparable-cost-unit')
    if any(s['cost'] is None for s in plan['steps']):
        reasons.append('cost-unknown')
    elif task['max_cost_units'] is not None and plan_cost(plan) > task['max_cost_units']:
        reasons.append('cost-budget-exceeded')
    duration = sum(s['duration_seconds'] for s in plan['steps'])
    if task['max_duration_seconds'] is not None and duration > task['max_duration_seconds']:
        reasons.append('duration-budget-exceeded')
    if transfers(plan, task) and task['transfer_count'] + transfers(plan, task) > policy['max_transfers']:
        reasons.append('transfer-limit-exceeded')
    for step in plan['steps']:
        if step['surface'] in task['forbidden_surfaces']:
            reasons.append('surface-forbidden')
        for action in step['actions']:
            reason = capability_reason(manifest, step['surface'], step['session_id'], action,
                                       now, policy['max_capability_age_seconds'])
            if reason:
                reasons.append(reason)
    return sorted(set(reasons))


def route(request, *, now=None, policy=None):
    """Return a recommendation only. Input observations must be trusted evidence."""
    validate('request', request)
    now, policy = clock(now), policy_config(policy)
    check_manifest(request['capabilities'], now)
    task = request['task']
    ids = [p['plan_id'] for p in request['candidates']]
    if len(ids) != len(set(ids)):
        raise ValueError('Candidate plan IDs must be unique')
    eligible, rejected = [], []
    for candidate in request['candidates']:
        reasons = plan_rejections(candidate, request, policy, now)
        if reasons:
            rejected.append({'plan_id': candidate['plan_id'], 'reasons': reasons})
        else:
            eligible.append(candidate)
    result = {'version': 1, 'task_id': task['task_id'], 'evaluated_at': now.isoformat(),
              'policy_version': policy['version'], 'policy_sha256': digest(policy),
              'status': 'blocked', 'reason': 'no-feasible-plan', 'route': None,
              'selected_plan_id': None, 'cost_unit': policy['cost_unit'],
              'estimated_cost_units': None, 'plan': None, 'rejected': rejected}
    if eligible:
        order = {s: i for i, s in enumerate(policy['tie_break_order'])}
        key = lambda p: (plan_cost(p), transfers(p, task),
                         tuple(order[s['surface']] for s in p['steps']), p['plan_id'])
        selected = min(eligible, key=key)
        current = [p for p in eligible if transfers(p, task) == 0]
        reason = 'lowest-estimated-total-cost'
        if transfers(selected, task) and current:
            stay = min(current, key=key)
            if plan_cost(stay) - plan_cost(selected) <= policy['min_transfer_savings_units']:
                selected, reason = stay, 'transfer-saving-insufficient'
        surfaces = {s['surface'] for s in selected['steps']}
        result.update(status='routed', reason=reason,
                      route=next(iter(surfaces)) if len(surfaces) == 1 else 'HYBRID',
                      selected_plan_id=selected['plan_id'], estimated_cost_units=plan_cost(selected),
                      plan=copy.deepcopy(selected))
    return validate('decision', result)
