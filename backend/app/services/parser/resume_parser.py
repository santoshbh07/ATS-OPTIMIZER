from pathlib import Path

from .text_extractor import extract_text
from .section_extractor import find_header_loc, extract_sections
from .parsers import (
    education_parser,
    skill_parser,
    project_parser,
)
def parse_resume(file_path):
    resume_txt = extract_text(file_path)

    header_loc, all_header_positions = find_header_loc(resume_txt)

    section_contents = extract_sections(
        resume_txt,
        header_loc,
        all_header_positions
    )

    education = section_contents.get("education", "")
    skills = section_contents.get("skills", "")
    projects = section_contents.get("projects", "")

    parsed_education = education_parser(education)
    parsed_skills = skill_parser(skills)
    parsed_projects = project_parser(projects)

    parsed_resume = {
        "education": parsed_education,
        "skills": parsed_skills,
        "projects": parsed_projects,
    }
    
    return parsed_resume