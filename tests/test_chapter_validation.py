from pathlib import Path
from chapter_validation import validate_chapter

def test_valid_chapter_has_no_issues():
    text="# Chapter\n\n"+"Useful content. "*30
    assert validate_chapter(Path("chapter.md"),text)==[]

def test_invalid_chapter_reports_structure():
    issues=validate_chapter(Path("empty.md"),"")
    assert {issue.code for issue in issues}=={"empty","heading","short"}
