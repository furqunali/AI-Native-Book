from knowledge_quality import inspect_chunks
from knowledge_source import KnowledgeChunk


def c(identifier,text):
    return KnowledgeChunk(identifier,"Chapter1.md","Intro",text,0)

def test_quality_report_accepts_unique_nonempty_chunks():
    report=inspect_chunks([c("a","alpha"),c("b","beta")])
    assert report.valid
    assert report.chunks==2

def test_quality_report_detects_duplicates_and_empty_text():
    report=inspect_chunks([c("a",""),c("a","same"),c("b","same")])
    assert report.empty==1
    assert report.duplicate_ids==1
    assert report.duplicate_texts==1
    assert not report.valid
