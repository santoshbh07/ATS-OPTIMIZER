import pytest

from app.services.resume_parsing.skill_parser import (
    clean_skill_candidate,
    parse_skills,
    split_skill_candidates,
)


def names(result):
    return [skill.name for skill in result.skills]


def test_parses_category_prefixed_skills():
    result = parse_skills(["Programming Languages: Python, Java, C++"])
    assert names(result) == ["Python", "Java", "C++"]
    assert {skill.category for skill in result.skills} == {"programming_languages"}


def test_parses_uncategorized_skill_line():
    result = parse_skills(["Python, Java, SQL"])
    assert names(result) == ["Python", "Java", "SQL"]
    assert all(skill.category is None for skill in result.skills)


def test_inherits_category_from_previous_line():
    result = parse_skills(["Frameworks", "FastAPI, Django"])
    assert names(result) == ["FastAPI", "Django"]
    assert all(skill.category == "frameworks" for skill in result.skills)


def test_switches_category_when_new_category_is_found():
    result = parse_skills(["Frameworks", "Django", "Databases", "PostgreSQL"])
    assert [skill.category for skill in result.skills] == ["frameworks", "databases"]


def test_software_category_uses_normalized_identifier():
    result = parse_skills(["Software: Excel, Tableau"])

    assert [skill.category for skill in result.skills] == ["software", "software"]


def test_preserves_cpp_csharp_and_dotnet():
    assert names(parse_skills(["C++, C#, .NET"])) == ["C++", "C#", ".NET"]


def test_preserves_slash_based_skill_names():
    assert names(parse_skills(["CI/CD, UI/UX, TCP/IP"])) == [
        "CI/CD",
        "UI/UX",
        "TCP/IP",
    ]


def test_does_not_split_scikit_learn_on_hyphen():
    assert names(parse_skills(["scikit-learn"])) == ["scikit-learn"]


def test_splits_common_skill_delimiters():
    assert split_skill_candidates("Python, Java; SQL | Git • Docker · AWS ▪ Azure ● GCP") == [
        "Python",
        "Java",
        "SQL",
        "Git",
        "Docker",
        "AWS",
        "Azure",
        "GCP",
    ]


def test_splits_slash_only_when_surrounded_by_spaces():
    assert split_skill_candidates("Python / Java / C++") == ["Python", "Java", "C++"]
    assert split_skill_candidates("CI/CD") == ["CI/CD"]


def test_does_not_split_commas_inside_parentheses():
    assert split_skill_candidates("Python (Pandas, NumPy), Java, C++") == [
        "Python (Pandas, NumPy)",
        "Java",
        "C++",
    ]


@pytest.mark.parametrize("bullet", ["•", "▪", "●", "◦", "‣", "-"])
def test_removes_leading_bullets(bullet):
    assert names(parse_skills([f"{bullet} Python"])) == ["Python"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Python - Advanced", "Python"),
        ("Java - Intermediate", "Java"),
        ("SQL (Proficient)", "SQL"),
        ("React: Beginner", "React"),
        ("AWS - Familiar", "AWS"),
    ],
)
def test_removes_known_proficiency_suffixes(value, expected):
    assert clean_skill_candidate(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("Python - 3 years", "Python"), ("Java (2+ years)", "Java"), ("SQL: 4 yrs", "SQL")],
)
def test_removes_years_of_experience_suffixes(value, expected):
    assert clean_skill_candidate(value) == expected


def test_preserves_unknown_dash_suffix():
    assert clean_skill_candidate("Python - data engineering") == "Python - data engineering"


def test_deduplicates_case_insensitively():
    assert names(parse_skills(["Python, python, PYTHON"])) == ["Python"]


def test_returns_empty_result_for_empty_input():
    result = parse_skills([])
    assert result.skills == []
    assert result.raw_lines == []


def test_ignores_blank_lines():
    assert names(parse_skills(["", "   ", "Python"])) == ["Python"]


def test_ignores_skill_section_header():
    assert names(parse_skills(["Skills", "Python"])) == ["Python"]


def test_does_not_create_record_for_empty_category():
    assert parse_skills(["Databases:"]).skills == []


def test_handles_unbalanced_parentheses_without_crashing():
    assert names(parse_skills(["Python (Pandas, NumPy, Java"])) == [
        "Python (Pandas, NumPy, Java"
    ]


def test_unknown_category_does_not_crash():
    assert names(parse_skills(["Specialties: Python, Java"])) == [
        "Specialties: Python",
        "Java",
    ]


@pytest.mark.parametrize(
    "metadata",
    [
        "5 years of experience",
        "Available immediately",
        "Open to relocation",
        "US Citizen",
        "Authorized to work in the US",
    ],
)
def test_rejects_obvious_non_skill_metadata(metadata):
    assert parse_skills([metadata]).skills == []


def test_uses_languages_for_spoken_languages():
    result = parse_skills(["Languages: English, Spanish"])
    assert all(skill.category == "spoken_languages" for skill in result.skills)


def test_supports_qualified_category_labels_and_raw_text():
    lines = ["Databases (Relational): PostgreSQL, MySQL"]
    result = parse_skills(lines)
    assert names(result) == ["PostgreSQL", "MySQL"]
    assert result.skills[0].raw_text == "PostgreSQL"
    assert result.raw_lines == lines
    assert result.raw_lines is not lines


def test_none_is_not_accepted():
    with pytest.raises(TypeError):
        parse_skills(None)
