import pytest

from app.services.parser.date_parser import (
    NormalizedDate,
    detect_date_candidates,
)


@pytest.mark.parametrize(
    "line",
    [
        "Python 3/11",
        "Version 3/11",
        "Score: 3/11",
        "Course CS 3/11",
        "https://example.com/releases/3/11",
        "3/11 - 5/12",
        "03/22 - Present",
    ],
)
def test_rejects_two_digit_numeric_dates(line):
    assert detect_date_candidates(line) == []


def test_detects_four_digit_numeric_month_year():
    candidates = detect_date_candidates("03/2022")

    assert len(candidates) == 1
    assert candidates[0].start_date == NormalizedDate(
        year=2022,
        month=3,
    )
    assert candidates[0].end_date is None
    assert candidates[0].is_current is False


def test_detects_four_digit_numeric_range():
    candidates = detect_date_candidates("03/2022 - 05/2026")

    assert len(candidates) == 1
    assert candidates[0].start_date == NormalizedDate(
        year=2022,
        month=3,
    )
    assert candidates[0].end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert candidates[0].is_current is False


def test_detects_four_digit_numeric_open_range():
    candidates = detect_date_candidates("03/2022 - Present")

    assert len(candidates) == 1
    assert candidates[0].start_date == NormalizedDate(
        year=2022,
        month=3,
    )
    assert candidates[0].end_date is None
    assert candidates[0].is_current is True


def test_named_month_formats_can_still_use_two_digit_years():
    candidates = detect_date_candidates("Sep 22 - May 26")

    assert len(candidates) == 1
    assert candidates[0].start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert candidates[0].end_date == NormalizedDate(
        year=2026,
        month=5,
    )


def test_detector_returns_date_without_interpreting_expected_marker():
    candidates = detect_date_candidates(
        "Sep 2022 - May 2026 (Expected)"
    )

    assert len(candidates) == 1
    assert candidates[0].start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert candidates[0].end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert not hasattr(candidates[0], "is_expected")