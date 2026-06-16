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
    ],

    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "educational background",
        "qualifications",
        "academic history",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "professional background",
        "relevant experience",
        "internship experience",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "relevant projects",
        "technical projects",
        "key projects",
        "project experience",
    ],
    
}

def reverse_section_headers(headers):
    reversed_headers = {}
    for header in headers:
        header_list = headers[header]
        # print(header_list)
        for item in header_list:
            reversed_headers[item] = header
    
    return reversed_headers
        
reversed_section_headers = reverse_section_headers(section_headers)
# print(reversed_section_headers)

def is_header(line):
    if not line:
        return False
    if line.startswith("-") or line.startswith("•"):
        return False
    if any(c in line for c in ["@", "/", ":", ".", ","]):
        return False
    # Must be all caps, 1-3 words, and at least 4 characters (avoids "SQL", "AI", etc.)
    return (
        (line.isupper() or line.istitle())
        and len(line.split()) <= 3
        and len(line) >= 6
    )
    
def find_header_loc(resume_text):
    text = resume_text
    lines = text.splitlines()

    # Build a single cleaned list (strip + skip empty) used everywhere
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_lower = [line.lower() for line in cleaned_lines]

    headers_loc = {}
    all_header_positions = []

    for index, line in enumerate(cleaned_lower):
        if line in reversed_section_headers:
            section_name = reversed_section_headers[line]
            headers_loc[section_name] = index
            all_header_positions.append(index)

    for index, line in enumerate(cleaned_lines):
        if is_header(line) and index not in all_header_positions:
            all_header_positions.append(index)

    all_header_positions.sort()  # ensure order is correct
    return headers_loc, all_header_positions


def extract_sections(resume_text, header_loc, all_header_positions):
    text = resume_text.strip()
    lines = text.splitlines()

    # Use the same cleaning logic as find_header_loc
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    extracted_sections = {}
    for section_name, start_index in header_loc.items():
        next_boundary = next(
            (pos for pos in all_header_positions if pos > start_index),
            len(cleaned_lines)
        )
        # +1 to skip the header line itself
        extracted_sections[section_name] = cleaned_lines[start_index + 1 : next_boundary]

    return extracted_sections
    