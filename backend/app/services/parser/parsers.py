import re

# Education Parser
education_aliases = {
    "degree": [
        "bachelor of science",
        "b.s.",
        "bs",
        "b.sc",
        "bachelor of arts",
        "b.a.",
        "ba",
        "bachelor",
        "master of science",
        "m.s.",
        "ms",
        "m.sc",
        "master of arts",
        "m.a.",
        "ma",
        "master",
        "ph.d.",
        "phd",
        "doctorate",
        "associate degree",
        "associate",
    ],

    "institution": [
        "university",
        "college",
        "institute",
        "school",
        "academy",
        "polytechnic",
    ],

    "graduation": [
        "expected graduation",
        "graduation",
        "graduating",
        "expected",
        "graduation date",
        "expected graduation date",
        "anticipated graduation",
        "completion date",
    ],

    "gpa": [
        "gpa",
        "cgpa",
        "grade point average",
        "cumulative gpa",
    ],

    "honors": [
        "cum laude",
        "magna cum laude",
        "summa cum laude",
        "dean's list",
        "honors",
        "honours",
        "distinction",
    ],
    "courseworks": [
        "relevant coursework",
        "coursework",
        "relevant courses",
        "courses",
        "course highlights",
        "academic coursework",
        "key coursework",
        "selected coursework",
        "related coursework",
        "core coursework",
        "major coursework",
        "course subjects",
    ],
}

def keyword_matcher(line):
    normalized_line = line.lower()
        
    words = normalized_line.split()
    
    new_words = []
    
    for word in words:
        if ":" in word:
            no_colons = word.replace(":", "")
            new_words.append(no_colons)
        else:
            new_words.append(word)
    for category, alias_list in education_aliases.items():
        for alias in alias_list:
            if alias in normalized_line:
                if " " in alias:
                    return category
                elif alias in new_words:
                    return category

def education_parser(education): #input is a list
    parsed_education = {}
    for item in education:
        category = keyword_matcher(item)
        print(item, "->", category)
        parsed_education[category] = item
    return parsed_education

# Skill Parser 

def skill_parser(skills):
    clean_skills = []
    parsed_skills = {}
    for skill in skills:
        cleaned = re.sub(r"^[\s•\-\*]+", "", skill)  # remove leading bullets/markers
        cleaned = cleaned.strip()                      # trim whitespace
        if cleaned:                                    # skip empty strings
            clean_skills.append(cleaned)
    parsed_skills["skills"] = clean_skills
    return parsed_skills

# Project Parser
action_verbs = {
    'analyzed', 'assessed', 'evaluated', 'examined', 'identified', 'measured',
    'researched', 'reviewed', 'studied', 'tested', 'tracked', 'monitored',
    'built', 'developed', 'designed', 'implemented', 'created', 'constructed',
    'deployed', 'launched', 'established', 'configured', 'set',
    'cleaned', 'collected', 'organized', 'processed', 'extracted', 'generated',
    'calculated', 'computed', 'automated', 'migrated', 'transformed',
    'collaborated', 'coordinated', 'contributed', 'communicated', 'managed',
    'led', 'mentored', 'supported', 'partnered', 'worked',
    'improved', 'optimized', 'reduced', 'increased', 'enhanced', 'streamlined',
    'refactored', 'debugged', 'fixed', 'resolved', 'integrated',
    'practiced', 'maintained', 'utilized', 'used', 'applied', 'demonstrated',
    'presented', 'documented', 'wrote', 'added', 'completed', 'participated',
    'performed', 'prepared', 'provided', 'handled', 'ensured', 'flexible',
    'available', 'collaborated', 'managed',
}

def is_title(line):
    line = line.strip()
    if not line:
        return False

    words = line.split()
    word_count = len(words)

    # Titles are short — descriptions run long
    if word_count > 8:
        return False

    # Ends with sentence punctuation → description
    if line.endswith(('.', ',', ';')):
        return False

    # Starts with a bullet marker → description
    if re.match(r'^[-*•●◦]\s', line):
        return False

    # Starts with a past-tense action verb → description
    first_word = words[0].lower()
    if first_word in action_verbs:
        return False

    # Contains large numbers → likely a description ("270,000 records")
    if re.search(r'\b\d{3,}\b', line):
        return False

    return True
    
# print(is_title("• ATS analyser"))
def project_parser(projects):
    # Guard: no lines at all
    if not projects:
        return {}

    title_positions = []
    for index, line in enumerate(projects):
        if line.strip() and is_title(line):
            title_positions.append((line.strip(), index))

    # Guard: no titles found
    if not title_positions:
        return {}

    parsed_projects = {}

    for i in range(len(title_positions)):
        title, start = title_positions[i]

        # Description ends just before the next title, or at the end of the list
        if i + 1 < len(title_positions):
            end = title_positions[i + 1][1]
        else:
            end = len(projects)

        # Grab description lines, strip blanks
        description = [
            line.strip()
            for line in projects[start + 1 : end]
            if line.strip()
        ]

        # Handle duplicate titles by appending a counter
        unique_title = title
        counter = 1
        while unique_title in parsed_projects:
            unique_title = f"{title} ({counter})"
            counter += 1

        parsed_projects[unique_title] = description

    return parsed_projects

# Experience Parser

position_keywords = {
    "engineering",
    "engineer",
    "developer",
    "intern",
    "analyst",
    "assistant",
    "manager",
    "consultant",
    "researcher",
    "specialist",
    "administrator",
}

def line_normalizer(line):
    if not line:
        return False
    cleaned_line = line.lower().strip()
    words = cleaned_line.split()
    return words
    
def is_position(line):
    words = line_normalizer(line)
    for word in words:
        if word in position_keywords:
            return True
    
# print(is_position("Software engineering intern"))
months = {
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december",
    "jan", "feb", "mar", "apr",
    "jun", "jul", "aug", "sep",
    "sept", "oct", "nov", "dec"
}
def is_date(line): #v1 date identifier
    words = line_normalizer(line)
    has_year = False
    has_month = False

    for word in words:
        if word.isdigit() and len(word) == 4:
            has_year = True
        if word in months:
            has_month = True

    return has_year and has_month
    
bullet_markers = {
    "•",  # standard bullet
    "-",  # hyphen
    "*",  # asterisk
    "○",  # hollow circle
    "●",  # filled circle
    "▪",  # small square
    "■",  # square
    "◦",  # small hollow bullet
    "‣",  # triangular bullet
    "–",  # en dash
    "—",  # em dash
}           
def is_description(line):
    if is_date(line):
        return False
    if is_position(line):
        return False

    words = line_normalizer(line)

    has_action_verb = False
    has_bullet = False

    for word in words:
        if word in action_verbs:
            has_action_verb = True

        if word in bullet_markers or any(char in bullet_markers for char in word):
            has_bullet = True

        if has_action_verb and has_bullet:
            break

    return has_action_verb or has_bullet


company_keywords = {
    "inc", "llc", "corp", "ltd", "limited", "technologies", "technology",
    "solutions", "systems", "services", "group", "consulting", "software",
    "labs", "studio", "studios", "ventures", "holdings", "enterprises",
    "foundation", "institute", "associates",
}

def is_company(line):
    if not line.strip():
        return False
    if is_date(line):
        return False
    if is_position(line):
        return False
    if is_description(line):
        return False
    else:
        return True

def is_location(line):
    if line:
        if line.lower() == "remote":
            return True
        else:
            return bool(re.match(r"[^,]+,\s[A-Za-z\s]+(?:\s\d+)?", line))

def split_experience_entries(experience):
    current_entry = []
    entries = []
    
    has_date = False
    has_position = False
    has_company = False
    
    
    for line in experience:
        # Boundary: new position detected and we already have one in progress
        if is_company(line) and has_company and not is_location(line):
            entries.append(current_entry)
            current_entry = []
            has_position = False
            has_company = False
            has_date = False

        # Classify and collect AFTER boundary check
        if is_date(line):
            has_date = True
            current_entry.append(line)
        elif is_position(line):
            has_position = True
            current_entry.append(line)
        elif is_company(line):
            has_company = True
            current_entry.append(line)
        elif is_description(line):
            current_entry.append(line)
        elif is_location(line):
            current_entry.append(line)
        # print(current_entry)
    # Save the final entry
    if current_entry:
        entries.append(current_entry)
    elif is_company(line) and not is_location(line):
        entries.append(current_entry)
    return entries  
        

def get_company_name(entry):
    for i, line in enumerate(entry):
        if is_position(line) and i > 0:
            prev_line = entry[i - 1]
            if not is_date(prev_line) and not is_description(prev_line) and not is_location(prev_line):
                return prev_line.strip()
            elif i>1 and is_location(prev_line):
                if entry[i - 2]:
                    return entry[i - 2].strip()
    # fallback: elimination
    for line in entry:
        if is_company(line):
            return line.strip()
    return ""

def get_work_position(entry):
    for line in entry:
        if is_position(line):
            return line.strip()
    return ""

def get_date(entry):
    for line in entry:
        if is_date(line):
            return line.strip()
    return ""

def get_description(entry):
    return [line.strip() for line in entry if is_description(line)]

def experience_parser(experiences):
    entries = split_experience_entries(experiences)
    parsed_experiences = []

    for entry in entries:
        parsed_entry = {
            "company": get_company_name(entry),
            "position": get_work_position(entry),
            "date": get_date(entry),
            "description": get_description(entry),
        }
        parsed_experiences.append(parsed_entry)

    return parsed_experiences