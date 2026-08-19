import pytest

from app.services.resume_parsing.education_parser import (
    detect_institution,
    detect_location,
    split_institution_and_location,
)


def test_detects_separate_city_and_state_location():
    entry = [
        "University of North Texas",
        "Denton, TX",
        "Bachelor of Science in Computer Science",
    ]

    assert detect_location(entry) == "Denton, TX"


def test_splits_institution_and_location_separated_by_comma():
    result = split_institution_and_location(
        "University of North Texas, Denton, TX"
    )

    assert result == ("University of North Texas", "Denton, TX")


def test_splits_institution_and_location_separated_by_pipe():
    result = split_institution_and_location(
        "Butler Community College | El Dorado, KS"
    )

    assert result == ("Butler Community College", "El Dorado, KS")


def test_splits_institution_and_location_separated_by_dash():
    result = split_institution_and_location(
        "Texas A&M University \u2014 College Station, Texas"
    )

    assert result == ("Texas A&M University", "College Station, Texas")


def test_detects_international_location():
    entry = ["Kathmandu University, Dhulikhel, Nepal"]

    assert detect_location(entry) == "Dhulikhel, Nepal"


def test_splits_canadian_city_and_province_location():
    line = "Concordia University, Montreal, Quebec"

    assert split_institution_and_location(line) == (
        "Concordia University",
        "Montreal, Quebec",
    )
    assert detect_institution(line) == "Concordia University"
    assert detect_location([line]) == "Montreal, Quebec"


@pytest.mark.parametrize(
    ("line", "expected_institution", "expected_location"),
    [
        (
            "University of Pittsburgh, Pittsburgh PA",
            "University of Pittsburgh",
            "Pittsburgh PA",
        ),
        (
            "University of Pittsburgh | Pittsburgh PA",
            "University of Pittsburgh",
            "Pittsburgh PA",
        ),
        (
            "Texas A&M University, College Station TX",
            "Texas A&M University",
            "College Station TX",
        ),
        (
            "Washington University, St. Louis MO",
            "Washington University",
            "St. Louis MO",
        ),
        (
            "Wake Forest University, Winston-Salem NC",
            "Wake Forest University",
            "Winston-Salem NC",
        ),
        (
            "University of Pittsburgh, Pittsburgh Pennsylvania",
            "University of Pittsburgh",
            "Pittsburgh Pennsylvania",
        ),
        (
            "University of Oxford, Oxford United Kingdom",
            "University of Oxford",
            "Oxford United Kingdom",
        ),
        (
            "Kathmandu University, Dhulikhel Nepal",
            "Kathmandu University",
            "Dhulikhel Nepal",
        ),
        (
            "University of Pittsburgh, Pittsburgh PA 15260",
            "University of Pittsburgh",
            "Pittsburgh PA 15260",
        ),
        (
            "University of Pittsburgh (Pittsburgh, PA)",
            "University of Pittsburgh",
            "Pittsburgh, PA",
        ),
        (
            "Example University, University City MO",
            "Example University",
            "University City MO",
        ),
    ],
)
def test_splits_locations_without_city_region_comma(
    line,
    expected_institution,
    expected_location,
):
    assert split_institution_and_location(line) == (
        expected_institution,
        expected_location,
    )
    assert detect_institution(line) == expected_institution
    assert detect_location([line]) == expected_location


@pytest.mark.parametrize(
    "line",
    [
        "Pittsburgh PA",
        "College Station TX",
        "St. Louis MO",
        "Winston-Salem NC",
        "Pittsburgh Pennsylvania",
        "Oxford United Kingdom",
        "Dhulikhel Nepal",
        "Pittsburgh PA 15260",
        "Pittsburgh PA.",
    ],
)
def test_detects_standalone_locations_without_commas(line):
    assert detect_location([line]) == line


@pytest.mark.parametrize(
    "line",
    [
        "Bachelor of Science, Computer Science",
        "Bachelor of Arts in Washington",
        "University of Pennsylvania",
        "College of Engineering",
    ],
)
def test_does_not_treat_academic_lines_as_locations(line):
    assert detect_location([line]) is None


def test_preserves_line_when_location_split_is_uncertain():
    line = "University of North Texas, School of Engineering"

    assert split_institution_and_location(line) == (line, None)
