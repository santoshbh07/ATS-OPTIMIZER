from pydantic import BaseModel, EmailStr
from typing import Optional


class Experience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None  # None when currently employed
    description: Optional[str] = None


class Education(BaseModel):  # str is too loose — give it its own model
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None


class Resume(BaseModel):
    name: str
    email: Optional[EmailStr] = None  # validates email format automatically
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[Education] = [] 