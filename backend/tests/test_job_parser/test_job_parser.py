import pytest

from app.services.job_parsing import parse_job_description


def test_parse_job_description_combines_all_parser_outputs():
    result = parse_job_description(
        """
        Backend Engineer
        Example Labs
        Austin, TX
        Full-time
        Compensation: $120,000 - $150,000 per year

        Requirements
        - 3+ years of Python experience
        Preferred Qualifications: AWS certification

        Responsibilities
        - Build reliable APIs
        - Collaborate with engineers
        """
    )

    assert result["metadata"] == {
        "job_title": "Backend Engineer",
        "company": "Example Labs",
        "location": "Austin, TX",
        "employment_type": "Full-time",
        "salary": "$120,000 - $150,000 per year",
    }
    assert result["requirements"] == [
        {
            "text": "3+ years of Python experience",
            "category": "experience",
            "is_preferred": False,
        },
        {
            "text": "AWS certification",
            "category": "certification",
            "is_preferred": True,
        },
    ]
    assert result["responsibilities"] == [
        "Build reliable APIs",
        "Collaborate with engineers",
    ]


def test_parse_job_description_handles_unsectioned_posting():
    result = parse_job_description(
        """
        Software Engineer
        Example Corp
        Remote
        Applicants must know Python.
        You will build reliable APIs.
        """
    )

    assert result["metadata"]["job_title"] == "Software Engineer"
    assert result["metadata"]["company"] == "Example Corp"
    assert result["metadata"]["location"] == "Remote"
    assert len(result["requirements"]) == 1
    assert result["responsibilities"] == ["You will build reliable APIs."]


@pytest.mark.parametrize("value", ["", "   "])
def test_parse_job_description_rejects_empty_text(value):
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_job_description(value)
