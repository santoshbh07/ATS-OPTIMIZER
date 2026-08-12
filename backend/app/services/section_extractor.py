import re

section_headers = {
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "competencies",
        "technologies",
        "technical proficiencies",
        "areas of expertise",
        "expertise",
        "tools",
        "skills & activities",
        "strengths",
        "skills / strengths"
    ],

    "education": [
    "education",
    "academic background",
    "academic qualifications",
    "educational background",
    "qualifications",
    "academic history",
    "certification",
    # Mixed headings
    "education and certifications",
    "education & certifications",
    "education / certifications",
    "education and training",
    "education, training and certifications",
    "degrees and certifications",
    "degrees & certifications",
    ], 
    
    "certifications": [
        "certification",
        "certifications",
        "professional certifications",
        "technical certifications",
        "licenses and certifications",
        "certifications and licenses",
        "credentials",
        "professional credentials",
        "training and certifications",
        "trainings and certifications",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "employment",
        "work history",
        "career history",
        "relevant experience",
        "industry experience",
        "internship",
        "internships",
        "internship experience",
        "professional background",
        "career experience",
        "work and leadership experience",
        "leadership and experience",
        "experience and leadership",
        "research experience",
        "teaching experience",
        "volunteer experience",
        "career related experience",
        "extracurricular experience",
        "additional work experience",
        "additional experience"
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "relevant projects",
        "technical projects",
        "key projects",
        "project experience",
        "selected projects"
    ],
    
}

section_headers["interests"] = ["interests", "hobbies"]
section_headers["activities"] = [
    "activities",
    "affiliations",
    "campus involvement",
    "campus activities",
    "extracurricular activities",
    "leadership",
    "leadership experience",
    "involvement",
    "organizations",
    "memberships",
    "memberships/affiliations",
    "memberships and affiliations",
    "memberships & affiliations",
]

def reverse_section_headers(headers):
    reversed_headers = {}
    for header in headers:
        header_list = headers[header]
        for item in header_list:
            reversed_headers[item] = header
    
    return reversed_headers
        
reversed_section_headers = reverse_section_headers(section_headers)

def normalize_header(line):
    if not line:
        return ""

    normalized = line.lower().strip()
    normalized = re.sub(r"^[\s\-*•▪■◦‣]+", "", normalized)
    normalized = normalized.rstrip(":|•-–— ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized

def is_header(line):
    return normalize_header(line) in reversed_section_headers

def _clean_resume_lines(resume_text: str) -> list[str]:
    return [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]


def find_header_loc(
    resume_text: str,
) -> tuple[dict[str, list[int]], list[int]]:
    cleaned_lines = _clean_resume_lines(resume_text)

    headers_loc: dict[str, list[int]] = {}
    all_header_positions: list[int] = []

    for index, line in enumerate(cleaned_lines):
        normalized_line = normalize_header(line)

        if normalized_line not in reversed_section_headers:
            continue

        section_name = reversed_section_headers[normalized_line]

        headers_loc.setdefault(section_name, []).append(index)
        all_header_positions.append(index)

    return headers_loc, all_header_positions


def extract_sections(
    resume_text: str,
) -> dict[str, list[str]]:
    cleaned_lines = _clean_resume_lines(resume_text)

    header_loc, all_header_positions = find_header_loc(
        resume_text
    )

    extracted_sections: dict[str, list[str]] = {}

    for section_name, start_indices in header_loc.items():
        combined_lines: list[str] = []

        for start_index in start_indices:
            next_boundary = next(
                (
                    position
                    for position in all_header_positions
                    if position > start_index
                ),
                len(cleaned_lines),
            )

            combined_lines.extend(
                cleaned_lines[start_index + 1 : next_boundary]
            )

        extracted_sections[section_name] = combined_lines

    return extracted_sections
