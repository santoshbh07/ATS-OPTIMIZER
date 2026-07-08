import re
from collections import defaultdict


# Canonical skill names map to aliases that may appear in resumes or job posts.
# Keep this vocabulary conservative in v1 so random words are not counted as skills.
SKILL_ALIASES = {
    "Python": ["python", "python3"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "C": ["c"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "SQL": ["sql"],
    "NoSQL": ["nosql", "no sql"],
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi", "fast api"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express": ["express", "express.js"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "Linux": ["linux"],
    "Windows": ["windows"],
    "Excel": ["excel", "microsoft excel"],
    "MS Office": ["microsoft office", "ms office", "office suite"],
    "AutoCAD": ["autocad"],
    "REST API": ["rest api", "restful api", "rest"],
    "GraphQL": ["graphql"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Machine Learning": ["machine learning", "ml"],
}

REQUIRED_CUES = (
    "required",
    "requirement",
    "requirements",
    "must have",
    "must-have",
    "minimum",
    "need",
    "needs",
)

PREFERRED_CUES = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "plus",
    "bonus",
    "desired",
)

QUALIFICATION_PATTERNS = {
    "education": [
        r"\bassociate(?:'s)?(?: degree)?\b",
        r"\bbachelor(?:'s)?(?: degree)?\b",
        r"\bmaster(?:'s)?(?: degree)?\b",
        r"\bph\.?d\.?\b",
        r"\bdoctorate\b",
        r"\bcomputer science\b",
        r"\bsoftware engineering\b",
        r"\bcivil engineering\b",
        r"\bconstruction management\b",
    ],
    "experience_level": [
        r"\b\d+\+?\s*(?:years|yrs)\b",
        r"\binternship experience\b",
        r"\bprofessional experience\b",
        r"\bwork experience\b",
        r"\bentry level\b",
    ],
    "certifications": [
        r"\bcertification\b",
        r"\bcertified\b",
        r"\blicense\b",
        r"\blicensed\b",
        r"\bsecurity\+\b",
        r"\baws certified\b",
    ],
    "work_authorization": [
        r"\bus citizen\b",
        r"\bu\.s\. citizen\b",
        r"\bwork authorization\b",
        r"\bauthorized to work\b",
        r"\bsponsorship\b",
    ],
}


def normalize_text(value):
    """Normalize text for matching while preserving original parsed output elsewhere."""
    if value is None:
        return ""
    text = str(value).lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def iter_resume_text(parsed_resume):
    """Yield searchable text from the parsed resume without assuming every section exists."""
    if not parsed_resume:
        return

    for values in parsed_resume.get("education", {}).values():
        for item in values:
            yield item

    for skill in parsed_resume.get("skills", {}).get("skills", []):
        yield skill

    for title, descriptions in parsed_resume.get("projects", {}).items():
        yield title
        for description in descriptions:
            yield description

    for experience in parsed_resume.get("experience", []):
        yield experience.get("company", "")
        yield experience.get("position", "")
        yield experience.get("date", "")
        for description in experience.get("description", []):
            yield description


def alias_pattern(alias):
    """Build a boundary-aware regex so short aliases like C or JS do not overmatch inside words."""
    escaped = re.escape(alias.lower())
    if re.fullmatch(r"[a-z0-9#.+]+", alias.lower()):
        return rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#])"
    return rf"\b{escaped}\b"


def find_skills_in_text(text):
    found = set()
    normalized = normalize_text(text)

    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if re.search(alias_pattern(alias), normalized):
                found.add(canonical)
                break

    return found


def extract_explicit_skills(parsed_resume):
    skill_lines = parsed_resume.get("skills", {}).get("skills", [])
    explicit_skills = set()

    for line in skill_lines:
        explicit_skills.update(find_skills_in_text(line))

    return explicit_skills


def extract_inferred_skills(parsed_resume, explicit_skills=None):
    explicit_skills = explicit_skills or set()
    inferred_skills = set()

    # Projects and experience usually contain tools that candidates forget to list
    # in the skills section, so we scan those narrative sections as enrichment only.
    for title, descriptions in parsed_resume.get("projects", {}).items():
        inferred_skills.update(find_skills_in_text(title))
        for description in descriptions:
            inferred_skills.update(find_skills_in_text(description))

    for experience in parsed_resume.get("experience", []):
        inferred_skills.update(find_skills_in_text(experience.get("position", "")))
        for description in experience.get("description", []):
            inferred_skills.update(find_skills_in_text(description))

    return inferred_skills - explicit_skills


def extract_resume_skills(parsed_resume):
    explicit = extract_explicit_skills(parsed_resume)
    inferred = extract_inferred_skills(parsed_resume, explicit)
    all_skills = explicit | inferred

    return {
        "explicit": sorted(explicit),
        "inferred": sorted(inferred),
        "all": sorted(all_skills),
    }


def canonical_qualification(value):
    normalized = normalize_text(value)
    if "associate" in normalized:
        return "associate"
    if "bachelor" in normalized:
        return "bachelor"
    if "master" in normalized:
        return "master"
    if "ph" in normalized or "doctorate" in normalized:
        return "doctorate"
    if "computer science" in normalized:
        return "computer science"
    if "software engineering" in normalized:
        return "software engineering"
    if "civil engineering" in normalized:
        return "civil engineering"
    if "construction management" in normalized:
        return "construction management"
    return normalized

def extract_qualifications_from_text(text):
    normalized = normalize_text(text)
    qualifications = defaultdict(set)

    for category, patterns in QUALIFICATION_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, normalized, re.IGNORECASE):
                qualifications[category].add(canonical_qualification(match.group().strip()))

    return {key: sorted(values) for key, values in qualifications.items()}


def extract_resume_qualifications(parsed_resume):
    combined_text = " ".join(text for text in iter_resume_text(parsed_resume) if text)
    qualifications = extract_qualifications_from_text(combined_text)

    # Education parser output is already structured, so preserve those lines as evidence.
    education = parsed_resume.get("education", {})
    if education.get("degree"):
        qualifications.setdefault("education", [])
        qualifications["education"].extend(education["degree"])

    if education.get("certifications"):
        qualifications.setdefault("certifications", [])
        qualifications["certifications"].extend(education["certifications"])

    return {
        category: sorted(set(values))
        for category, values in qualifications.items()
    }


def classify_job_requirement(line):
    normalized = normalize_text(line)
    if any(cue in normalized for cue in REQUIRED_CUES):
        return "required"
    if any(cue in normalized for cue in PREFERRED_CUES):
        return "preferred"
    return "mentioned"


def extract_job_requirements(job_description):
    requirements = {
        "skills": {
            "required": set(),
            "preferred": set(),
            "mentioned": set(),
        },
        "qualifications": {
            "required": defaultdict(set),
            "preferred": defaultdict(set),
            "mentioned": defaultdict(set),
        },
    }

    lines = [line.strip() for line in str(job_description).splitlines() if line.strip()]
    if not lines:
        lines = [str(job_description)]

    for line in lines:
        bucket = classify_job_requirement(line)

        requirements["skills"][bucket].update(find_skills_in_text(line))

        qualifications = extract_qualifications_from_text(line)
        for category, values in qualifications.items():
            requirements["qualifications"][bucket][category].update(values)

    return {
        "skills": {
            bucket: sorted(values)
            for bucket, values in requirements["skills"].items()
        },
        "qualifications": {
            bucket: {
                category: sorted(values)
                for category, values in categories.items()
            }
            for bucket, categories in requirements["qualifications"].items()
        },
    }


def flatten_qualification_buckets(qualification_buckets):
    flat = set()
    for values in qualification_buckets.values():
        flat.update(values)
    return flat


def match_resume_to_job(parsed_resume, job_description):
    resume_skills = extract_resume_skills(parsed_resume)
    resume_qualifications = extract_resume_qualifications(parsed_resume)
    job_requirements = extract_job_requirements(job_description)

    resume_skill_set = set(resume_skills["all"])
    required_skills = set(job_requirements["skills"]["required"])
    preferred_skills = set(job_requirements["skills"]["preferred"])
    mentioned_skills = set(job_requirements["skills"]["mentioned"])
    target_skills = required_skills | preferred_skills | mentioned_skills

    matched_skills = resume_skill_set & target_skills
    missing_required_skills = required_skills - resume_skill_set
    missing_preferred_skills = preferred_skills - resume_skill_set

    resume_qualification_set = flatten_qualification_buckets(resume_qualifications)
    required_qualifications = flatten_qualification_buckets(
        job_requirements["qualifications"]["required"]
    )
    preferred_qualifications = flatten_qualification_buckets(
        job_requirements["qualifications"]["preferred"]
    )
    mentioned_qualifications = flatten_qualification_buckets(
        job_requirements["qualifications"]["mentioned"]
    )
    target_qualifications = (
        required_qualifications | preferred_qualifications | mentioned_qualifications
    )

    matched_qualifications = resume_qualification_set & target_qualifications
    missing_required_qualifications = required_qualifications - resume_qualification_set
    missing_preferred_qualifications = preferred_qualifications - resume_qualification_set

    # Matcher returns evidence only. scorer.py decides how this evidence becomes a score.
    return {
        "resume_skills": resume_skills,
        "resume_qualifications": resume_qualifications,
        "job_requirements": job_requirements,
        "matched_skills": sorted(matched_skills),
        "target_skills": sorted(target_skills),
        "missing_required_skills": sorted(missing_required_skills),
        "missing_preferred_skills": sorted(missing_preferred_skills),
        "matched_qualifications": sorted(matched_qualifications),
        "target_qualifications": sorted(target_qualifications),
        "missing_required_qualifications": sorted(missing_required_qualifications),
        "missing_preferred_qualifications": sorted(missing_preferred_qualifications),
    }
