"""Request and response schemas for a resume-to-job analysis."""

from pydantic import BaseModel, Field

from .job import JobDescription
from .resume import Resume


class AnalysisRequest(BaseModel):
    resume: Resume
    job: JobDescription


class AnalysisResponse(BaseModel):
    score: float = Field(ge=0, le=100)
    # Matching will replace this generic mapping with its final result model.
    result: dict[str, object]
