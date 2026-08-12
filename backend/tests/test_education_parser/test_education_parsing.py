import pytest

from app.services.parser.date_parser import NormalizedDate
from app.services.parser.education_parser import parse_degree_entry, parse_education


def test_parse_degree_entry_stores_detected_location():
    record = parse_degree_entry(
        [
            "University of North Texas, Denton, TX",
            "Bachelor of Science in Computer Science",
        ]
    )

    assert record.institution == "University of North Texas"
    assert record.location == "Denton, TX"


def test_parse_degree_entry_cleans_inline_expected_date_metadata():
    line = (
        "University of North Texas (UNT) - Denton, TX\t"
        "Expected May 2029"
    )

    record = parse_degree_entry([line])

    assert record.institution == "University of North Texas (UNT)"
    assert record.location == "Denton, TX"
    assert record.start_date is None
    assert record.end_date == NormalizedDate(year=2029, month=5)
    assert record.is_expected is True


def test_parse_degree_entry_populates_field_without_changing_other_fields():
    lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Expected May 2027",
    ]

    record = parse_degree_entry(lines)

    assert record.institution == "University of North Texas"
    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]

    assert record.start_date is None

    assert record.end_date is not None
    assert record.end_date.year == 2027
    assert record.end_date.month == 5

    assert record.gpa is None
    assert record.raw_lines == lines

    assert record.is_expected is True
    assert record.is_current is False


def test_parse_degree_entry_populates_gpa_and_minors():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Minor in Mathematics",
        "GPA: 3.82/4.00",
        "Expected May 2027",
    ]

    record = parse_degree_entry(education_lines)

    assert record.institution == "University of North Texas"
    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]
    assert record.minors == ["Mathematics"]
    assert record.gpa == "3.82"
    assert record.raw_lines == education_lines


def test_parse_degree_entry_stores_multiple_fields():
    lines = [
        "University of North Texas",
        "Bachelor of Science",
        "Double Major: Computer Science and Mathematics",
    ]

    record = parse_degree_entry(lines)

    assert record.fields_of_study == [
        "Computer Science",
        "Mathematics",
    ]


def test_parse_education_returns_degree_records():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "GPA: 3.82",
    ]

    records = parse_education(education_lines)

    assert len(records) == 1
    assert records[0].institution == "University of North Texas"
    assert records[0].degree_name == "Bachelor of Science"
    assert records[0].fields_of_study == ["Computer Science"]
    assert records[0].gpa == "3.82"


def test_parse_degree_entry_without_date_keeps_date_fields_empty():
    entry_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.start_date is None
    assert record.end_date is None
    assert record.is_expected is False
    assert record.is_current is False


def test_parse_degree_entry_without_institution_keeps_institution_none():
    entry_lines = [
        "Bachelor of Science in Computer Science",
        "Expected Graduation: May 2026",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.institution is None


def test_parse_degree_entry_without_institution_parses_remaining_fields():
    entry_lines = [
        "Bachelor of Science in Computer Science",
        "Expected Graduation: May 2026",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.institution is None

    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]

    assert record.end_date is not None
    assert record.end_date.year == 2026
    assert record.end_date.month == 5
    assert record.is_expected is True

    assert record.gpa == "3.66"


def test_parse_degree_entry_collects_field_and_specialization():
    record = parse_degree_entry(
        [
            "Example University",
            "Bachelor of Science in Geology",
            "Concentration: Computational Biology",
        ]
    )

    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Geology"]
    assert record.specializations == [
        "Computational Biology",
    ]


def test_expected_marker_modifies_attached_education_range():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "Sep 2022 - May 2026 (Expected)",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True
    assert record.is_current is False


def test_education_range_wins_over_isolated_graduation_date():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Expected May 2026",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True


def test_expected_marker_does_not_modify_unrelated_range():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Expected May 2027",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is False


@pytest.mark.parametrize(
    "line",
    [
        "Expected May 2026",
        "Expected Graduation: May 2026",
        "Anticipated May 2026",
        "May 2026 (Expected)",
    ],
)
def test_expected_marker_applies_to_isolated_graduation_date(line):
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            line,
        ]
    )

    assert record.start_date is None
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True


def test_education_prefers_range_even_when_single_date_appears_first():
    record = parse_degree_entry(
        [
            "May 2026",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
