import pytest

from sentence_start_variety import (
    StartRepeat,
    check_start_variety,
    is_varied,
    opening_words,
)


def test_repeated_opener_flagged():
    text = "The cat sat. The dog ran. The bird flew.\n"
    (repeat,) = check_start_variety(text, threshold=3)
    assert repeat.word == "the"
    assert repeat.count == 3
    assert repeat.sentences == (1, 2, 3)
    assert is_varied(text, threshold=3) is False


def test_varied_openers_pass():
    text = "Agents plan. Models predict. Tools execute.\n"
    assert check_start_variety(text, threshold=2) == []
    assert is_varied(text, threshold=2) is True


def test_threshold_boundary():
    text = "This works. This too. This again.\n"
    assert check_start_variety(text, threshold=4) == []
    assert len(check_start_variety(text, threshold=3)) == 1


def test_case_insensitive_openers():
    text = "The one. the two. THE three.\n"
    (repeat,) = check_start_variety(text, threshold=3)
    assert repeat.word == "the"


def test_opening_words_reading_order():
    text = "Alpha runs. Beta walks.\n"
    assert opening_words(text) == ["alpha", "beta"]


def test_multiple_repeats_sorted_by_count():
    text = "It a. It b. It c. We x. We y.\n"
    repeats = check_start_variety(text, threshold=2)
    assert [r.word for r in repeats] == ["it", "we"]
    assert repeats[0].count == 3


def test_fenced_code_ignored():
    text = "The intro sentence stands alone.\n```\nThe fake. The fake. The fake.\n```\n"
    assert check_start_variety(text, threshold=2) == []


def test_heading_markers_stripped():
    text = "## The heading\n\nThe body one. The body two.\n"
    (repeat,) = check_start_variety(text, threshold=3)
    assert repeat.word == "the"
    assert repeat.count == 3


def test_questions_and_exclamations_split():
    text = "Why now? Why later? Why ever?\n"
    (repeat,) = check_start_variety(text, threshold=3)
    assert repeat.word == "why"


def test_empty_text_returns_empty():
    assert check_start_variety("", threshold=2) == []


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        opening_words(None)


def test_rejects_low_threshold():
    with pytest.raises(ValueError, match="at least 2"):
        check_start_variety("hi.", threshold=1)


def test_rejects_bool_threshold():
    with pytest.raises(TypeError, match="threshold must be an int"):
        check_start_variety("hi.", threshold=True)


def test_repeat_is_immutable():
    (repeat,) = check_start_variety("A x. A y. A z.\n", threshold=3)
    assert isinstance(repeat, StartRepeat)
    with pytest.raises(AttributeError):
        repeat.count = 0
