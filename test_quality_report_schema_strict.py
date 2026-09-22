from quality_report_schema import validate_quality_report


def _valid_report() -> dict:
    return {
        "chunks": 3,
        "empty": 0,
        "duplicate_ids": 0,
        "duplicate_texts": 1,
        "valid": True,
        "passed": True,
    }


def test_schema_rejects_bool_as_count():
    payload = _valid_report()
    payload["chunks"] = True
    assert not validate_quality_report(payload)


def test_schema_accepts_zero_counts():
    assert validate_quality_report(_valid_report())
