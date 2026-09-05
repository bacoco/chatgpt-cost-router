"""Action/resource/session-scoped observations, never inferred from a tool name."""
from .validation import clock, timestamp, validate


def action_set(actions):
    return {(a['action'], a['resource']) for a in actions}


def check_manifest(manifest, now):
    validate('capabilities', manifest)
    now = clock(now)
    captured = timestamp(manifest['captured_at'])
    if captured > now:
        raise ValueError('Capability manifest is from the future')
    for observation in manifest['observations']:
        observed = timestamp(observation['observed_at'])
        if observed > captured:
            raise ValueError('Observation is newer than its manifest')
        expires = observation['expires_at']
        if expires is not None and timestamp(expires) <= observed:
            raise ValueError('Capability expiry must follow observation time')


def capability_reason(manifest, surface, session_id, action, now, max_age):
    matches = [o for o in manifest['observations']
               if (o['surface'], o['session_id'], o['action'], o['resource']) ==
               (surface, session_id, action['action'], action['resource'])]
    if not matches:
        return 'capability-not-verified'
    newest = max(timestamp(o['observed_at']) for o in matches)
    latest = [o for o in matches if timestamp(o['observed_at']) == newest]
    # Conflicting observations at the same instant fail closed. A newer denial
    # overrides an older successful observation, regardless of input order.
    if any(o['status'] != 'verified' for o in latest):
        return 'capability-unavailable-or-unknown'
    if (now - newest).total_seconds() > max_age:
        return 'capability-stale'
    if any(timestamp(o['expires_at']) <= now for o in latest):
        return 'capability-expired'
    return None
