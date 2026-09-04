import pytest
from pydantic import ValidationError

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.job import JobDescription
from app.schemas.resume import Resume
from app.services.job_parsing import parse_job_description


def test_job_schema_accepts_job_parser_output():
    parsed_job = parse_job_description(
        """
        Software Engineer
        Example Corp
        Austin, TX
        Requirements: Python
        Responsibilities: Build APIs
        """
    )

    job = JobDescription.model_validate(parsed_job)

    assert job.metadata.job_title == "Software Engineer"
    assert job.requirements[0].category == "skill"
    assert job.responsibilities == ["Build APIs"]


def test_resume_schema_accepts_resume_parser_shape():
    resume = Resume.model_validate(
        {
            "education": [
                {
                    "institution": "Example University",
                    "degree_name": "Bachelor of Science",
                    "degree_level": "bachelor",
                    "end_date": {"year": 2026, "month": 5, "season": None},
                    "fields_of_study": ["Computer Science"],
                }
            ],
            "skills": [{"name": "Python", "category": "programming_languages"}],
            "projects": [{"name": "ATS Optimizer", "technologies": ["Python"]}],
            "experience": [
                {
                    "company": "Example Corp",
                    "position": "Software Engineer",
                    "descriptions": ["Built APIs"],
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Cloud Practitioner",
                    "issuer": "Amazon Web Services",
                }
            ],
        }
    )

    assert resume.education[0].end_date.year == 2026
    assert resume.skills[0].name == "Python"
    assert resume.projects[0].technologies == ["Python"]
    assert resume.experience[0].position == "Software Engineer"
    assert resume.certifications[0].issuer == "Amazon Web Services"


def test_analysis_request_uses_parsed_objects_without_database_ids():
    request = AnalysisRequest(
        resume={"skills": [{"name": "Python"}]},
        job={
            "requirements": [
                {
                    "text": "Python",
                    "category": "skill",
                    "is_preferred": False,
                }
            ]
        },
    )

    assert request.resume.skills[0].name == "Python"
    assert request.job.requirements[0].text == "Python"


def test_analysis_response_uses_typed_matching_result():
    response = AnalysisResponse(
        score=75,
        result={
            "requirement_matches": [
                {
                    "requirement": {
                        "text": "Python",
                        "category": "skill",
                    },
                    "status": "matched",
                    "score": 1,
                    "evidence": [
                        {
                            "source": "skills",
                            "source_index": 0,
                            "text": "Python",
                            "matched_terms": ["Python"],
                        }
                    ],
                    "matched_terms": ["Python"],
                }
            ],
            "category_scores": [
                {
                    "category": "skill",
                    "score": 75,
                    "earned_weight": 1.5,
                    "available_weight": 2,
                    "matched_count": 1,
                }
            ],
            "matched_keywords": ["Python"],
        },
    )

    match = response.result.requirement_matches[0]
    assert match.status == "matched"
    assert match.evidence[0].source == "skills"
    assert response.result.category_scores[0].score == 75


@pytest.mark.parametrize("score", [-0.1, 100.1])
def test_analysis_response_rejects_scores_outside_zero_to_one_hundred(score):
    with pytest.raises(ValidationError):
        AnalysisResponse(
            score=score,
            result={},
        )
