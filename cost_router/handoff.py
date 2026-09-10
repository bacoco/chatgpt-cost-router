"""Handoff v2 invariants beyond structural JSON Schema validation."""
from .capabilities import action_set, capability_reason, check_manifest
from .validation import clock, digest, policy_config, timestamp, validate


def validate_handoff(packet, *, manifest=None, now=None, current_commit=None,
                     execution=False, policy=None, accepted_policy_identity=None):
    validate('handoff', packet)
    now = clock(now)
    if accepted_policy_identity is not None:
        if execution or packet['direction'] != 'return':
            raise ValueError('Accepted policy identity is only for reconciling a return')
        expected_policy = tuple(accepted_policy_identity)
    else:
        policy = policy_config(policy)
        expected_policy = (policy['version'], digest(policy))
    if (packet['policy_version'], packet['policy_sha256']) != expected_policy:
        raise ValueError('Policy changed; re-evaluate before accepting this handoff')
    if timestamp(packet['created_at']) > now:
        raise ValueError('Handoff is from the future')
    if packet['parent_handoff_id'] == packet['handoff_id']:
        raise ValueError('A handoff cannot be its own parent')
    if packet['recommended_surface'] in packet['forbidden_surfaces']:
        raise ValueError('Destination surface is forbidden')
    if not action_set(packet['actions']) <= action_set(packet['authorized_actions']):
        raise ValueError('Handoff action is not authorized')
    budget = packet['max_cost_units']
    if budget is not None and packet['estimated_cost_units'] > budget:
        raise ValueError('Handoff exceeds its cost budget')
    if current_commit is not None and packet['commit_sha'] != current_commit:
        raise ValueError('Repository state differs from the handoff commit')
    if execution and packet['repo'] is not None and current_commit is None:
        raise ValueError('Current repository commit must be checked before execution')
    evidence = {e['ref']: e for e in packet['evidence']}
    if len(evidence) != len(packet['evidence']):
        raise ValueError('Evidence references must be unique')
    for record in packet['evidence'] + packet['verification']:
        if timestamp(record['observed_at']) > now:
            raise ValueError('Evidence is from the future')
    criteria = {v['criterion']: v for v in packet['verification']}
    if len({t['command'] for t in packet['tests']}) != len(packet['tests']):
        raise ValueError('Test commands must be unique')
    if len(criteria) != len(packet['verification']):
        raise ValueError('Each success criterion can be verified only once')
    if not set(criteria) <= set(packet['success_criteria']):
        raise ValueError('Verification names an unknown success criterion')
    for check in packet['verification'] + packet['tests']:
        if check['result'] == 'pass':
            source = evidence.get(check['evidence_ref'])
            if source is None:
                raise ValueError('A passing check must reference supplied evidence')
            if check['commit_sha'] != packet['commit_sha'] or source['commit_sha'] != packet['commit_sha']:
                raise ValueError('Passing evidence belongs to a different commit')
    if packet['status'] == 'completed':
        if set(criteria) != set(packet['success_criteria']) or any(
                c['result'] != 'pass' for c in packet['verification'] + packet['tests']):
            raise ValueError('Completion requires all declared criteria and tests to pass')
    if execution:
        if manifest is None:
            raise ValueError('Destination capability preflight is required')
        check_manifest(manifest, now)
        for action in packet['actions']:
            reason = capability_reason(manifest, packet['recommended_surface'], packet['target_session_id'],
                                       action, now, policy['max_capability_age_seconds'])
            if reason:
                raise ValueError('Destination preflight: ' + reason)
    return packet


def make_return(delegation, *, result_surface, result_session_id, return_session_id,
                handoff_id, status, done, remaining, evidence, tests, verification,
                commit_sha, now=None):
    """Construct a return envelope. Validate it explicitly before publishing it."""
    import copy
    result = copy.deepcopy(delegation)
    result.update(direction='return', status=status, handoff_id=handoff_id,
                  parent_handoff_id=delegation['handoff_id'], created_at=clock(now).isoformat(),
                  from_surface=result_surface, from_session_id=result_session_id,
                  recommended_surface=delegation['from_surface'], target_session_id=return_session_id,
                  done=done, remaining=remaining, actions=[], estimated_cost_units=0,
                  evidence=evidence, tests=tests, verification=verification, commit_sha=commit_sha,
                  escalation_reason='Specialist result; destination must re-evaluate remaining work')
    return result
