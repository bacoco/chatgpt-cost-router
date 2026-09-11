"""Strict bounded JSON values used by both independent products."""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path


class ContractError(ValueError):
    """An invalid or unauthorized operation, without private input in the error."""


ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,127}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SECRET_KEYS = {"password", "api_key", "access_token", "refresh_token", "private_key", "authorization"}


def identifier(value, label="identifier"):
    if not isinstance(value, str) or not ID.fullmatch(value) or ".." in value:
        raise ContractError(f"invalid {label}")
    return value


def fields(value, required, optional=()):
    if not isinstance(value, dict):
        raise ContractError("expected an object")
    if set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ContractError("missing or unknown contract field")
    return value


def number(value, low, high, label="number"):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"invalid {label}")
    if not low <= value <= high:
        raise ContractError(f"out-of-range {label}")
    return value


def integer(value, low, high, label="integer"):
    if type(value) is not int:
        raise ContractError(f"invalid {label}")
    return int(number(value, low, high, label))


def canonical(value):
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ContractError("invalid JSON value") from exc
    if len(text.encode()) > 1_048_576:
        raise ContractError("contract exceeds 1 MiB")
    return text


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _pairs(pairs):
    obj = {}
    for key, val in pairs:
        if key in obj:
            raise ContractError("duplicate JSON field")
        obj[key] = val
    return obj


def _nonfinite(_):
    raise ContractError("non-finite JSON")


def loads(text):
    if len(text) > 1_048_576:
        raise ContractError("JSON exceeds 1 MiB")
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise ContractError("invalid JSON") from exc


def load(path):
    return loads(Path(path).expanduser().read_text(encoding="utf-8"))


def no_credentials(value, depth=0):
    if depth > 32:
        raise ContractError("nested input is too deep")
    if isinstance(value, dict):
        for key, val in value.items():
            if not isinstance(key, str):
                raise ContractError("object keys must be strings")
            if key.lower().replace("-", "_") in SECRET_KEYS:
                raise ContractError("credentials belong in local transport configuration")
            no_credentials(val, depth + 1)
    elif isinstance(value, list):
        for val in value:
            no_credentials(val, depth + 1)
    canonical(value)
