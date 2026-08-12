from dataclasses import asdict
from pathlib import Path

from .parser.education_parser import parse_education
from .parser.project_parser import parse_projects
from .parser.skill_parser import parse_skills
from .section_extractor import extract_sections
from .text_extractor import extract_text


def parse_resume_file(
    file_path: Path,
) -> dict[str, list[dict[str, object]]]:
    resume_text = extract_text(file_path)
    sections = extract_sections(resume_text)

    education_records = parse_education(
        sections.get("education", [])
    )
    parsed_skills = parse_skills(
        sections.get("skills", [])
    )
    project_records = parse_projects(
        sections.get("projects", [])
    )

    return {
        "education": [
            asdict(record)
            for record in education_records
        ],
        "skills": [
            asdict(record)
            for record in parsed_skills.skills
        ],
        "projects": [
            asdict(record)
            for record in project_records
        ],
    }
