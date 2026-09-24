import pytest

from bare_url import BareURL, find_bare_urls, has_bare_urls


def test_finds_bare_url():
    (bare,) = find_bare_urls("See https://example.com for details.")
    assert bare.url == "https://example.com"
    assert bare.line == 1


def test_markdown_link_destination_not_flagged():
    assert find_bare_urls("See [the site](https://example.com).") == []


def test_autolink_not_flagged():
    assert find_bare_urls("See <https://example.com> now.") == []


def test_http_and_https_detected():
    urls = [b.url for b in find_bare_urls("a http://x.com b https://y.com")]
    assert urls == ["http://x.com", "https://y.com"]


def test_trailing_period_trimmed():
    (bare,) = find_bare_urls("Visit https://example.com/page.")
    assert bare.url == "https://example.com/page"


def test_trailing_paren_trimmed():
    (bare,) = find_bare_urls("(see https://example.com)")
    assert bare.url == "https://example.com"


def test_url_in_inline_code_ignored():
    assert find_bare_urls("Run `curl https://example.com` please.") == []


def test_url_in_fenced_code_ignored():
    text = "```\nhttps://example.com\n```\n"
    assert find_bare_urls(text) == []


def test_column_is_reported():
    (bare,) = find_bare_urls("xy https://example.com")
    assert bare.column == 4


def test_line_numbers_across_lines():
    text = "clean\nhttps://a.com\nclean\nhttps://b.com\n"
    lines = [b.line for b in find_bare_urls(text)]
    assert lines == [2, 4]


def test_non_http_scheme_ignored():
    assert find_bare_urls("mailto:me@example.com ftp://x.com") == []


def test_has_bare_urls_boolean():
    assert has_bare_urls("go to https://x.com") is True
    assert has_bare_urls("[x](https://x.com)") is False


def test_result_is_immutable():
    (bare,) = find_bare_urls("https://x.com")
    assert isinstance(bare, BareURL)
    with pytest.raises(AttributeError):
        bare.line = 5


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_bare_urls(None)
