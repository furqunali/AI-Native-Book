import math

import pytest

from chapter_balance import (
    BalanceReport,
    Section,
    analyze_balance,
    format_balance_report,
)


def test_splits_at_section_level_headings():
    text = (
        "# Chapter\n\n"
        "## Alpha\n\none two three\n\n"
        "## Beta\n\nfour five\n"
    )
    report = analyze_balance(text)
    assert [(s.title, s.word_count) for s in report.sections] == [
        ("Alpha", 3),
        ("Beta", 2),
    ]
    assert report.section_count == 2
    assert report.total_words == 5


def test_prose_before_first_section_is_preamble():
    text = "# Chapter\n\nlead in words here\n\n## Alpha\n\nbody text\n"
    report = analyze_balance(text)
    # "lead in words here" = 4 words, none attributed to a section.
    assert report.preamble_words == 4
    assert report.total_words == 2
    assert report.section_count == 1


def test_nested_subsections_fold_into_parent_section():
    text = (
        "## Alpha\n\none two\n\n"
        "### Deeper\n\nthree four five\n\n"
        "## Beta\n\nsix\n"
    )
    report = analyze_balance(text)
    counts = {s.title: s.word_count for s in report.sections}
    # Alpha keeps its own prose plus the subsection prose (2 + 3 = 5).
    assert counts == {"Alpha": 5, "Beta": 1}


def test_shallower_heading_closes_section_and_returns_to_preamble():
    # With section_level=2, an H1 after an H2 section ends that section; the
    # prose beneath the H1 (but before the next H2) is preamble again.
    text = (
        "## Alpha\n\none two\n\n"
        "# Part Two\n\norphan prose here\n\n"
        "## Beta\n\nthree\n"
    )
    report = analyze_balance(text)
    counts = {s.title: s.word_count for s in report.sections}
    assert counts == {"Alpha": 2, "Beta": 1}
    assert report.preamble_words == 3  # "orphan prose here"


def test_fenced_code_is_not_counted_and_hashes_are_not_headings():
    text = (
        "## Alpha\n\nreal prose\n\n"
        "```bash\n# not a heading\necho lots of words in code\n```\n\n"
        "more prose\n"
    )
    report = analyze_balance(text)
    (alpha,) = report.sections
    assert report.section_count == 1
    # "real prose" + "more prose" = 4 words; nothing from inside the fence.
    assert alpha.word_count == 4


def test_inline_markdown_and_links_reduce_to_plain_words():
    text = "## Alpha\n\nThe **bold** `code` and [link](http://x.com) end\n"
    (alpha,) = analyze_balance(text).sections
    # bold, code, and, link, end plus The => "The bold code and link end" = 6.
    assert alpha.word_count == 6


def test_custom_section_level():
    text = "# Top\n\n## Alpha\n\none two\n\n## Beta\n\nthree\n"
    report = analyze_balance(text, section_level=1)
    # At level 1 there is a single section (the H1), everything folds into it.
    assert report.section_count == 1
    assert report.sections[0].title == "Top"
    assert report.sections[0].word_count == 3


def test_no_sections_reports_all_prose_as_preamble_and_is_balanced():
    text = "just some prose with no headings at all\n"
    report = analyze_balance(text)
    assert report.section_count == 0
    assert report.sections == ()
    assert report.total_words == 0
    assert report.preamble_words == 8
    assert report.balanced is True
    assert report.imbalance_ratio == 0.0
    assert report.coefficient_of_variation == 0.0


def test_empty_text_returns_zeroed_report():
    report = analyze_balance("")
    assert report == BalanceReport(
        section_count=0,
        total_words=0,
        preamble_words=0,
        sections=(),
        mean_words=0.0,
        min_words=0,
        max_words=0,
        imbalance_ratio=0.0,
        coefficient_of_variation=0.0,
        balanced=True,
    )


def test_single_section_is_perfectly_balanced():
    report = analyze_balance("## Only\n\none two three\n")
    assert report.section_count == 1
    assert report.coefficient_of_variation == 0.0
    assert report.imbalance_ratio == 1.0
    assert report.balanced is True


def test_even_sections_have_low_cv_and_are_balanced():
    text = "## A\n\none two\n\n## B\n\nthree four\n\n## C\n\nfive six\n"
    report = analyze_balance(text)
    assert report.mean_words == 2.0
    assert report.coefficient_of_variation == 0.0
    assert report.imbalance_ratio == 1.0
    assert report.balanced is True


def test_lopsided_sections_are_flagged_imbalanced():
    big = " ".join(["word"] * 100)
    text = f"## Big\n\n{big}\n\n## Tiny\n\none\n"
    report = analyze_balance(text)
    assert report.max_words == 100
    assert report.min_words == 1
    assert report.imbalance_ratio == 100.0
    assert report.coefficient_of_variation > 0.5
    assert report.balanced is False


def test_empty_section_yields_infinite_imbalance_ratio():
    text = "## Full\n\nsome words here now\n\n## Empty\n"
    report = analyze_balance(text)
    assert report.min_words == 0
    assert report.max_words == 4
    assert math.isinf(report.imbalance_ratio)
    assert report.balanced is False


def test_mean_min_max_are_reported():
    text = "## A\n\none\n\n## B\n\none two\n\n## C\n\none two three\n"
    report = analyze_balance(text)
    assert report.min_words == 1
    assert report.max_words == 3
    assert report.mean_words == 2.0


def test_format_report_renders_table_and_shares():
    text = "## Alpha\n\none two three\n\n## Beta\n\nfour\n"
    out = format_balance_report(analyze_balance(text))
    assert "| Section | Words | Share |" in out
    assert "| Alpha | 3 | 75% |" in out
    assert "| Beta | 1 | 25% |" in out
    assert "2 sections" in out
    assert "balanced" in out


def test_format_report_marks_imbalance():
    big = " ".join(["word"] * 50)
    text = f"## Big\n\n{big}\n\n## Tiny\n\none\n"
    out = format_balance_report(analyze_balance(text))
    assert "imbalanced" in out


def test_format_report_handles_no_sections():
    report = analyze_balance("prose only\n")
    assert format_balance_report(report) == "_No sections found._"


def test_untitled_section_is_labelled_in_table():
    # An H2 with no title text still opens a section.
    text = "##\n\nsome words\n"
    out = format_balance_report(analyze_balance(text))
    assert "(untitled)" in out


def test_analyze_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        analyze_balance(None)


def test_analyze_rejects_bad_section_level():
    with pytest.raises(ValueError, match="between 1 and 6"):
        analyze_balance("## H\n", section_level=0)
    with pytest.raises(ValueError, match="between 1 and 6"):
        analyze_balance("## H\n", section_level=7)
    with pytest.raises(TypeError, match="must be an int"):
        analyze_balance("## H\n", section_level=True)


def test_format_report_rejects_non_report():
    with pytest.raises(TypeError, match="must be a BalanceReport"):
        format_balance_report({"section_count": 0})


def test_report_and_section_are_immutable():
    report = analyze_balance("## A\n\none\n")
    with pytest.raises(AttributeError):
        report.balanced = False
    with pytest.raises(AttributeError):
        report.sections[0].word_count = 99


def test_section_dataclass_shape():
    (section,) = analyze_balance("## A\n\none two\n").sections
    assert section == Section(title="A", level=2, start_line=1, word_count=2)
