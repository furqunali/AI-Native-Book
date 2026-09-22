"""CLI for validating and exporting the AI-Native Book knowledge source."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from chapter_validation import validate_chapter
from knowledge_manifest import build_book_manifest, write_manifest
from knowledge_quality import inspect_chunks
from knowledge_source import build_knowledge_source, write_jsonl


def build_parser():
    p=argparse.ArgumentParser(description="Validate and export book knowledge")
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--jsonl",type=Path)
    p.add_argument("--manifest",type=Path)
    p.add_argument("--validate",action="store_true")
    return p

def main():
    a=build_parser().parse_args(); root=a.root.resolve()
    chunks=build_knowledge_source(root); quality=inspect_chunks(chunks)
    manifest=build_book_manifest(root); issues=[]
    for path in sorted(root.glob("Chapter*.md")):
        issues.extend(validate_chapter(path,path.read_text(encoding="utf-8")))
    if a.jsonl: write_jsonl(chunks,a.jsonl)
    if a.manifest: write_manifest(manifest,a.manifest)
    payload={"chunks":quality.chunks,"empty":quality.empty,"duplicate_ids":quality.duplicate_ids,
             "duplicate_texts":quality.duplicate_texts,"chapter_issues":[i.__dict__ for i in issues],
             "manifest_digest":manifest.digest,"valid":quality.valid and not issues}
    print(json.dumps(payload,indent=2))
    return 0 if payload["valid"] or not a.validate else 1

if __name__=="__main__":
    raise SystemExit(main())
