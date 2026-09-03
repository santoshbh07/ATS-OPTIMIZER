"""Schemas for the structured output of the job-description parser."""

from typing import Literal

from pydantic import BaseModel, Field


RequirementCategory = Literal[
    "education",
    "experience",
    "certification",
    "soft_skill",
    "domain_knowledge",
    "skill",
    "other",
]


class JobMetadata(BaseModel):
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None


class JobRequirement(BaseModel):
    text: str
    category: RequirementCategory
    is_preferred: bool = False


class JobDescription(BaseModel):
    metadata: JobMetadata = Field(default_factory=JobMetadata)
    requirements: list[JobRequirement] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    sections: dict[str, list[str]] = Field(default_factory=dict)
