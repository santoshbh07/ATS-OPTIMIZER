import pytest

from app.services.parser.education_parser import detect_minors


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Minor in Mathematics", ["Mathematics"]),
        ("Minor: Psychology", ["Psychology"]),
        ("Mathematics Minor", ["Mathematics"]),
        ("B.S. in Computer Science, Minor in Statistics", ["Statistics"]),
        ("Minors in Mathematics and Physics", ["Mathematics", "Physics"]),
        ("Minors: Finance, Economics", ["Finance", "Economics"]),
        ("Double Minor: Mathematics; Statistics", ["Mathematics", "Statistics"]),
        ("Minor in Comp Sci", ["Computer Science"]),
        ("Minor: Business Admin", ["Business Administration"]),
        ("Minor in Humanitarian Studies", ["Humanitarian Studies"]),
        ("Humanitarian Studies Minor", ["Humanitarian Studies"]),
        ("Minor in Mathematics, GPA: 3.85", ["Mathematics"]),
        (
            "Minors in Mathematics and Physics | Expected May 2027",
            ["Mathematics", "Physics"],
        ),
        ("Minors: Mathematics, Math", ["Mathematics"]),
    ],
)
def test_detect_minors_supported_formats(line, expected):
    assert detect_minors(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "University of North Texas",
        "Mathematics and Physics",
        "Relevant Coursework: Mathematics and Physics",
        "Played a minor role in the project",
        "Minor formatting changes",
        "Students who are minors",
        "No Minor Declared",
        "Minor: None",
    ],
)
def test_detect_minors_rejects_invalid_lines(line):
    assert detect_minors(line) == []
