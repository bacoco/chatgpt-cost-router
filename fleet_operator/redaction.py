"""Best-effort credential redaction. Public GitHub is not a confidential log store."""
import re
from operation_contracts.common import SECRET_KEYS

PATTERNS = [
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----",re.S),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/-]+=*",re.I),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
]


def redact(value):
    if isinstance(value,dict):
        return {key:"[REDACTED]" if str(key).lower().replace("-","_") in SECRET_KEYS else redact(val) for key,val in value.items()}
    if isinstance(value,list):
        return [redact(item) for item in value]
    if isinstance(value,str):
        for pattern in PATTERNS:
            value = pattern.sub("[REDACTED]",value)
    return value
