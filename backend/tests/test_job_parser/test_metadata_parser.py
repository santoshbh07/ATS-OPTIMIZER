import pytest

from app.services.job_parsing.metadata_parser import (
    _looks_like_location,
    parse_metadata,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Denton, TX", True),
        ("Denton TX", True),
        ("Denton, Texas", True),
        ("Denton, TX 76201", True),
        ("Denton, TX 76201-1234", True),
        ("Toronto, ON", True),
        ("Toronto, Ontario", True),
        ("London, United Kingdom", True),
        ("London, UK", True),
        ("New York, NY, USA", True),
        ("New York, NY", True),
        ("St. Louis, MO", True),
        ("Winston-Salem, NC", True),
        ("Software Engineer", False),
        ("Texas", False),
        ("United States", False),
        ("", False),
        ("Remote", False),
        ("Engineering Team, Texas", True),
    ],
)
def test_looks_like_location(value: str, expected: bool):
    assert _looks_like_location(value) is expected


def test_parse_metadata_reads_labelled_fields():
    metadata = parse_metadata(
        """
        Job Title: Backend Engineer
        Company: Example Labs
        Location: Remote
        Employment Type: Full Time
        Salary: $120,000 - $150,000 per year
        """
    )

    assert metadata.job_title == "Backend Engineer"
    assert metadata.company == "Example Labs"
    assert metadata.location == "Remote"
    assert metadata.employment_type == "Full-time"
    assert metadata.salary == "$120,000 - $150,000 per year"


def test_parse_metadata_uses_common_unlabelled_preamble_layout():
    metadata = parse_metadata(
        """
        Software Engineer
        Example Corp
        Denton, TX
        Full-time

        Responsibilities
        Build reliable services.
        """
    )

    assert metadata.job_title == "Software Engineer"
    assert metadata.company == "Example Corp"
    assert metadata.location == "Denton, TX"
    assert metadata.employment_type == "Full-time"


def test_location_detector_does_not_treat_lowercase_state_code_as_location():
    assert not _looks_like_location("Based in")


def test_labelled_title_allows_unlabelled_company_name():
    metadata = parse_metadata(
        "Title: Software Engineer\nAcme\nRequirements: Python"
    )

    assert metadata.job_title == "Software Engineer"
    assert metadata.company == "Acme"
