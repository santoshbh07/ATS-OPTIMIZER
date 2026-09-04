from dataclasses import asdict
from pathlib import Path

from .certification_parser import parse_certifications
from .education_parser import parse_education
from .experience_parser import parse_experience
from .project_parser import parse_projects
from .skill_parser import parse_skills
from ..resume_text_extractor.section_extractor import extract_sections
from ..resume_text_extractor.text_extractor import extract_text


def parse_resume_file(
    file_path: Path,
) -> dict[str, list[dict[str, object]]]:
    resume_text = extract_text(file_path)
    if not resume_text.strip():
        raise ValueError(
            "No readable text was found in the resume. "
            "Scanned documents require OCR before upload."
        )

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
    experience_records = parse_experience(
        sections.get("experience", [])
    )
    certification_records = parse_certifications(
        sections.get("certifications", [])
    )
    embedded_certification_records = parse_certifications(
        sections.get("education", []),
        require_marker=True,
    )

    seen_certifications = {
        record.name.casefold()
        for record in certification_records
    }
    certification_records.extend(
        record
        for record in embedded_certification_records
        if record.name.casefold() not in seen_certifications
    )

    result = {
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
        "experience": [
            asdict(record)
            for record in experience_records
        ],
        "certifications": [
            asdict(record)
            for record in certification_records
        ],
    }

    if not any(result.values()):
        raise ValueError(
            "No supported resume sections or structured content could be parsed."
        )

    return result
