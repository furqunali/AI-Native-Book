import pytest

from passive_voice import (
    PassiveSentence,
    find_passive_sentences,
    passive_ratio,
)


def test_flags_simple_passive():
    (flagged,) = find_passive_sentences("The model was trained on data.")
    assert flagged.trigger == "was trained"
    assert flagged.index == 0


def test_active_sentence_not_flagged():
    assert find_passive_sentences("The team trained the model.") == []


def test_adverb_between_be_and_participle():
    (flagged,) = find_passive_sentences("Results are clearly shown here.")
    assert flagged.trigger == "are shown"


def test_irregular_participle_detected():
    (flagged,) = find_passive_sentences("The work was done overnight.")
    assert flagged.trigger == "was done"


def test_get_passive_detected():
    (flagged,) = find_passive_sentences("The bug got fixed quickly.")
    assert flagged.trigger.startswith("got")


def test_stop_participle_not_flagged():
    # "used" is a common false positive that we intentionally skip.
    assert find_passive_sentences("This is used everywhere.") == []


def test_multiple_sentences_indices():
    text = "The task was completed. Then we shipped it. It was reviewed later."
    flagged = find_passive_sentences(text)
    assert [f.index for f in flagged] == [0, 2]


def test_code_and_headings_ignored():
    text = "# The plan was approved\n\n```\nx was set\n```\n\nWe move on.\n"
    assert find_passive_sentences(text) == []


def test_ratio_computation():
    text = "It was seen. We ran fast."
    assert passive_ratio(text) == 0.5


def test_ratio_empty_is_zero():
    assert passive_ratio("") == 0.0


def test_predicate_adjective_short_word_not_flagged():
    # "red" is too short to be treated as a participle.
    assert find_passive_sentences("The light was red.") == []


def test_result_is_immutable():
    (flagged,) = find_passive_sentences("The file was written.")
    assert isinstance(flagged, PassiveSentence)
    with pytest.raises(AttributeError):
        flagged.index = 3


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_passive_sentences(None)


def test_empty_text_no_flags():
    assert find_passive_sentences("") == []
