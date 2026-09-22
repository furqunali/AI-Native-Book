"""Stable JSON export for corpus quality-gate results."""
from __future__ import annotations
import json
from dataclasses import asdict
from quality_gate import QualityGate
from quality_report_schema import validate_quality_report

def quality_report_dict(result: QualityGate) -> dict:
    if not isinstance(result, QualityGate):
        raise TypeError("result must be a QualityGate")
    data = asdict(result)
    payload = {"passed": data["passed"], **data["report"]}
    if not validate_quality_report(payload):
        raise ValueError("quality report failed schema validation")
    return payload

def quality_report_json(result: QualityGate) -> str:
    return json.dumps(quality_report_dict(result), sort_keys=True)
