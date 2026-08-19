import pytest

from app.services.resume_parsing.education_parser import detect_study_fields


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "Bachelor of Science in Computer Science",
            ["Computer Science"],
        ),
        (
            "Bachelor of Arts in Psychology",
            ["Psychology"],
        ),
        (
            "Master of Science in Data Science",
            ["Data Science"],
        ),
        (
            "B.S. in Software Engineering",
            ["Software Engineering"],
        ),
        (
            "B.S., Computer Science",
            ["Computer Science"],
        ),
        (
            "MBA in Finance",
            ["Finance"],
        ),
        (
            "Computer Science, Bachelor of Science",
            ["Computer Science"],
        ),
        (
            "Mechanical Engineering (B.S.)",
            ["Mechanical Engineering"],
        ),
        (
            "Major: Computer Science",
            ["Computer Science"],
        ),
        (
            "Major in Mathematics",
            ["Mathematics"],
        ),
        (
            "Field of Study: Information Technology",
            ["Information Technology"],
        ),
        (
            "Program: Data Analytics",
            ["Data Analytics"],
        ),
        (
            "B.S. in Computer Science, Minor in Mathematics",
            ["Computer Science"],
        ),
        (
            "Bachelor of Arts in Psychology, GPA: 3.80",
            ["Psychology"],
        ),
        (
            "Bachelor of Science in Computer Science GPA: 3.66",
            ["Computer Science"],
        ),
        (
            "B.S., Data Science, Expected May 2027",
            ["Data Science"],
        ),
        (
            "Major: Comp Sci",
            ["Computer Science"],
        ),
        (
            "B.S. in Computer Sciences",
            ["Computer Science"],
        ),
        (
            "Field of Study: Business Admin",
            ["Business Administration"],
        ),
        (
            "Major: CS",
            ["Computer Science"],
        ),
        (
            "B.S. in CS",
            ["Computer Science"],
        ),
        (
            "Field of Study: IT",
            ["Information Technology"],
        ),
    ],
)
def test_detect_study_fields_supported_formats(line, expected):
    assert detect_study_fields(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "University of North Texas",
        "Denton, TX",
        "May 2027",
        "Expected Graduation: May 2027",
        "GPA: 3.85",
        "Dean's List",
        "College of Engineering",
        "School of Computer Science",
        "Department of Mathematics",
        "Relevant Coursework: Algorithms and Databases",
        "Bachelor of Science",
        "Master of Science",
        "Associate of Arts",
        "IT Support Assistant",
        "Worked with IS systems",
        "Business management experience",
    ],
)
def test_detect_study_fields_avoids_false_positives(line):
    assert detect_study_fields(line) == []


def test_detect_study_fields_returns_both_double_majors():
    result = detect_study_fields(
        "Double Major: Computer Science and Mathematics"
    )

    assert result == [
        "Computer Science",
        "Mathematics",
    ]


def test_detect_study_fields_returns_multiple_degree_adjacent_fields():
    result = detect_study_fields(
        "Bachelor of Science in Computer Science and Mathematics"
    )

    assert result == [
        "Computer Science",
        "Mathematics",
    ]


def test_detect_study_fields_prefers_longest_alias():
    result = detect_study_fields(
        "Major: Management Information Systems"
    )

    assert result == [
        "Management Information Systems",
    ]


def test_detect_study_fields_deduplicates_fields():
    result = detect_study_fields(
        "Double Major: Computer Science and Computer Science"
    )

    assert result == [
        "Computer Science",
    ]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # Unknown fields in strong academic contexts
        (
            "Bachelor of Science in Geology",
            ["Geology"],
        ),
        (
            "Major: Marine Biology",
            ["Marine Biology"],
        ),
        (
            "Field of Study: Urban Planning",
            ["Urban Planning"],
        ),
        (
            "Program in Game Design",
            ["Game Design"],
        ),
        (
            "Concentration: Computational Biology",
            [],
        ),
        (
            "Bachelor of Arts in Peace and Conflict Studies",
            ["Peace and Conflict Studies"],
        ),

        # Known aliases and abbreviations
        (
            "B.S., Computer Science",
            ["Computer Science"],
        ),
        (
            "Major: CS",
            ["Computer Science"],
        ),
        (
            "Field of Study: Business Admin",
            ["Business Administration"],
        ),

        # Multiple fields
        (
            "Double Major: Computer Science and Mathematics",
            ["Computer Science", "Mathematics"],
        ),
        (
            "Double Major: Geology and Anthropology",
            ["Geology", "Anthropology"],
        ),

        # Embedded engineering fields
        (
            "Bachelor of Civil and Environmental Engineering",
            ["Civil and Environmental Engineering"],
        ),
        (
            "Master of Building Engineering",
            ["Building Engineering"],
        ),

        # Metadata trimming
        (
            "Bachelor of Science in Geology, GPA: 3.8",
            ["Geology"],
        ),
        (
            "Bachelor of Science in Geology, Minor in Mathematics",
            ["Geology"],
        ),

        # No field
        (
            "Bachelor of Science",
            [],
        ),
    ],
)
def test_detect_study_fields(line, expected):
    assert detect_study_fields(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "Geology Club Member",
        "Interested in Geology",
        "Department of Geology",
        "Coursework: Geology",
        "Relevant Coursework: Geology",
        "School of Environmental Science",
        "University Department of Anthropology",
    ],
)
def test_study_fields_require_strong_academic_context(line):
    assert detect_study_fields(line) == []
