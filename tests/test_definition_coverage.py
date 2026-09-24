import pytest

from definition_coverage import (
    TermCoverage,
    check_coverage,
    coverage_ratio,
    unused_terms,
)


def test_used_and_unused_terms():
    text = "An agent uses a model to plan.\n"
    coverage = check_coverage(["agent", "model", "widget"], text)
    by_term = {c.term: c for c in coverage}
    assert by_term["agent"].used is True
    assert by_term["model"].used is True
    assert by_term["widget"].used is False


def test_unused_terms_helper():
    text = "The agent runs.\n"
    assert unused_terms(["agent", "gizmo", "sprocket"], text) == ["gizmo", "sprocket"]


def test_count_multiple_occurrences():
    text = "agent agent agent everywhere\n"
    (cov,) = check_coverage(["agent"], text)
    assert cov.count == 3


def test_case_insensitive():
    text = "The Agent and the AGENT.\n"
    (cov,) = check_coverage(["agent"], text)
    assert cov.count == 2


def test_word_boundary_prevents_substring():
    text = "management of reagents\n"
    (cov,) = check_coverage(["agent"], text)
    assert cov.used is False


def test_multiword_term_across_whitespace():
    text = "the context\nwindow is finite\n"
    (cov,) = check_coverage(["context window"], text)
    assert cov.used is True


def test_code_span_ignored():
    text = "we call `agent.run()` but never mention it in prose\n"
    (cov,) = check_coverage(["agent"], text)
    assert cov.used is False


def test_fenced_code_ignored():
    text = "prose only\n```\nagent agent agent\n```\n"
    (cov,) = check_coverage(["agent"], text)
    assert cov.count == 0


def test_order_preserved_and_deduplicated():
    coverage = check_coverage(["b", "a", "B"], "nothing here")
    assert [c.term for c in coverage] == ["b", "a"]


def test_coverage_ratio():
    text = "agent and model\n"
    assert coverage_ratio(["agent", "model", "tool", "loop"], text) == 0.5


def test_coverage_ratio_empty_terms():
    assert coverage_ratio([], "text") == 0.0


def test_rejects_non_list_terms():
    with pytest.raises(TypeError, match="terms must be a list"):
        check_coverage("agent", "text")


def test_rejects_non_string_text():
    with pytest.raises(TypeError, match="text must be a string"):
        check_coverage(["agent"], None)


def test_rejects_empty_term():
    with pytest.raises(ValueError, match="terms must not be empty"):
        check_coverage(["agent", "  "], "text")


def test_coverage_is_immutable():
    (cov,) = check_coverage(["agent"], "agent\n")
    assert isinstance(cov, TermCoverage)
    with pytest.raises(AttributeError):
        cov.count = 0
