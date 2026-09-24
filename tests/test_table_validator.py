import pytest

from table_validator import (
    TableIssue,
    has_valid_tables,
    validate_tables,
)


def test_valid_table_has_no_issues():
    text = (
        "| Name | Role |\n"
        "| --- | --- |\n"
        "| Ada | Engineer |\n"
        "| Alan | Researcher |\n"
    )
    assert validate_tables(text) == []
    assert has_valid_tables(text) is True


def test_valid_table_without_outer_pipes():
    text = "Name | Role\n--- | ---\nAda | Engineer\n"
    assert validate_tables(text) == []


def test_alignment_delimiters_are_accepted():
    text = "| L | C | R |\n| :-- | :--: | --: |\n| a | b | c |\n"
    assert validate_tables(text) == []


def test_body_row_column_mismatch_is_reported():
    text = "| A | B |\n| --- | --- |\n| only-one |\n"
    (issue,) = validate_tables(text)
    assert issue.kind == "row-column-mismatch"
    assert issue.line == 3
    assert has_valid_tables(text) is False


def test_delimiter_column_mismatch_is_reported():
    text = "| A | B | C |\n| --- | --- |\n| x | y | z |\n"
    kinds = [i.kind for i in validate_tables(text)]
    assert "delimiter-column-mismatch" in kinds


def test_prose_with_pipes_is_not_a_table():
    text = "The choices are red | green | blue in most themes.\n"
    assert validate_tables(text) == []


def test_missing_delimiter_means_not_a_table():
    # Two pipe lines but the second is not a delimiter row.
    text = "| A | B |\n| x | y |\n"
    assert validate_tables(text) == []


def test_escaped_pipes_do_not_split_columns():
    text = "| Expr | Result |\n| --- | --- |\n| a \\| b | ok |\n"
    assert validate_tables(text) == []


def test_tables_inside_code_fences_are_ignored():
    text = "```\n| A | B |\n| - |\n| x |\n```\n"
    assert validate_tables(text) == []


def test_multiple_tables_are_each_validated():
    text = (
        "| A | B |\n| --- | --- |\n| 1 | 2 |\n"
        "\n"
        "| C | D |\n| --- | --- |\n| 3 |\n"
    )
    issues = validate_tables(text)
    assert len(issues) == 1
    assert issues[0].line == 7


def test_validate_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        validate_tables(42)


def test_issue_is_immutable():
    text = "| A | B |\n| --- | --- |\n| x |\n"
    (issue,) = validate_tables(text)
    assert isinstance(issue, TableIssue)
    with pytest.raises(AttributeError):
        issue.kind = "changed"
