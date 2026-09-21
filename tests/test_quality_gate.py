from knowledge_source import KnowledgeChunk
from quality_gate import evaluate_quality_gate

def c(i,text): return KnowledgeChunk(str(i),"book.md","Book",text,i)

def test_gate_passes_clean_corpus():
    gate = evaluate_quality_gate([c(0,"alpha"),c(1,"beta")])
    assert gate.passed is True and gate.report.chunks == 2

def test_gate_rejects_duplicates():
    gate = evaluate_quality_gate([c(0,"same"),c(1,"same")])
    assert gate.passed is False and gate.report.duplicate_texts == 1
