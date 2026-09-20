"""Stable JSON contract for knowledge health reports."""
from __future__ import annotations
from dataclasses import asdict
import json
from knowledge_health import KnowledgeHealth

def to_json(health: KnowledgeHealth) -> str:
    return json.dumps(asdict(health), sort_keys=True, separators=(",", ":"))
