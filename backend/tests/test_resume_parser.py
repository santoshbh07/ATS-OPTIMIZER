from pathlib import Path

from app.services import resume_parser


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
