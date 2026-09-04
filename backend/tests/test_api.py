import pytest
from pydantic import ValidationError

from app.main import app, parse_job_endpoint
from app.schemas.job import JobDescription, JobTextRequest
from app.schemas.resume import Resume


def test_parse_job_endpoint_returns_parser_output():
    result = parse_job_endpoint(
        JobTextRequest(
            text="""
            Backend Engineer
            Example Corp
            Remote
            Requirements: Python
            Responsibilities: Build APIs
            """
        )
    )

    parsed = JobDescription.model_validate(result)
    assert parsed.metadata.job_title == "Backend Engineer"
    assert parsed.requirements[0].text == "Python"
    assert parsed.responsibilities == ["Build APIs"]


def test_job_text_request_rejects_blank_text():
    with pytest.raises(ValidationError, match="text cannot be empty"):
        JobTextRequest(text="   ")


def test_parsing_routes_publish_typed_response_models():
    routes = {
        route.path: route
        for route in app.routes
        if hasattr(route, "response_model")
    }

    assert routes["/parse-resume"].response_model is Resume
    assert routes["/parse-job"].response_model is JobDescription
