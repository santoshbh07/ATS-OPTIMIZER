"""Schemas for the structured output of the resume parser."""

from pydantic import BaseModel, Field


class NormalizedDate(BaseModel):
    year: int
    month: int | None = None
    season: str | None = None


class Skill(BaseModel):
    name: str
    category: str | None = None
    raw_text: str | None = None


class Experience(BaseModel):
    company: str | None = None
    position: str | None = None
    location: str | None = None
    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_current: bool = False
    descriptions: list[str] = Field(default_factory=list)
    raw_lines: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str | None = None
    location: str | None = None
    degree_name: str | None = None
    degree_level: str | None = None
    fields_of_study: list[str] = Field(default_factory=list)
    specializations: list[str] = Field(default_factory=list)
    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_expected: bool = False
    is_current: bool = False
    gpa: str | None = None
    honors: list[str] = Field(default_factory=list)
    minors: list[str] = Field(default_factory=list)
    coursework: list[str] = Field(default_factory=list)
    raw_lines: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str | None = None
    technologies: list[str] = Field(default_factory=list)
    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_current: bool = False
    github_url: str | None = None
    live_url: str | None = None
    other_urls: list[str] = Field(default_factory=list)
    descriptions: list[str] = Field(default_factory=list)
    raw_lines: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
