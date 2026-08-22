import re

JOB_SECTION_ALIASES = {
    "responsibilities": {
        "responsibilities",
        "job responsibilities",
        "key responsibilities",
        "primary responsibilities",
        "core responsibilities",
        "your responsibilities",
        "roles and responsibilities",
        "duties",
        "job duties",
        "key duties",
        "what you'll do",
        "what you will do",
        "what you'll be doing",
        "what you will be doing",
        "what you'll do",
        "what you'll be doing",
        "your role",
        "the role",
        "in this role",
        "day-to-day",
        "day to day",
        "what to expect",
    },

    "requirements": {
        "requirements",
        "job requirements",
        "position requirements",
        "minimum requirements",
        "required qualifications",
        "minimum qualifications",
        "basic qualifications",
        "qualifications",
        "what we're looking for",
        "what we are looking for",
        "what you need",
        "what you'll need",
        "what you will need",
        "what you'll need",
        "what you bring",
        "what you'll bring",
        "what you will bring",
        "what you'll bring",
        "required qualifications and skills",
        "skills and qualifications",
        "experience and qualifications",
        "candidate requirements",
        "candidate qualifications",
    },

    "preferred_requirements": {
        "preferred qualifications",
        "preferred requirements",
        "preferred skills",
        "preferred experience",
        "desired qualifications",
        "desired skills",
        "desired experience",
        "nice to have",
        "nice-to-have",
        "nice to haves",
        "good to have",
        "bonus qualifications",
        "bonus skills",
        "bonus points",
        "additional qualifications",
        "additional skills",
        "ideal qualifications",
        "ideally",
        "what would set you apart",
    },

    "about_company": {
        "about us",
        "about the company",
        "about our company",
        "who we are",
        "our company",
        "company overview",
        "company description",
        "our story",
        "about the team",
        "meet the team",
        "our team",
    },

    "job_overview": {
        "job overview",
        "position overview",
        "role overview",
        "position summary",
        "job summary",
        "role summary",
        "job description",
        "position description",
        "about the role",
        "about this role",
        "about the position",
        "the opportunity",
        "opportunity",
    },

    "education": {
        "education",
        "education requirements",
        "educational requirements",
        "education qualifications",
        "educational qualifications",
        "required education",
        "academic requirements",
    },

    "experience": {
        "experience",
        "experience requirements",
        "required experience",
        "professional experience",
        "work experience",
        "relevant experience",
    },

    "skills": {
        "skills",
        "required skills",
        "key skills",
        "technical skills",
        "core skills",
        "skills required",
        "skills and competencies",
        "competencies",
        "core competencies",
        "knowledge and skills",
    },

    "benefits": {
        "benefits",
        "employee benefits",
        "our benefits",
        "benefits and perks",
        "perks and benefits",
        "perks",
        "what we offer",
        "what you'll get",
        "what you will get",
        "why join us",
        "why you'll love working here",
    },

    "compensation": {
        "compensation",
        "salary",
        "pay",
        "salary range",
        "pay range",
        "compensation range",
        "base salary",
        "base pay",
        "total compensation",
    },

    "work_environment": {
        "work environment",
        "working conditions",
        "work conditions",
        "physical requirements",
        "physical demands",
        "work setting",
    },

    "location": {
        "location",
        "job location",
        "work location",
        "office location",
        "workplace",
    },

    "schedule": {
        "schedule",
        "work schedule",
        "working hours",
        "hours",
        "hours of work",
        "shift",
        "shifts",
    },

    "application": {
        "how to apply",
        "application process",
        "application instructions",
        "apply",
        "to apply",
        "next steps",
        "interview process",
        "hiring process",
    },

    "equal_opportunity": {
        "equal opportunity",
        "equal employment opportunity",
        "equal opportunity employer",
        "eeo",
        "eeo statement",
        "diversity and inclusion",
        "diversity & inclusion",
    },
}

def reverse_section_headers(headers):
    reversed_headers = {}
    for header in headers:
        header_list = headers[header]
        for item in header_list:
            reversed_headers[item] = header
    
    return reversed_headers
        
reversed_section_headers = reverse_section_headers(JOB_SECTION_ALIASES)

def normalize_header(line):
    if not line:
        return ""

    normalized = line.lower().strip()
    normalized = re.sub(r"^[\s\-*•▪■◦‣]+", "", normalized)
    normalized = re.sub(r"\u2019", "'", normalized)
    normalized = normalized.rstrip(":|•-–— ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized

def is_header(line):
    return normalize_header(line) in reversed_section_headers

def _clean_jd_lines(jd_text: str) -> list[str]:
    return [
        line.strip()
        for line in jd_text.splitlines()
        if line.strip()
    ]
    
def find_header_loc(
    resume_text: str,
) -> tuple[dict[str, list[int]], list[int]]:
    cleaned_lines = _clean_jd_lines(resume_text)

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
    cleaned_lines = _clean_jd_lines(resume_text)

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
