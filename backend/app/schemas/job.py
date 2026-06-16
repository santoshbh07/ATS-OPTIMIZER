from pydantic import BaseModel
from typing import Optional


class JobDescription(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: list[str]
    experience_required: Optional[float] = None  # fixed typo + default