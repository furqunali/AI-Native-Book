from knowledge_policy import HealthFinding
from knowledge_policy_json import to_json


def test_policy_json_is_stable():
    findings = (HealthFinding("DUPLICATE_IDS", "warning", "2 duplicate chunk ids detected"),)
    assert to_json(findings) == '[{"code":"DUPLICATE_IDS","message":"2 duplicate chunk ids detected","severity":"warning"}]'
