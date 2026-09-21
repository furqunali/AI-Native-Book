"""Schema validation for exported corpus quality reports."""
from __future__ import annotations
REQUIRED_FIELDS = frozenset({"chunks","empty","duplicate_ids","duplicate_texts","valid","passed"})

def validate_quality_report(payload: dict) -> bool:
    if not isinstance(payload, dict) or set(payload) != REQUIRED_FIELDS:
        return False
    return all(isinstance(payload[name], bool) for name in ("valid","passed")) and all(
        isinstance(payload[name], int) and payload[name] >= 0
        for name in ("chunks","empty","duplicate_ids","duplicate_texts")
    )
