from quality_gate import QualityGate
from quality_report_export import quality_report_dict, quality_report_json
from knowledge_quality import QualityReport

def test_export_is_stable():
    result = QualityGate(QualityReport(3, 0, 1, 2), True)
    assert quality_report_dict(result)["passed"] is True
    assert quality_report_json(result) == '{"duplicate_ids": 0, "duplicate_texts": 1, "empty": 2, "passed": true}'


def test_export_rejects_wrong_type():
    try:
        quality_report_dict(object())
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")
