from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    resume_id: int
    job_id: int


class AnalysisResponse(BaseModel):
    resume_id: int
    job_id: int
    score: float
    result: dict  # will tighten this once scorer.py output shape is clear