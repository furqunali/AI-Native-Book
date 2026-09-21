from knowledge_quality import QualityReport
from quality_gate import QualityGate
from quality_report_export import quality_report_dict, quality_report_json

def test_export_is_stable():
    result = QualityGate(QualityReport(3, 0, 1, 2, False), True)
    assert quality_report_dict(result) == {
        "chunks": 3, "empty": 0, "duplicate_ids": 1, "duplicate_texts": 2,
        "valid": False, "passed": True,
    }
    assert quality_report_json(result) == '{"chunks": 3, "duplicate_ids": 1, "duplicate_texts": 2, "empty": 0, "passed": true, "valid": false}'


def test_export_rejects_wrong_type():
    try:
        quality_report_dict(object())
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")
