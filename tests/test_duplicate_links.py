import pytest

from duplicate_links import (
    DuplicateLink,
    LinkUse,
    extract_links,
    find_duplicate_links,
    has_duplicate_links,
)


def test_extracts_links():
    uses = extract_links("See [docs](https://x.com) and [home](https://y.com).")
    assert [(u.text, u.url) for u in uses] == [
        ("docs", "https://x.com"),
        ("home", "https://y.com"),
    ]


def test_same_url_different_text_flagged():
    text = "[the docs](https://x.com)\n[click here](https://x.com)\n"
    (dup,) = find_duplicate_links(text)
    assert dup.url == "https://x.com"
    assert dup.texts == ("the docs", "click here")


def test_same_url_same_text_not_flagged():
    text = "[docs](https://x.com)\n[docs](https://x.com)\n"
    assert find_duplicate_links(text) == []


def test_different_urls_not_flagged():
    text = "[a](https://x.com) [b](https://y.com)"
    assert find_duplicate_links(text) == []


def test_three_texts_all_collected():
    text = "[a](u)\n[b](u)\n[c](u)\n"
    (dup,) = find_duplicate_links(text)
    assert dup.texts == ("a", "b", "c")


def test_uses_record_line_numbers():
    text = "[a](u)\n\n[b](u)\n"
    (dup,) = find_duplicate_links(text)
    assert [use.line for use in dup.uses] == [1, 3]


def test_link_title_discarded():
    (use,) = extract_links('[x](https://x.com "a title")')
    assert use.url == "https://x.com"


def test_links_in_code_fence_ignored():
    text = "```\n[a](u)\n[b](u)\n```\n"
    assert find_duplicate_links(text) == []


def test_groups_ordered_by_first_occurrence():
    text = "[a](u1)\n[b](u2)\n[c](u1)\n[d](u2)\n"
    dups = find_duplicate_links(text)
    assert [d.url for d in dups] == ["u1", "u2"]


def test_has_duplicate_links_boolean():
    assert has_duplicate_links("[a](u)\n[b](u)\n") is True
    assert has_duplicate_links("[a](u)\n") is False


def test_result_is_immutable():
    (dup,) = find_duplicate_links("[a](u)\n[b](u)\n")
    assert isinstance(dup, DuplicateLink)
    assert isinstance(dup.uses[0], LinkUse)
    with pytest.raises(AttributeError):
        dup.url = "z"


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_duplicate_links(None)


def test_extract_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_links(None)
