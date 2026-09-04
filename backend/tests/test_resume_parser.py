from pathlib import Path

import pytest

from app.services.resume_parsing import resume_parser


def test_parse_resume_file_includes_projects(monkeypatch):
    monkeypatch.setattr(resume_parser, "extract_text", lambda _: "resume")
    monkeypatch.setattr(
        resume_parser,
        "extract_sections",
        lambda _: {
            "projects": [
                "ATS Optimizer | Python",
                "• Built a resume parser.",
            ],
        },
    )

    result = resume_parser.parse_resume_file(Path("resume.pdf"))

    assert result["projects"][0]["name"] == "ATS Optimizer"
    assert result["projects"][0]["technologies"] == ["Python"]
    assert result["projects"][0]["descriptions"] == [
        "Built a resume parser.",
    ]


def test_parse_resume_file_includes_experience(monkeypatch):
    monkeypatch.setattr(resume_parser, "extract_text", lambda _: "resume")
    monkeypatch.setattr(
        resume_parser,
        "extract_sections",
        lambda _: {
            "experience": [
                "Acme Corp, Austin, TX | Jan 2023 - Present",
                "Software Engineer",
                "\u2022 Built internal APIs.",
            ],
        },
    )

    result = resume_parser.parse_resume_file(Path("resume.pdf"))

    assert result["experience"][0]["company"] == "Acme Corp"
    assert result["experience"][0]["position"] == "Software Engineer"
    assert result["experience"][0]["location"] == "Austin, TX"
    assert result["experience"][0]["is_current"] is True
    assert result["experience"][0]["descriptions"] == [
        "Built internal APIs.",
    ]


def test_parse_resume_file_includes_deduplicated_certifications(monkeypatch):
    monkeypatch.setattr(resume_parser, "extract_text", lambda _: "resume")
    monkeypatch.setattr(
        resume_parser,
        "extract_sections",
        lambda _: {
            "education": [
                "Example University",
                "Bachelor of Science in Computer Science",
                "AWS Certified Cloud Practitioner",
            ],
            "certifications": [
                "AWS Certified Cloud Practitioner",
                "Issued by: Amazon Web Services",
            ],
        },
    )

    result = resume_parser.parse_resume_file(Path("resume.pdf"))

    assert len(result["certifications"]) == 1
    assert result["certifications"][0]["name"] == (
        "AWS Certified Cloud Practitioner"
    )
    assert result["certifications"][0]["issuer"] == "Amazon Web Services"


def test_parse_resume_file_rejects_document_without_readable_text(monkeypatch):
    monkeypatch.setattr(resume_parser, "extract_text", lambda _: "   ")

    with pytest.raises(ValueError, match="No readable text"):
        resume_parser.parse_resume_file(Path("resume.pdf"))


def test_parse_resume_file_rejects_document_without_supported_content(monkeypatch):
    monkeypatch.setattr(resume_parser, "extract_text", lambda _: "Candidate Name")
    monkeypatch.setattr(resume_parser, "extract_sections", lambda _: {})

    with pytest.raises(ValueError, match="No supported resume sections"):
        resume_parser.parse_resume_file(Path("resume.pdf"))
