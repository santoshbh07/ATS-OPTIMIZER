import pytest

from app.services.resume_parsing.education_parser import detect_gpa


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("GPA: 3.85", "3.85"),
        ("gpa 3.8", "3.8"),
        ("Overall GPA - 3.72", "3.72"),
        ("Cumulative GPA: 3.850", "3.850"),
        ("GPA: 3.85/4.00", "3.85"),
        ("GPA: 4.5/5.0", "4.5"),
        ("GPA: 5.0/5.00", "5.0"),
        ("GPA: 0.0/4.0", "0.0"),
        ("GPA: 8.6 / 10", None),
        ("", None),
        ("Graduated in 2024", None),
        ("3.85 years of experience", None),
        ("GPA: N/A", None),
        ("Major GPA: 3.90", None),
        ("GPA: 4.5/4.0", None),
        ("GPA: 4.1", None),
        ("GPA: 5.1/5.0", None),
        ("GPA: 3.8/10", None),
        ("GPA: -1.0", None),
    ],
)
def test_detect_gpa_supported_and_invalid_formats(line, expected):
    assert detect_gpa(line) == expected


def test_detect_gpa_prefers_cumulative_over_later_major_gpa():
    assert detect_gpa("Cumulative GPA: 3.72 | Major GPA: 3.91") == "3.72"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # Valid unscaled GPA values: 0.0-4.0
        ("GPA: 0", "0"),
        ("GPA: 0.0", "0.0"),
        ("GPA: 2.75", "2.75"),
        ("gpa 3.8", "3.8"),
        ("GPA=3.85", "3.85"),
        ("Overall GPA - 3.72", "3.72"),
        ("Cumulative GPA: 3.850", "3.850"),
        ("Grade Point Average: 4.0", "4.0"),

        # Valid 4-point scale
        ("GPA: 0.0/4.0", "0.0"),
        ("GPA: 3.85/4", "3.85"),
        ("GPA: 3.85 / 4.00", "3.85"),
        ("GPA: 4.0/4.0", "4.0"),

        # Valid 4.3-point scale
        ("Grade Point Average: 4.0/4.3", "4.0"),

        # Valid 5-point scale
        ("GPA: 0.0/5.0", "0.0"),
        ("GPA: 4.0/5", "4.0"),
        ("GPA: 4.5/5.0", "4.5"),
        ("GPA: 5.0/5.00", "5.0"),

        # Score exceeds allowed range
        ("GPA: 4.01", None),
        ("GPA: 5.0", None),
        ("GPA: 4.1/4.0", None),
        ("GPA: 4.5/4.0", None),
        ("GPA: 5.1/5.0", None),
        ("GPA: 8.6/10", None),

        # Unsupported scales
        ("GPA: 3.8/4.5", None),
        ("GPA: 3.8/6.0", None),
        ("GPA: 3.8/10", None),

        # Invalid or missing values
        ("GPA: -1.0", None),
        ("GPA: N/A", None),
        ("GPA:", None),
        ("GPA: five", None),
        ("", None),

        # Missing or excluded GPA context
        ("3.85", None),
        ("3.85 years of experience", None),
        ("Graduated in 2024", None),
        ("Major GPA: 3.90", None),
    ],
)
def test_detect_gpa_ranges_and_scales(line, expected):
    assert detect_gpa(line) == expected
