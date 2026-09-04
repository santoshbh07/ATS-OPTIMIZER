import pytest

from app.services.resume_parsing.certification_parser import (
    parse_certification_entry,
    parse_certifications,
)


def test_parse_certification_entry_extracts_structured_metadata():
    record = parse_certification_entry(
        [
            "AWS Certified Cloud Practitioner | Amazon Web Services",
            "Issued Jan 2024 | Expires Jan 2027",
            "Credential ID: ABC-123",
            "https://example.com/verify/ABC-123",
        ]
    )

    assert record.name == "AWS Certified Cloud Practitioner"
    assert record.issuer == "Amazon Web Services"
    assert record.issue_date is not None
    assert record.issue_date.year == 2024
    assert record.issue_date.month == 1
    assert record.expiration_date is not None
    assert record.expiration_date.year == 2027
    assert record.credential_id == "ABC-123"
    assert record.credential_url == "https://example.com/verify/ABC-123"


def test_parse_certifications_handles_wrapped_entries_and_deduplicates():
    records = parse_certifications(
        [
            "• CompTIA Security+",
            "CompTIA",
            "Issued: June 2025",
            "CompTIA Security+",
        ]
    )

    assert len(records) == 1
    assert records[0].name == "CompTIA Security+"
    assert records[0].issuer == "CompTIA"
    assert records[0].issue_date is not None
    assert records[0].issue_date.year == 2025


def test_parse_certifications_can_scan_mixed_education_section():
    records = parse_certifications(
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "AWS Certified Cloud Practitioner",
            "Issued by: Amazon Web Services",
        ],
        require_marker=True,
    )

    assert [record.name for record in records] == [
        "AWS Certified Cloud Practitioner"
    ]
    assert records[0].issuer == "Amazon Web Services"


def test_parse_certifications_rejects_non_string_lines():
    with pytest.raises(TypeError, match="must be strings"):
        parse_certifications(["AWS Certified Developer", 123])  # type: ignore[list-item]


def test_parse_certification_entry_rejects_empty_input():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_certification_entry([])
