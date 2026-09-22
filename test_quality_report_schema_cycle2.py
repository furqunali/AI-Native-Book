from quality_report_schema import validate_quality_report

def test_quality_report_rejects_inconsistent_status():
    payload = {"chunks": 3, "empty": 1, "duplicate_ids": 0, "duplicate_texts": 0, "valid": True, "passed": True}
    assert not validate_quality_report(payload)

def test_quality_report_accepts_healthy_report():
    payload = {"chunks": 3, "empty": 0, "duplicate_ids": 0, "duplicate_texts": 0, "valid": True, "passed": True}
    assert validate_quality_report(payload)

def test_quality_report_rejects_negative_counts():
    payload = {"chunks": -1, "empty": 0, "duplicate_ids": 0, "duplicate_texts": 0, "valid": True, "passed": True}
    assert not validate_quality_report(payload)
