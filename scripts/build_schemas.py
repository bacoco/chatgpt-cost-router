"""Generate the published contracts from shared, reviewable definitions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URI = 'https://cost-router.invalid/schemas/'
SURFACES = ['CHAT', 'SCHEDULED_CHAT', 'LOCAL_TOOL', 'CODEX', 'WORK', 'EXTERNAL_API']


def obj(properties, required=None, **extra):
    return dict(type='object', additionalProperties=False, properties=properties,
                required=list(properties) if required is None else required, **extra)


def arr(items, minimum=0, **extra):
    return dict(type='array', items=items, minItems=minimum, **extra)


def ref(name):
    return {'$ref': 'common.schema.json#/$defs/' + name}


def nullable(schema):
    return {'anyOf': [schema, {'type': 'null'}]}


text = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
number = {'type': 'integer', 'minimum': 0}
stamp = {'type': 'string', 'format': 'date-time'}
surface = {'enum': SURFACES}
action = obj({'action': text, 'resource': text})
actions = arr(ref('action'), uniqueItems=True)
texts = arr(ref('text'), uniqueItems=True)
cost = obj({'execution': number, 'transfer': number, 'retry': number, 'ci': number})
observation = obj({'surface': surface, 'session_id': text, 'action': text,
                   'resource': text, 'status': {'enum': ['verified', 'unavailable', 'unknown']},
                   'observed_at': stamp, 'expires_at': nullable(stamp),
                   'evidence_ref': nullable(text), 'method': {'enum': ['action-result', 'permission-check', 'not-checked']}})
observation['allOf'] = [{'if': {'properties': {'status': {'const': 'verified'}}},
                        'then': {'properties': {'expires_at': stamp, 'evidence_ref': text,
                                                'method': {'enum': ['action-result', 'permission-check']}}}}]
step = obj({'step_id': text, 'role': {'enum': ['scheduler', 'executor']},
            'surface': surface, 'session_id': text, 'actions': arr(ref('action'), 1, uniqueItems=True),
            'cost': nullable(ref('cost')), 'duration_seconds': number,
            'delivery': {'enum': ['manual', 'adapter']}, 'adapter_ref': nullable(text)})
step['allOf'] = [{'if': {'properties': {'delivery': {'const': 'adapter'}}},
                 'then': {'properties': {'adapter_ref': text}}},
                {'if': {'properties': {'role': {'const': 'scheduler'}}},
                 'then': {'properties': {'surface': {'enum': ['SCHEDULED_CHAT', 'EXTERNAL_API']}}}}]
manifest = obj({'version': {'const': 1}, 'manifest_id': text, 'captured_at': stamp,
                'observations': arr(ref('observation'))})
plan = obj({'plan_id': text, 'cost_unit': {'const': 'usd_micro'}, 'steps': arr(ref('step'), 1)})
task = obj({'task_id': text, 'goal': text, 'current_surface': surface,
            'current_session_id': text, 'required_actions': arr(ref('action'), 1, uniqueItems=True),
            'authorized_actions': actions, 'authorization_ref': text,
            'forbidden_surfaces': arr(surface, uniqueItems=True), 'recurring': {'type': 'boolean'},
            'max_cost_units': nullable(number), 'max_duration_seconds': nullable(number),
            'transfer_count': number})
verification = obj({'criterion': text, 'result': {'enum': ['pass', 'fail', 'unknown']},
                    'evidence_ref': nullable(text), 'observed_at': stamp, 'commit_sha': nullable(ref('sha'))})
evidence = obj({'ref': text, 'description': text, 'observed_at': stamp,
                'commit_sha': nullable(ref('sha'))})
common = {'$defs': {'text': text, 'surface': surface, 'sha': {'type': 'string', 'pattern': '^[0-9a-f]{40}$'},
                   'action': action, 'cost': cost, 'observation': observation, 'step': step,
                   'plan': plan, 'task': task, 'manifest': manifest, 'verification': verification, 'evidence': evidence}}
request = obj({'version': {'const': 1}, 'task': ref('task'), 'capabilities': ref('manifest'),
               'candidates': arr(ref('plan'))})
handoff = obj({'version': {'const': 2}, 'task_id': text, 'handoff_id': text,
               'operation_id': text, 'parent_handoff_id': nullable(text),
               'direction': {'enum': ['delegation', 'return']},
               'status': {'enum': ['ready', 'completed', 'failed', 'blocked']},
               'from_surface': surface, 'from_session_id': text,
               'recommended_surface': surface, 'target_session_id': text,
               'policy_version': text, 'policy_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
               'created_at': stamp, 'goal': text, 'done': texts, 'remaining': texts,
               'repo': nullable({'type': 'string', 'pattern': '^[^/\\s]+/[^/\\s]+$'}),
               'branch': nullable(text), 'commit_sha': nullable(ref('sha')), 'files': texts,
               'constraints': texts, 'actions': actions,
               'authorized_actions': actions, 'authorization_ref': text,
               'forbidden_surfaces': arr(surface, uniqueItems=True),
               'cost_unit': {'const': 'usd_micro'}, 'estimated_cost_units': number,
               'max_cost_units': nullable(number), 'evidence': arr(ref('evidence')),
               'tests': arr(obj({'command': text, 'result': {'enum': ['pass', 'fail', 'not-run']},
                                 'evidence_ref': nullable(text), 'commit_sha': nullable(ref('sha'))})),
               'success_criteria': arr(ref('text'), 1, uniqueItems=True),
               'verification': arr(ref('verification')), 'escalation_reason': text,
               'return_to_chat_when': texts, 'extensions': {'type': 'object'}})
handoff['allOf'] = [
    {'if': {'properties': {'direction': {'const': 'delegation'}}},
     'then': {'properties': {'status': {'const': 'ready'}, 'remaining': arr(ref('text'), 1),
                             'actions': arr(ref('action'), 1), 'return_to_chat_when': arr(ref('text'), 1)}}},
    {'if': {'properties': {'direction': {'const': 'return'}}},
     'then': {'properties': {'status': {'enum': ['completed', 'failed', 'blocked']},
                             'parent_handoff_id': text, 'actions': {'maxItems': 0}}}},
    {'if': {'properties': {'status': {'const': 'completed'}}},
     'then': {'properties': {'remaining': {'maxItems': 0}, 'verification': arr(ref('verification'), 1)}}},
    {'if': {'properties': {'repo': {'type': 'string'}}},
     'then': {'properties': {'branch': text, 'commit_sha': ref('sha')}},
     'else': {'properties': {'branch': {'type': 'null'}, 'commit_sha': {'type': 'null'}, 'files': {'maxItems': 0}}}},
]
decision = obj({'version': {'const': 1}, 'task_id': text, 'evaluated_at': stamp,
                'policy_version': text, 'policy_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
                'status': {'enum': ['routed', 'blocked']}, 'reason': text,
                'route': nullable({'enum': SURFACES + ['HYBRID']}),
                'selected_plan_id': nullable(text), 'cost_unit': {'const': 'usd_micro'},
                'estimated_cost_units': nullable(number), 'plan': nullable(ref('plan')),
                'rejected': arr(obj({'plan_id': text, 'reasons': arr(ref('text'), 1)}))})
decision['allOf'] = [
    {'if': {'properties': {'status': {'const': 'blocked'}}},
     'then': {'properties': {k: {'type': 'null'} for k in ('route', 'selected_plan_id', 'estimated_cost_units', 'plan')}},
     'else': {'properties': {'route': {'enum': SURFACES + ['HYBRID']}, 'selected_plan_id': text,
                             'estimated_cost_units': number, 'plan': ref('plan')}}}]

if __name__ == '__main__':
    for name, schema in {'common': common, 'request': request, 'handoff': handoff,
                         'decision': decision, 'capabilities': manifest}.items():
        schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
                  '$id': URI + name + '.schema.json', 'title': name.title(), **schema}
        (ROOT / 'schemas' / (name + '.schema.json')).write_text(json.dumps(schema, indent=2) + '\n')
