from quality_report_schema import validate_quality_report


def test_valid_quality_schema():
    assert validate_quality_report({"chunks":3,"empty":0,"duplicate_ids":0,"duplicate_texts":1,"valid":False,"passed":True})

def test_invalid_quality_schema():
    assert not validate_quality_report({"chunks":-1,"empty":0,"duplicate_ids":0,"duplicate_texts":0,"valid":True,"passed":True})
