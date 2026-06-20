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
        "skills & activities"
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

def reverse_section_headers(headers):
    reversed_headers = {}
    for header in headers:
        header_list = headers[header]
        # print(header_list)
        for item in header_list:
            reversed_headers[item] = header
    
    return reversed_headers
        
reversed_section_headers = reverse_section_headers(section_headers)
print(reversed_section_headers)

def is_header(line):
    if not line:
        return False
    x = reversed_section_headers.keys()
    if line in x:
        return True

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

    all_header_positions.sort()  # ensuring order is correct
    for index in all_header_positions:
        print(index, cleaned_lines[index])
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


txt = """
JOHN DOE
john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

EDUCATION

University of North Texas — Denton, TX
Bachelor of Science in Computer Science
Expected Graduation: May 2028
GPA: 3.8/4.0

SKILLS

• Python
• Java
• C++
• FastAPI
• SQL
• Git
• Docker
• PostgreSQL
• Data Analysis
• Microsoft Excel
• Problem Solving
• Team Collaboration

EXPERIENCE

Software Engineer Intern
TechCorp Solutions
May 2025 - Aug 2025

• Developed REST APIs using FastAPI and PostgreSQL
• Implemented authentication and authorization features
• Improved API response times by 35%
• Collaborated with a team of 5 engineers

Data Analyst Intern
Insight Analytics
Jan 2025 - Apr 2025

• Analyzed customer datasets using Python and SQL
• Created dashboards to visualize business metrics
• Automated weekly reporting processes
• Presented findings to management

IT Support Assistant
University of North Texas
Sep 2024 - Dec 2024

• Resolved hardware and software issues for students
• Maintained computer lab equipment
• Assisted with network troubleshooting
• Documented support procedures

PROJECTS

ATS Resume Optimizer

• Built a resume parser using FastAPI
• Extracted education, skills, projects, and experience sections
• Implemented keyword matching against job descriptions

Expense Tracker App

• Developed a full-stack expense tracking application
• Added user authentication and reporting features
• Integrated PostgreSQL database

LEADERSHIP

Computer Science Club

• Organized technical workshops
• Mentored first-year students
"""
x, y= find_header_loc(txt)
print(x, y)
z = extract_sections(txt,x,y)
print(z)