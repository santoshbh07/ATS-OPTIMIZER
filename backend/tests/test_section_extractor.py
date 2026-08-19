from app.services.resume_text_extractor.section_extractor import (
    extract_sections,
    find_header_loc,
)


def test_extract_sections_detects_multiple_sections():
    resume_text = """
    EDUCATION
    University of North Texas
    Bachelor of Science in Computer Science

    SKILLS
    Python, FastAPI, PostgreSQL
    """

    result = extract_sections(resume_text)

    assert result == {
        "education": [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
        ],
        "skills": [
            "Python, FastAPI, PostgreSQL",
        ],
    }


def test_extract_sections_returns_empty_dictionary_without_headers():
    resume_text = """
    Santosh
    Computer Science Student
    Python and FastAPI Developer
    """

    assert extract_sections(resume_text) == {}


def test_extract_sections_handles_repeated_section_headers():
    resume_text = """
    EXPERIENCE
    Software Intern
    ABC Company

    EXPERIENCE
    Teaching Assistant
    XYZ School
    """

    result = extract_sections(resume_text)

    assert result["experience"] == [
        "Software Intern",
        "ABC Company",
        "Teaching Assistant",
        "XYZ School",
    ]


def test_find_header_loc_returns_header_positions():
    resume_text = """
    EDUCATION
    University of North Texas

    SKILLS
    Python
    """

    headers, positions = find_header_loc(resume_text)

    assert headers == {
        "education": [0],
        "skills": [2],
    }
    assert positions == [0, 2]


def test_memberships_affiliations_heading_ends_experience_section():
    resume_text = """
    EXPERIENCE
    Software Engineer
    Acme Corp

    MEMBERSHIPS/AFFILIATIONS
    Association for Computing Machinery
    """

    result = extract_sections(resume_text)

    assert result["experience"] == [
        "Software Engineer",
        "Acme Corp",
    ]
    assert result["activities"] == [
        "Association for Computing Machinery",
    ]
