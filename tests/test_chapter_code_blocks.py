import pytest

from chapter_code_blocks import (
    UNLABELED,
    CodeBlock,
    LanguageTally,
    extract_code_blocks,
    tally_languages,
    tally_languages_across,
)


def test_extracts_single_labeled_block():
    text = "intro\n\n```python\nprint('hi')\n```\n\nafter"
    (block,) = extract_code_blocks(text)
    assert block.language == "python"
    assert block.info == "python"
    assert block.content == "print('hi')"
    assert block.line_count == 1
    assert block.closed is True


def test_start_and_end_lines_are_one_based():
    text = "line1\n```js\na\nb\n```\n"
    (block,) = extract_code_blocks(text)
    assert block.start_line == 2
    assert block.end_line == 5
    assert block.line_count == 2


def test_language_is_first_token_lowercased():
    text = "```Python title=demo.py\nx = 1\n```\n"
    (block,) = extract_code_blocks(text)
    assert block.language == "python"
    assert block.info == "Python title=demo.py"


def test_unlabeled_block_has_empty_language():
    text = "```\nplain\n```\n"
    (block,) = extract_code_blocks(text)
    assert block.language == UNLABELED
    assert block.info == ""


def test_tilde_and_backtick_fences_both_recognised():
    text = "```bash\necho hi\n```\n\n~~~sql\nSELECT 1;\n~~~\n"
    langs = [b.language for b in extract_code_blocks(text)]
    assert langs == ["bash", "sql"]


def test_tilde_fence_body_may_contain_backticks():
    text = "~~~markdown\nuse ```code``` inline\n~~~\n"
    (block,) = extract_code_blocks(text)
    assert block.language == "markdown"
    assert block.content == "use ```code``` inline"


def test_mismatched_fence_char_does_not_close_block():
    # A ~~~ line inside a ``` block is content, not a close.
    text = "```python\n~~~\nstill code\n```\n"
    (block,) = extract_code_blocks(text)
    assert block.content == "~~~\nstill code"
    assert block.closed is True


def test_backtick_info_string_with_backtick_is_not_a_fence():
    # "``` `x` ```" style: backtick in the info string invalidates the opener.
    text = "``` `bad`\nnot code\n"
    assert extract_code_blocks(text) == []


def test_closing_fence_may_be_longer_than_opener():
    text = "```py\ncode\n`````\n"
    (block,) = extract_code_blocks(text)
    assert block.closed is True
    assert block.content == "code"


def test_shorter_run_does_not_close_block():
    text = "````py\ncode\n```\nmore\n````\n"
    (block,) = extract_code_blocks(text)
    assert block.closed is True
    assert block.content == "code\n```\nmore"


def test_unclosed_fence_runs_to_end_of_file():
    text = "```python\nline one\nline two\n"
    (block,) = extract_code_blocks(text)
    assert block.closed is False
    assert block.line_count == 2
    assert block.end_line == 3


def test_indented_fence_strips_indentation_from_body():
    text = "   ```python\n   indented = 1\n   ```\n"
    (block,) = extract_code_blocks(text)
    assert block.language == "python"
    assert block.content == "indented = 1"


def test_over_indented_fence_is_not_recognised():
    text = "    ```python\n    code\n    ```\n"
    assert extract_code_blocks(text) == []


def test_multiple_blocks_in_order():
    text = "```py\na\n```\ntext\n```js\nb\n```\n"
    blocks = extract_code_blocks(text)
    assert [b.language for b in blocks] == ["py", "js"]


def test_empty_code_block():
    text = "```python\n```\n"
    (block,) = extract_code_blocks(text)
    assert block.content == ""
    assert block.line_count == 0


def test_tally_languages_from_text():
    text = "```py\na\n```\n```py\nb\n```\n```js\nc\n```\n"
    assert tally_languages(text) == {"py": 2, "js": 1}


def test_tally_languages_from_blocks_iterable():
    blocks = extract_code_blocks("```py\na\n```\n```py\nb\n```\n")
    assert tally_languages(blocks) == {"py": 2}


def test_tally_can_exclude_unlabeled():
    text = "```py\na\n```\n```\nplain\n```\n"
    assert tally_languages(text) == {"py": 1, UNLABELED: 1}
    assert tally_languages(text, include_unlabeled=False) == {"py": 1}


def test_tally_across_chapters_totals_and_breakdown():
    chapters = {
        "Chapter1.md": "```py\na\n```\n```js\nb\n```\n",
        "Chapter2.md": "```py\nc\n```\n",
    }
    result = tally_languages_across(chapters)
    assert isinstance(result, LanguageTally)
    assert result.total == {"py": 2, "js": 1}
    assert result.block_count == 3
    assert result.per_chapter["Chapter1.md"] == {"py": 1, "js": 1}
    assert result.per_chapter["Chapter2.md"] == {"py": 1}


def test_tally_across_isolates_unclosed_fences():
    # An unclosed fence in one chapter must not affect another.
    chapters = {
        "a": "```py\nunterminated\n",
        "b": "prose only, no code",
    }
    result = tally_languages_across(chapters)
    assert result.total == {"py": 1}
    assert result.per_chapter["b"] == {}


def test_extract_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_code_blocks(None)


def test_tally_across_rejects_non_mapping():
    with pytest.raises(TypeError, match="mapping"):
        tally_languages_across(["not", "a", "mapping"])


def test_tally_rejects_bad_iterable_items():
    with pytest.raises(TypeError, match="iterable of CodeBlock"):
        tally_languages(["python"])


def test_code_block_is_immutable():
    (block,) = extract_code_blocks("```py\na\n```\n")
    assert isinstance(block, CodeBlock)
    with pytest.raises(AttributeError):
        block.language = "js"
