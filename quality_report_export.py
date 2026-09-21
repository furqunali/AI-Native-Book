"""Stable JSON export for corpus quality-gate results."""
from __future__ import annotations
import json
from dataclasses import asdict
from quality_gate import QualityGate

def quality_report_dict(result: QualityGate) -> dict:
    if not isinstance(result, QualityGate):
        raise TypeError("result must be a QualityGate")
    data = asdict(result)
    return {"passed": data["passed"], **data["report"]}

def quality_report_json(result: QualityGate) -> str:
    return json.dumps(quality_report_dict(result), sort_keys=True)
