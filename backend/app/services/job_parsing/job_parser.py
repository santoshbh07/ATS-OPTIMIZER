"""Public orchestration for job-description parsing."""

from dataclasses import asdict

from .metadata_parser import parse_metadata
from .requirement_parser import parse_requirements
from .responsibility_parser import parse_responsibilities
from .section_extractor import extract_sections


def parse_job_description(jd_text: str) -> dict[str, object]:
    """Parse job-description text into metadata, requirements, and duties."""
    if not isinstance(jd_text, str):
        raise TypeError("jd_text must be a string")
    if not jd_text.strip():
        raise ValueError("jd_text cannot be empty")

    sections = extract_sections(jd_text)
    if not sections:
        # Retain unsectioned postings so conservative parser fallbacks can still
        # recognize clearly worded requirements and responsibilities.
        overview_lines = [
            line.strip()
            for line in jd_text.splitlines()
            if line.strip()
        ]
        sections = {"job_overview": overview_lines}

    metadata = parse_metadata(jd_text, sections)
    requirements = parse_requirements(sections)
    responsibilities = parse_responsibilities(sections)

    return {
        "metadata": asdict(metadata),
        "requirements": [asdict(record) for record in requirements],
        "responsibilities": responsibilities,
        "sections": sections,
    }
