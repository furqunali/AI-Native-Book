"""Stable JSON contract for knowledge policy findings."""
from __future__ import annotations
from dataclasses import asdict
import json
from knowledge_policy import HealthFinding

def to_json(findings: tuple[HealthFinding, ...]) -> str:
    return json.dumps([asdict(finding) for finding in findings], sort_keys=True, separators=(",", ":"))
