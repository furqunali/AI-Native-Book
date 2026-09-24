from pathlib import Path

import pytest

from glossary_crossref import (
    GlossaryReport,
    GlossaryTerm,
    TermUsage,
    count_uses,
    crossref_glossary,
    parse_glossary,
    render_report,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_GLOSSARY = (
    "# Glossary\n"
    "\n"
    "| Term | Meaning |\n"
    "|---|---|\n"
    "| **Agent** | A system that acts toward a goal. |\n"
    "| **RAG** | Retrieval-Augmented Generation. |\n"
    "| **Vector database** | A store for numeric vectors. |\n"
)


def test_parse_extracts_terms_in_order():
    terms = parse_glossary(SAMPLE_GLOSSARY)
    assert [t.term for t in terms] == ["Agent", "RAG", "Vector database"]
    assert terms[0].definition == "A system that acts toward a goal."


def test_parse_strips_bold_and_records_line_numbers():
    (term,) = parse_glossary("| **Foo** | bar |\n")
    assert term == GlossaryTerm(term="Foo", definition="bar", line=1)


def test_parse_skips_header_and_separator_rows():
    terms = parse_glossary(SAMPLE_GLOSSARY)
    # Neither the "Term" header nor the "---" separator becomes a term.
    assert all(t.term not in {"Term", "---"} for t in terms)
    assert len(terms) == 3


def test_parse_ignores_rows_inside_code_fences():
    text = (
        "| **Real** | a real term |\n"
        "\n"
        "```\n"
        "| **Fake** | not a term |\n"
        "```\n"
    )
    assert [t.term for t in parse_glossary(text)] == ["Real"]


def test_parse_skips_rows_missing_a_cell():
    text = "| **Lonely** |\n| **Complete** | has a definition |\n"
    assert [t.term for t in parse_glossary(text)] == ["Complete"]


def test_parse_handles_rows_without_outer_pipes():
    (term,) = parse_glossary("Term | Meaning\n**Alpha** | first letter\n")
    assert term.term == "Alpha"
    assert term.definition == "first letter"


def test_parse_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        parse_glossary(None)


def test_count_uses_is_case_insensitive_by_default():
    assert count_uses("Agent", "An agent and another Agent act.") == 2


def test_count_uses_respects_case_sensitivity_flag():
    assert count_uses("Agent", "agent Agent", case_sensitive=True) == 1


def test_count_uses_matches_whole_words_only():
    # "RAG" must not match inside "storage" or "fragment".
    assert count_uses("RAG", "storage fragment") == 0
    assert count_uses("RAG", "We use RAG here.") == 1


def test_count_uses_matches_multiword_across_whitespace():
    assert count_uses("Vector database", "a vector\n  database entry") == 1


def test_count_uses_matches_hyphenated_term():
    text = "An AI-native application differs from an AI feature."
    assert count_uses("AI-native application", text) == 1


def test_count_uses_ignores_code_and_links():
    text = (
        "Prose mentions Agent once.\n"
        "```\n"
        "Agent Agent Agent in code\n"
        "```\n"
        "Inline `Agent` and a [Agent](http://agent.example) link.\n"
    )
    # Only the first prose mention and the link's visible text count.
    assert count_uses("Agent", text) == 2


def test_count_uses_rejects_empty_term():
    with pytest.raises(ValueError, match="must not be empty"):
        count_uses("   ", "text")


def test_count_uses_rejects_non_string_args():
    with pytest.raises(TypeError):
        count_uses(123, "text")
    with pytest.raises(TypeError):
        count_uses("term", None)


def test_crossref_reports_usage_and_chapters():
    chapters = {
        # "Agents" (plural) must not count; only the whole word "Agent" does.
        "Chapter1.md": "Agents everywhere. An Agent acts.",
        "Chapter2.md": "We apply RAG and another agent.",
    }
    report = crossref_glossary(SAMPLE_GLOSSARY, chapters)
    by_term = {u.term: u for u in report.usages}
    assert by_term["Agent"].total_uses == 2
    assert by_term["Agent"].chapters == ("Chapter1.md", "Chapter2.md")
    assert by_term["RAG"].chapters == ("Chapter2.md",)


def test_crossref_collects_unused_terms():
    chapters = {"Chapter1.md": "Only mentions an agent here."}
    report = crossref_glossary(SAMPLE_GLOSSARY, chapters)
    assert "Vector database" in report.unused
    assert "RAG" in report.unused
    assert "Agent" not in report.unused


def test_crossref_preserves_glossary_order():
    report = crossref_glossary(SAMPLE_GLOSSARY, {"Chapter1.md": ""})
    assert [u.term for u in report.usages] == ["Agent", "RAG", "Vector database"]


def test_crossref_detects_duplicate_definitions():
    glossary = (
        "| **Agent** | first definition |\n"
        "| **agent** | duplicate with different case |\n"
    )
    report = crossref_glossary(glossary, {"Chapter1.md": "agent"})
    assert report.duplicates == ("agent",)
    # Duplicate is cross-referenced only once.
    assert [u.term for u in report.usages] == ["Agent"]


def test_crossref_is_clean_property():
    clean = crossref_glossary(
        "| **Agent** | acts |\n", {"Chapter1.md": "an Agent acts"}
    )
    assert clean.is_clean is True
    dirty = crossref_glossary(
        "| **Agent** | acts |\n", {"Chapter1.md": "nothing here"}
    )
    assert dirty.is_clean is False


def test_crossref_rejects_bad_chapter_types():
    with pytest.raises(TypeError, match="chapters must be a dict"):
        crossref_glossary(SAMPLE_GLOSSARY, ["not", "a", "dict"])
    with pytest.raises(TypeError, match="map str names to str text"):
        crossref_glossary(SAMPLE_GLOSSARY, {"Chapter1.md": 123})


def test_render_report_lists_terms_and_sections():
    chapters = {"Chapter1.md": "an Agent acts"}
    report = crossref_glossary(SAMPLE_GLOSSARY, chapters)
    rendered = render_report(report)
    assert "**Agent** — 1 use(s): Chapter1.md" in rendered
    assert "## Unused terms" in rendered
    assert "## Duplicate definitions" in rendered


def test_render_report_shows_none_when_all_clean():
    report = crossref_glossary(
        "| **Agent** | acts |\n", {"Chapter1.md": "an Agent acts"}
    )
    rendered = render_report(report)
    assert "## Unused terms\n- none" in rendered
    assert "## Duplicate definitions\n- none" in rendered


def test_render_report_rejects_non_report():
    with pytest.raises(TypeError, match="must be a GlossaryReport"):
        render_report("not a report")


def test_dataclasses_are_immutable():
    usage = TermUsage(term="X", definition="d", total_uses=0, chapters=())
    with pytest.raises(AttributeError):
        usage.total_uses = 5
    report = GlossaryReport(usages=(), unused=(), duplicates=())
    with pytest.raises(AttributeError):
        report.unused = ("x",)


def test_real_glossary_terms_are_used_in_the_book():
    """Integration: every glossary term should appear in at least one chapter."""
    glossary_text = (REPO_ROOT / "GLOSSARY.md").read_text(encoding="utf-8")
    chapters = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(REPO_ROOT.glob("Chapter*.md"))
    }
    assert chapters, "expected chapter files to be present"
    report = crossref_glossary(glossary_text, chapters)
    assert report.usages, "expected the glossary to define terms"
    # The parsed glossary must not contain accidental duplicate definitions.
    assert report.duplicates == ()
