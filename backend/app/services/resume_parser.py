from dataclasses import asdict
from pathlib import Path

from .parser.education_parser import parse_education
from .section_extractor import extract_sections
from .text_extractor import extract_text


def parse_resume_file(file_path: Path) -> dict:
    resume_text = extract_text(file_path)
    sections = extract_sections(resume_text)

    education_records = parse_education(
        sections.get("education", [])
    )

    return {
        "education": [
            asdict(record)
            for record in education_records
        ],
    }