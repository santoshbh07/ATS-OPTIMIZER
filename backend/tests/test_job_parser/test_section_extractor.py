import pytest

from app.services.job_parsing.section_extractor import (
    JOB_SECTION_ALIASES,
    is_header,
    normalize_header,
    reverse_section_headers,
)


def test_reverse_section_headers_returns_alias_to_canonical_mapping():
    headers = {"requirements": {"minimum qualifications"}}

    assert reverse_section_headers(headers) == {
        "minimum qualifications": "requirements",
    }


def test_reverse_section_headers_reverses_all_aliases_for_one_section():
    headers = {
        "responsibilities": {
            "responsibilities",
            "job duties",
            "what you'll do",
        },
    }

    assert reverse_section_headers(headers) == {
        "responsibilities": "responsibilities",
        "job duties": "responsibilities",
        "what you'll do": "responsibilities",
    }


def test_every_job_section_alias_appears_in_reversed_mapping():
    reversed_headers = reverse_section_headers(JOB_SECTION_ALIASES)

    for aliases in JOB_SECTION_ALIASES.values():
        assert aliases <= reversed_headers.keys()


def test_job_section_aliases_are_unique_across_canonical_sections():
    sections_by_alias: dict[str, set[str]] = {}

    for canonical_section, aliases in JOB_SECTION_ALIASES.items():
        for alias in aliases:
            sections_by_alias.setdefault(alias, set()).add(canonical_section)

    duplicate_aliases = {
        alias: sections
        for alias, sections in sections_by_alias.items()
        if len(sections) > 1
    }
    assert duplicate_aliases == {}


def test_normalize_header_lowercases_headers():
    assert normalize_header("REQUIREMENTS") == "requirements"


def test_normalize_header_strips_leading_and_trailing_whitespace():
    assert normalize_header("  requirements\t") == "requirements"


@pytest.mark.parametrize("bullet", ["-", "*", "•", "▪", "■", "◦", "‣"])
def test_normalize_header_removes_supported_bullet_characters(bullet):
    assert normalize_header(f"{bullet} Requirements") == "requirements"


@pytest.mark.parametrize("punctuation", [":", "|", "•", "-", "–", "—"])
def test_normalize_header_removes_supported_trailing_punctuation(punctuation):
    assert normalize_header(f"Requirements{punctuation}") == "requirements"


def test_normalize_header_handles_empty_strings():
    assert normalize_header("") == ""


def test_normalize_header_leaves_normalized_headers_unchanged():
    assert normalize_header("requirements") == "requirements"


def test_known_header_is_recognized():
    assert is_header("requirements")


def test_header_recognition_is_case_insensitive_after_normalization():
    assert is_header("WhAt YoU BrInG")


def test_header_with_extra_whitespace_is_recognized():
    assert is_header("   minimum qualifications   ")


def test_header_with_bullet_prefix_is_recognized():
    assert is_header("• Key responsibilities")


def test_header_with_supported_punctuation_is_recognized():
    assert is_header("Benefits:")


def test_unknown_header_is_rejected():
    assert not is_header("company values")


def test_job_description_sentence_is_not_mistaken_for_header():
    assert not is_header("You will collaborate with engineers across the company.")


def test_partial_header_text_is_not_accepted():
    assert not is_header("responsibil")


def test_similar_but_unsupported_header_wording_is_rejected():
    assert not is_header("what you should bring")
