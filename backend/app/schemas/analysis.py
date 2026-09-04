"""Request and response schemas for a resume-to-job analysis."""

from typing import Literal

from pydantic import BaseModel, Field

from .job import JobDescription, JobRequirement, RequirementCategory
from .resume import Resume


MatchStatus = Literal[
    "matched",
    "partial",
    "missing",
    "not_evaluated",
]

EvidenceSource = Literal[
    "skills",
    "projects",
    "experience",
    "education",
    "certifications",
]


class MatchEvidence(BaseModel):
    source: EvidenceSource
    text: str
    source_index: int | None = Field(default=None, ge=0)
    matched_terms: list[str] = Field(default_factory=list)


class RequirementMatch(BaseModel):
    requirement: JobRequirement
    status: MatchStatus
    score: float = Field(ge=0, le=1)
    evidence: list[MatchEvidence] = Field(default_factory=list)
    matched_terms: list[str] = Field(default_factory=list)
    missing_terms: list[str] = Field(default_factory=list)
    explanation: str | None = None


class CategoryScore(BaseModel):
    category: RequirementCategory
    score: float = Field(ge=0, le=100)
    earned_weight: float = Field(ge=0)
    available_weight: float = Field(ge=0)
    matched_count: int = Field(default=0, ge=0)
    partial_count: int = Field(default=0, ge=0)
    missing_count: int = Field(default=0, ge=0)
    not_evaluated_count: int = Field(default=0, ge=0)


class AnalysisResult(BaseModel):
    requirement_matches: list[RequirementMatch] = Field(default_factory=list)
    category_scores: list[CategoryScore] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    resume: Resume
    job: JobDescription


class AnalysisResponse(BaseModel):
    score: float = Field(ge=0, le=100)
    result: AnalysisResult = Field(default_factory=AnalysisResult)
