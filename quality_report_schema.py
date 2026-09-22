"""Schema validation for exported corpus quality reports."""
from __future__ import annotations

REQUIRED_FIELDS = frozenset({"chunks", "empty", "duplicate_ids", "duplicate_texts", "valid", "passed"})


def validate_quality_report(payload: dict) -> bool:
    if not isinstance(payload, dict) or set(payload) != REQUIRED_FIELDS:
        return False
    counts = ("chunks", "empty", "duplicate_ids", "duplicate_texts")
    if not all(type(payload[name]) is int and payload[name] >= 0 for name in counts):
        return False
    return all(isinstance(payload[name], bool) for name in ("valid", "passed"))
