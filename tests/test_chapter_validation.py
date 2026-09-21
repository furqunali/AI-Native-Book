from pathlib import Path
from chapter_validation import validate_chapter

def test_valid_chapter_has_no_issues():
    text="# Chapter\n\n"+"Useful content. "*30
    assert validate_chapter(Path("chapter.md"),text)==[]

def test_invalid_chapter_reports_structure():
    issues=validate_chapter(Path("empty.md"),"")
    assert {issue.code for issue in issues}=={"empty","heading","short"}


def test_heading_inside_fenced_code_does_not_count():
    text="```markdown\n# Not a chapter heading\n```\n\n"+"Useful content. "*20
    issues=validate_chapter(Path("chapter.md"), text)
    assert "heading" in {issue.code for issue in issues}


def test_heading_inside_tilde_fence_does_not_count():
    text="~~~markdown\n# Not a chapter heading\n~~~\n\n"+"Useful content. "*20
    issues=validate_chapter(Path("chapter.md"), text)
    assert "heading" in {issue.code for issue in issues}


def test_fenced_code_does_not_satisfy_body_length():
    text = "# Chapter\n\n" + "```\n" + ("example code. " * 15) + "```\n\n" + ("Useful content. " * 4)
    issues = validate_chapter(Path("chapter.md"), text)
    assert "short" in {issue.code for issue in issues}


def test_validate_chapter_rejects_non_string_text():
    import pytest
    with pytest.raises(TypeError, match="text must be a string"):
        validate_chapter(Path("chapter.md"), None)
