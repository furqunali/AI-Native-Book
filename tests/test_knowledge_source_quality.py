from knowledge_source import KnowledgeChunk
from knowledge_source_quality import profile_source_quality

def c(i,s,t): return KnowledgeChunk(str(i),s,"title",t,i)

def test_profiles_sources_and_duplicates():
    result=profile_source_quality([c(0,"a","one"),c(1,"a","one"),c(2,"b","long")])
    assert result[0].chunks == 2 and result[0].duplicate_texts == 1
    assert result[1].average_length == 4.0

def test_empty_corpus():
    assert profile_source_quality([]) == ()
