import re

MOJIBAKE_REPLACEMENTS = {
    "Ã¢â‚¬Â¢": "â€¢",
    "Ã¢â€”â€¹": "â—‹",
    "Ã¢â€”Â": "â—",
    "Ã¢â€“Âª": "â–ª",
    "Ã¢â€“Â ": "â– ",
    "Ã¢â€”Â¦": "â—¦",
    "Ã¢â‚¬Â£": "â€£",
    "Ã¢â‚¬â€œ": "â€“",
    "Ã¢â‚¬â€": "â€”",
    "Ã¢â‚¬â„¢": "'",
    "Ã¢â‚¬Ëœ": "'",
    "Ã¢â‚¬Å“": '"',
    "Ã¢â‚¬Â": '"',
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€": '"',
}

BULLET_PATTERN = r"^[\sâ€¢\-*â—‹â—â–ªâ– â—¦â€£]+"

MOJIBAKE_REPLACEMENTS.update({
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00c2\u00a2": "\u2022",
    "\u00c3\u00a2\u00e2\u20ac\u201d\u00e2\u20ac\u00b9": "\u25cb",
    "\u00c3\u00a2\u00e2\u20ac\u201d\u00c2\u008f": "\u25cf",
    "\u00c3\u00a2\u00e2\u20ac\u201c\u00c2\u00aa": "\u25aa",
    "\u00c3\u00a2\u00e2\u20ac\u201c\u00c2\u00a0": "\u25a0",
    "\u00c3\u00a2\u00e2\u20ac\u201d\u00c2\u00a6": "\u25e6",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00c2\u00a3": "\u2023",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0153": "\u2013",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u009d": "\u2014",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2": "'",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00cb\u0153": "'",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00c5\u201c": '"',
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00c2\u009d": '"',
    "\u00e2\u20ac\u00a2": "\u2022",
    "\u00e2\u2014\u2039": "\u25cb",
    "\u00e2\u2014\u008f": "\u25cf",
    "\u00e2\u20ac\u201c\u00aa": "\u25aa",
    "\u00e2\u20ac\u201c\u00a0": "\u25a0",
    "\u00e2\u2014\u00a6": "\u25e6",
    "\u00e2\u20ac\u00a3": "\u2023",
    "\u00e2\u20ac\u201c": "\u2013",
    "\u00e2\u20ac\u009d": "\u2014",
    "\u00e2\u20ac\u2122": "'",
    "\u00e2\u20ac\u02dc": "'",
    "\u00e2\u20ac\u0153": '"',
    "\u2019": "'",
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
})

BULLET_PATTERN = r"^[\s\u2022\-*\u25cb\u25cf\u25aa\u25a0\u25e6\u2023]+"

def normalize_text(text):
    if not text:
        return ""

    normalized = str(text)
    try:
        repaired = normalized.encode("cp1252").decode("utf-8")
        if "ï¿½" not in repaired:
            normalized = repaired
    except UnicodeError:
        pass

    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        normalized = normalized.replace(bad, good)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()

def strip_bullet(line):
    return re.sub(BULLET_PATTERN, "", normalize_text(line)).strip()

def has_bullet(line):
    return bool(re.match(BULLET_PATTERN, normalize_text(line)))

# ==============Education Parser================
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
    "minor": [
        "minor",
        "minors",
    ],
    "courseworks": [
        "relevant coursework",
        "coursework",
        "relevant courses",
        "courses",
        "selected courses",
        "course highlights",
        "academic coursework",
        "key coursework",
        "selected coursework",
        "related coursework",
        "core coursework",
        "major coursework",
        "course subjects",
    ],
    "certifications": [
        "certification",
        "certifications",
        "certificate",
        "certificates",
        "health and safety",
        "microsoft excel",
        "udemy",
    ],
}

def keyword_matcher(line):
    normalized_line = strip_bullet(line).lower()
    words = normalized_line.split()

    new_words = []
    for word in words:
        stripped_word = word.strip(":,.;")
        new_words.append(stripped_word)

    for category, alias_list in education_aliases.items():
        for alias in alias_list:
            if alias in normalized_line:
                if " " in alias:
                    return category
                elif alias in new_words:
                    return category

def education_parser(education): #input is a list
    parsed_education = {}
    last_category = None
    for item in education:
        item = normalize_text(item)
        if not item:
            continue
        category = keyword_matcher(item)
        if category is None and last_category == "courseworks":
            category = "courseworks"
        if category is None:
            category = "other"
        parsed_education.setdefault(category, []).append(item)
        last_category = category
    return parsed_education

# =============Skill Parser============== 

def skill_parser(skills):
    clean_skills = []
    parsed_skills = {}
    for skill in skills:
        cleaned = strip_bullet(skill)                  # remove leading bullets/markers
        if cleaned:                                    # skip empty strings
            clean_skills.append(cleaned)
    parsed_skills["skills"] = clean_skills
    return parsed_skills

# ==============Shared vacob==============
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
    'available', 'collaborated', 'managed', 'achieved',
}

months = {
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
}

position_keywords = {
    "engineer", "developer", "intern", "analyst", "assistant",
    "manager", "consultant", "researcher", "specialist", "administrator",
    "tutor", "president", "vice", "vp", "treasurer", "secretary", "director",
    "coordinator", "lead", "leader", "chair", "officer", "teacher", "server",
}

bullet_markers = {"â€¢", "*", "â—‹", "â—", "â–ª", "â– ", "â—¦", "â€£"}

non_company_labels = [
    "experience", "activities", "skills", "summary", "objective", "profile",
    "about", "about me", "interests", "hobbies", "references", "awards",
    "achievements", "publications", "presentations", "certifications",
    "certificates", "licenses", "workshops", "involvement", "leadership",
    "organizations", "memberships", "volunteer", "volunteering",
    "work experience", "career related experience", "additional experience",
    "additional work experience", "related experience", "relevant experience",
    "prior experience", "work history", "employment history",
    "campus involvement", "campus activities", "extracurricular activities",
    "extracurricular experience", "leadership experience", "volunteer experience",
    "community service", "community involvement", "training and certifications",
    "trainings and certifications", "professional development",
    "technical skills", "core competencies", "additional information",
    "honors and awards", "references available",
]

embedded_section_labels = [
    "campus involvement",
    "activities",
    "leadership",
    "leadership experience",
    "extracurricular activities",
    "additional information",
]

def strip_embedded_section_header(line):
    normalized = normalize_text(line)
    for label in embedded_section_labels:
        pattern = rf"\s+{re.escape(label.upper())}\b.*$"
        cleaned = re.sub(pattern, "", normalized)
        if cleaned != normalized:
            return cleaned.strip(), True
    return normalized, False

def is_non_company_label(line):
    normalized = normalize_text(line).lower().rstrip(":")
    return normalized in non_company_labels

def line_normalizer(line):
    if not line:
        return []
    normalized = strip_bullet(line).lower()
    return [word.strip(":,.;()[]") for word in normalized.split()]


# ============Date Extraction===============

month_pattern = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t|tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
season_pattern = r"(spring|summer|summers|fall|autumn|winter)"
date_separator = rf"\s*[-{chr(0x2013)}{chr(0x2014)}]\s*"
month_name_date = rf"{month_pattern}\.?\s*\d{{2,4}}{date_separator}(present|current|{month_pattern}\.?\s*\d{{2,4}})"
season_date = rf"{season_pattern}\.?\s*\d{{2,4}}{date_separator}(present|current|{season_pattern}\.?\s*\d{{2,4}}|\d{{2,4}})"
numeric_date = rf"\d{{1,2}}/(?:xx|XX|\d{{2,4}}){date_separator}(present|current|\d{{1,2}}/(?:xx|XX|\d{{2,4}}))"
bare_year_date = rf"\b\d{{4}}{date_separator}(present|current|\d{{4}})\b"
month_pair_shared_year = rf"{month_pattern}\.?{date_separator}{month_pattern}\.?\s*\d{{2,4}}"

date_fragment_pattern = re.compile(
    rf"({month_name_date})|({season_date})|({numeric_date})|({bare_year_date})|({month_pair_shared_year})",
    re.IGNORECASE
)

def extract_date(line):
    """Finds a date-range fragment anywhere in the line.
    Returns (date_text, remainder) â€” remainder is the line with the date removed."""
    line = normalize_text(line)
    match = date_fragment_pattern.search(line)
    if not match:
        return None, line

    date_text = match.group().strip()
    remainder = (line[:match.start()] + line[match.end():]).strip(" ,")
    return date_text, remainder


def is_date(line):
    """True only if the ENTIRE line is just a date fragment (nothing else)."""
    date_text, remainder = extract_date(line)
    if date_text is None:
        return False
    return remainder == ""

# ==============Project Parser==============

def is_title(line):
    if has_bullet(line):
        return False

    line = strip_bullet(line)
    if not line:
        return False
    
    _, remainder = extract_date(line)
    check_line = remainder if remainder else line

    words = check_line.split()
    word_count = len(words)

    if word_count > 12:
        return False

    if check_line.endswith(('.', ',', ';')):
        return False
    
    first_word = words[0].lower() if words else ""
    if first_word in action_verbs:
        return False
    if first_word in {"and", "or", "but", "which", "that", "with", "using", "across"}:
        return False

    # Large numbers are fine if they're part of a date we already stripped;
    # only flag numbers NOT belonging to a date (e.g. "270,000 records")
    numbers = re.findall(r'\b\d{3,}\b', check_line)
    for num in numbers:
        if not (len(num) == 4 and num[:2] in ("19", "20")):
            return False


    return True

def merge_project_continuation_lines(lines):
    """Merge wrapped bullet lines (no bullet, not a title) into the previous line
    when the previous line looks mid-sentence rather than complete."""
    merged = []
    for raw_line in lines:
        stripped = normalize_text(raw_line)
        if not stripped:
            continue

        if merged:
            prev = merged[-1]
            looks_like_new_title = is_title(stripped)
            line_has_bullet = has_bullet(stripped)
            prev_incomplete = not ends_with_terminal_punctuation(prev)
            prev_ends_with_connector = bool(re.search(r"\b(and|or|with|using|across|to|of|for|in)$|,$", prev.lower()))

            # Merge if: not a new title, no leading bullet, and previous line looks unfinished
            if not line_has_bullet and (
                (not looks_like_new_title and prev_incomplete) or
                prev_ends_with_connector
            ):
                merged[-1] = prev.rstrip() + " " + stripped
                continue

        merged.append(stripped)
    return merged


def project_parser(projects):
    if not projects:
        return {}

    projects = merge_project_continuation_lines(projects)

    title_positions = []
    for index, line in enumerate(projects):
        if line.strip() and is_title(line):
            title_positions.append((line.strip(), index))

    if not title_positions:
        return {}

    parsed_projects = {}

    for i in range(len(title_positions)):
        title, start = title_positions[i]
        end = title_positions[i + 1][1] if i + 1 < len(title_positions) else len(projects)

        description = [
            line.strip()
            for line in projects[start + 1 : end]
            if line.strip()
        ]

        unique_title = title
        counter = 1
        while unique_title in parsed_projects:
            unique_title = f"{title} ({counter})"
            counter += 1

        parsed_projects[unique_title] = description

    return parsed_projects

# ================Experience Parser================

def is_position(line):
    words = line_normalizer(line)
    return any(word in position_keywords for word in words)

         
def is_description(line):
    if is_date(line):
        return False
    if is_position(line):
        return False

    stripped = normalize_text(line)

    line_has_bullet = has_bullet(stripped)

    words = line_normalizer(line)
    has_action_verb = any(word in action_verbs for word in words)
        
    return has_action_verb or line_has_bullet


def is_company(line):
    line = normalize_text(line)
    if not line.strip():
        return False
    first_alpha = re.search(r"[A-Za-z]", line)
    if first_alpha and first_alpha.group().islower():
        return False
    if is_date(line):
        return False
    if is_position(line):
        return False
    if is_description(line):
        return False
    if is_non_company_label(line):
        return False
    if any(word in line.lower() for word in ("university", "department", "association", "club", "services", "group")):
        return len(line.split()) <= 10
    if len(line.split()) > 5:
        return False
    if re.search(r'\.\s+\w', line):  # dot followed by space and word â†’ sentence
        return False
    return True

def is_location(line):
    if not line:
        return False
    line = normalize_text(line)
    if line.lower() == "remote":
        return True
    if "/" in line:
        return False

    stripped = line.strip()
    if "," not in stripped:
        return False

    parts = [p.strip() for p in stripped.split(",")]
    if len(parts) < 2:
        return False

    last = parts[-1]
    if any(word in last.lower() for word in ("department", "university", "college", "school", "services", "group")):
        return False
    # Last segment should look like a state/country â€” short, letters only
    if not re.match(r'^[A-Za-z\s]+(?:\s\d+)?$', last):
        return False
    if len(last.split()) > 3:
        return False

    # Every earlier segment (company/city) should be short too â€” not a full sentence
    for part in parts[:-1]:
        if len(part.split()) > 6:
            return False

    # Overall line shouldn't run sentence-length
    if len(stripped.split()) > 12:
        return False

    return True

def is_new_entry_signal(line):
    """True if this line looks like it starts something new
    (date, bullet, position, or location) â€” i.e. NOT a wrapped continuation."""
    date_text, _ = extract_date(line)
    if date_text:
        return True
    if has_bullet(line):
        return True
    if is_position(line):
        return True
    if is_company(line):
        return True
    if is_location(line):
        return True
    
def ends_with_terminal_punctuation(line):
    return normalize_text(line).endswith(('.', '!', '?', ':'))

def split_location_and_position(line):
    line = normalize_text(line)
    match = re.match(r"^(.+?,\s*[A-Za-z]{2})(?:\s+|\s+-\s+|\s+â€“\s+|\s+â€”\s+)(.+)$", line)
    if not match:
        return None

    location = match.group(1).strip()
    position = match.group(2).strip()
    if is_location(location) and is_position(position):
        return location, position
    return None

def split_company_and_position(line):
    line = normalize_text(line)
    words = line.split()
    if len(words) < 2:
        return None

    for index in range(len(words) - 1, 0, -1):
        company = " ".join(words[:index]).strip()
        position = " ".join(words[index:]).strip()
        if is_company(company) and is_position(position):
            return company, position
    return None

def merge_continuation_lines(lines):
    merged = []
    for raw_line in lines:
        stripped, section_boundary = strip_embedded_section_header(raw_line)
        if not stripped:
            if section_boundary:
                break
            continue
        
        if merged:
            prev = merged[-1]
            looks_like_new_entry = is_new_entry_signal(stripped)
            prev_incomplete = not ends_with_terminal_punctuation(prev)

            if not looks_like_new_entry and prev_incomplete:
                merged[-1] = prev.rstrip() + " " + stripped
                continue
        
        merged.append(stripped)
        if section_boundary:
            break
    return merged

def split_experience_entries(experience):
    experience = merge_continuation_lines(experience)
    experience = [line for line in experience if not is_non_company_label(line)]
    
    current_entry = []
    entries = []

    has_date = False
    has_position = False
    has_company = False

    for line in experience:
        split_location_position = split_location_and_position(line)
        if split_location_position:
            location, position = split_location_position
            if current_entry and (has_date or has_position):
                entries.append(current_entry)
                current_entry = []
                has_position = False
                has_company = False
                has_date = False

            current_entry.append(location)
            current_entry.append(position)
            has_position = True
            continue

        date_text, remainder = extract_date(line)

        if date_text:
            has_date = True
            current_entry.append(date_text)

        if not remainder:
            continue

        line = remainder

        split_company_position = None if has_company or not date_text else split_company_and_position(line)
        if split_company_position:
            company, position = split_company_position
            if current_entry and (has_company or has_position):
                entries.append(current_entry)
                current_entry = []
                has_position = False
                has_company = False
                has_date = False
                if date_text:
                    current_entry.append(date_text)
                    has_date = True

            current_entry.append(company)
            current_entry.append(position)
            has_company = True
            has_position = True
            continue

        # Boundary: new position/company detected and we already have one in progress
        if (is_company(line) and has_company and not is_location(line)) or \
           (is_position(line) and has_position):
            entries.append(current_entry)
            current_entry = []
            has_position = False
            has_company = False
            has_date = False

        if is_position(line):
            has_position = True
            current_entry.append(line)
        elif is_location(line):
            if has_company:  # new entry starting
                entries.append(current_entry)
                current_entry = []
                has_company = False
                has_position = False
                has_date = False

            parts = [p.strip() for p in line.split(",")]

            if len(parts) >= 3:
                company = ", ".join(parts[:-2])
                city = parts[-2]
                state = parts[-1]
            elif len(parts) == 2:
                company = ""
                city = parts[-2]
                state = parts[-1]
            else:
                company = ""
                city = line
                state = ""

            full_location = f"{city}, {state}" if state else city

            current_entry.append(company)
            has_company = True
            current_entry.append(full_location)
        elif is_company(line):
            has_company = True
            current_entry.append(line)
        elif is_description(line):
            current_entry.append(line)

    # Save the final entry
    if current_entry:
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


