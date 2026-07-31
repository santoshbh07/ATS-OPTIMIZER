import pytest

from app.services.parser.education_parser import detect_degree


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("", None),
        ("   ", None),
        ("Bachelor of Science in Computer Science", ("Bachelor of Science", "bachelor")),
        ("associate OF arts", ("Associate of Arts", "associate")),
        ("B.S. Computer Science, May 2026", ("Bachelor of Science", "bachelor")),
        ("University of North Texas | BS Computer Science | May 2026", ("Bachelor of Science", "bachelor")),
        ("M S in Mathematics, GPA: 3.9", ("Master of Science", "master")),
        ("B.Sc. Information Technology", ("Bachelor of Science", "bachelor")),
        ("MSc Data Science", ("Master of Science", "master")),
        ("Ph.D. in Computer Science", ("Doctor of Philosophy", "doctorate")),
        ("EdD Education Leadership", ("Doctor of Education", "doctorate")),
        ("High School Diploma, 2022", ("High School Diploma", "high_school")),
        ("GED", ("GED", "high_school")),
        ("Bachelor's Degree in Information Technology", ("Bachelor's Degree", "bachelor")),
        ("Bachelors Degree", ("Bachelor's Degree", "bachelor")),
        ("Masters Degree", ("Master's Degree", "master")),
        ("Associate Degree", ("Associate Degree", "associate")),
        ("Expected Bachelor of Arts, May 2027", ("Bachelor of Arts", "bachelor")),
        ("Pursuing a Bachelor of Engineering", ("Bachelor of Engineering", "bachelor")),
        ("Candidate for a Master of Business Administration", ("Master of Business Administration", "master")),
        ("Bachelor of Business Administration / Bachelor's Degree", ("Bachelor of Business Administration", "bachelor")),
    ],
)
def test_detect_degree_supported_formats(line, expected):
    assert detect_degree(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "Business management experience",
        "Mastered Python and SQL",
        "Worked as a teaching assistant",
        "Mathematics Department",
        "Basic programming knowledge",
        "University of North Texas",
        "Computer Science Department",
    ],
)
def test_detect_degree_avoids_false_positives(line):
    assert detect_degree(line) is None
