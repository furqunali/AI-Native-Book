from knowledge_health import KnowledgeHealth
from knowledge_health_json import to_json

def test_health_json_is_stable_and_machine_readable():
    health = KnowledgeHealth(3, 2, 120, 0, 0, 0, True)
    assert to_json(health) == '{"characters":120,"chunks":3,"duplicate_ids":0,"duplicate_texts":0,"empty":0,"sources":2,"valid":true}'
