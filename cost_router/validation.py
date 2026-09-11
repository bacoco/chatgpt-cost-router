"""Local-only schema resolution and policy validation."""
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT if (ROOT / 'schemas').is_dir() else Path(__file__).resolve().parent / 'data'
SURFACES = ('CHAT', 'SCHEDULED_CHAT', 'LOCAL_TOOL', 'CODEX', 'WORK', 'EXTERNAL_API')


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)', value):
        raise ValueError('Expected a timezone-aware RFC3339 timestamp')
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def clock(now=None):
    value = datetime.now(timezone.utc) if now is None else now
    if isinstance(value, str):
        value = timestamp(value)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Evaluation time must have a timezone')
    return value.astimezone(timezone.utc)


FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=(ValueError, TypeError))
def valid_timestamp(value):
    timestamp(value)
    return True


def load_json(path):
    def reject_constant(value):
        raise ValueError('Non-finite JSON number: ' + value)
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON field: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), parse_constant=reject_constant,
                      object_pairs_hook=unique_object)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=8)
def validator(name):
    if name not in ('common', 'request', 'capabilities', 'handoff', 'decision'):
        raise ValueError('Unknown schema: ' + name)
    schemas = [load_json(p) for p in sorted((DATA / 'schemas').glob('*.schema.json'))]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    # Only these local resources are resolvable; no remote schema retrieval.
    registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas)
    schema = next(s for s in schemas if s['$id'].endswith('/' + name + '.schema.json'))
    return Draft202012Validator(schema, registry=registry, format_checker=FORMATS)


def validate(name, value):
    validator(name).validate(value)
    return value


def policy_config(value=None):
    policy = load_json(DATA / 'policy/routing.json') if value is None else dict(value)
    expected = {'version', 'cost_unit', 'tie_break_order', 'max_transfers',
                'min_transfer_savings_units', 'max_capability_age_seconds'}
    if set(policy) != expected or policy['cost_unit'] != 'usd_micro':
        raise ValueError('Invalid routing policy fields or cost unit')
    if not isinstance(policy['version'], str) or not policy['version'].strip():
        raise ValueError('A policy version is required')
    order = policy['tie_break_order']
    if not isinstance(order, list) or len(order) != len(SURFACES) or set(order) != set(SURFACES):
        raise ValueError('Tie-break order must contain each canonical surface once')
    for key in ('max_transfers', 'min_transfer_savings_units', 'max_capability_age_seconds'):
        if type(policy[key]) is not int or policy[key] < 0:
            raise ValueError(key + ' must be a nonnegative integer')
    return policy
