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
    "certifications",
    "trainings and certifications",
    "training and certifications",
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
    "campus involvement",
    "campus activities",
    "extracurricular activities",
    "leadership",
    "leadership experience",
    "involvement",
    "organizations",
    "memberships",
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

def find_header_loc(resume_text):
    text = resume_text
    lines = text.splitlines()

    # Build a single cleaned list (strip + skip empty) used everywhere
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    cleaned_headers = [normalize_header(line) for line in cleaned_lines]
    
    headers_loc = {}
    all_header_positions = []

    for index, line in enumerate(cleaned_headers):
        if line in reversed_section_headers:
            section_name = reversed_section_headers[line]
            headers_loc.setdefault(section_name, []).append(index)
            all_header_positions.append(index)

    all_header_positions.sort()  # ensuring order is correct
    return headers_loc, all_header_positions

def extract_sections(resume_text, header_loc, all_header_positions):
    text = resume_text.strip()
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    extracted_sections = {}
    for section_name, start_indices in header_loc.items():
        combined = []
        for start_index in start_indices:
            next_boundary = next(
                (pos for pos in all_header_positions if pos > start_index),
                len(cleaned_lines)
            )
            combined.extend(cleaned_lines[start_index + 1 : next_boundary])
        extracted_sections[section_name] = combined

    return extracted_sections
