"""Validation helpers for chapter structure and metadata."""
from __future__ import annotations
from dataclasses import dataclass
import re
from pathlib import Path

@dataclass(frozen=True)
class ChapterIssue:
    path: str
    code: str
    message: str

def _strip_fenced_code(text: str) -> str:
    return re.sub(r"^```.*?^```[ \\t]*$", "", text, flags=re.MULTILINE | re.DOTALL)

def validate_chapter(path: Path, text: str) -> list[ChapterIssue]:
    issues=[]
    if not text.strip():
        issues.append(ChapterIssue(str(path),"empty","chapter is empty"))
    if not re.search(r"^#\s+\S+", text, re.MULTILINE):
        issues.append(ChapterIssue(str(path),"heading","chapter needs a level-one heading"))
    if len(text.strip()) < 200:
        issues.append(ChapterIssue(str(path),"short","chapter has insufficient body content"))
    return issues
