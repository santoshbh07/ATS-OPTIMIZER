from dataclasses import dataclass, field
import re


@dataclass
class SkillRecord:
    name: str
    category: str | None = None
    raw_text: str | None = None


@dataclass
class ParsedSkills:
    skills: list[SkillRecord] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)


SKILL_CATEGORY_ALIASES: dict[str, str] = {
    "programming languages": "programming_languages",
    "coding languages": "programming_languages",
    "computer languages": "programming_languages",
    "frameworks": "frameworks",
    "web frameworks": "frameworks",
    "libraries": "libraries",
    "databases": "databases",
    "database technologies": "databases",
    "tools": "tools",
    "developer tools": "tools",
    "cloud": "cloud",
    "cloud platforms": "cloud",
    "operating systems": "operating_systems",
    "os": "operating_systems",
    "technical skills": "technical_skills",
    "technologies": "technical_skills",
    "soft skills": "soft_skills",
    "professional skills": "soft_skills",
    "professional": "soft_skills",
    "languages": "spoken_languages",
    "software": "software",
}

SKILL_SECTION_HEADERS = frozenset(
    {"skills", "technical skills", "core competencies"}
)
PROFICIENCY_LABELS = frozenset(
    {
        "beginner",
        "basic",
        "intermediate",
        "advanced",
        "proficient",
        "expert",
        "familiar",
        "working knowledge",
    }
)

_BULLET_CHARS = "•·▪●◦‣"
_LEADING_BULLET_RE = re.compile(rf"^\s*(?:[{_BULLET_CHARS}]|-\s+)\s*")
_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_QUALIFIER_RE = re.compile(r"\s*\([^()]*\)\s*$")
_EXPERIENCE_SUFFIX_RE = re.compile(
    r"\s*(?:[-:]|\()\s*\d+(?:\.\d+)?\+?\s*"
    r"(?:years?|yrs?)\s*(?:of\s+experience\s*)?\)?\s*$",
    re.IGNORECASE,
)
_PAREN_PROFICIENCY_RE = re.compile(
    r"\s*\((?P<label>[^()]*)\)\s*$", re.IGNORECASE
)
_SEPARATOR_PROFICIENCY_RE = re.compile(
    r"\s*(?:-|:)\s*(?P<label>[^-:]+)\s*$", re.IGNORECASE
)
_METADATA_PATTERNS = (
    re.compile(r"^\d+(?:\.\d+)?\+?\s+(?:years?|yrs?)\s+of\s+experience$", re.I),
    re.compile(r"^available\s+immediately$", re.I),
    re.compile(r"^open\s+to\s+relocation$", re.I),
    re.compile(r"^u\.?s\.?\s+citizen$", re.I),
    re.compile(r"^authorized\s+to\s+work\s+in\s+the\s+u\.?s\.?$", re.I),
)
_DESCRIPTIVE_PREFIXES = (
    "experienced in",
    "knowledge of",
    "familiar with",
    "strong understanding of",
    "hands-on experience with",
)


def clean_skill_line(line: str) -> str:
    """Remove line-level formatting without damaging skill punctuation."""
    cleaned = _LEADING_BULLET_RE.sub("", line.strip())
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def is_skill_section_header(line: str) -> bool:
    """Return whether a line is a skills-section heading, not a category."""
    normalized = line.strip().rstrip(":").casefold()
    return normalized in SKILL_SECTION_HEADERS


def _lookup_category(label: str) -> str | None:
    normalized = _WHITESPACE_RE.sub(" ", label.strip()).casefold()
    category = SKILL_CATEGORY_ALIASES.get(normalized)
    if category is not None:
        return category
    without_qualifier = _TRAILING_QUALIFIER_RE.sub("", normalized).strip()
    return SKILL_CATEGORY_ALIASES.get(without_qualifier)


def extract_skill_category(line: str) -> tuple[str | None, str]:
    """Extract a known category label and the remaining skill-list text."""
    category = _lookup_category(line.rstrip(":").strip())
    if category is not None:
        return category, ""

    for match in re.finditer(r"\s*(?P<separator>:|[|]|[-–—])\s*", line):
        label = line[: match.start()]
        category = _lookup_category(label)
        if category is not None:
            return category, line[match.end() :].strip()

    return None, line


def split_skill_candidates(skill_text: str) -> list[str]:
    """Split top-level delimiters while preserving nested and slash names."""
    candidates: list[str] = []
    current: list[str] = []
    closing_for = {"(": ")", "[": "]", "{": "}"}
    closing_stack: list[str] = []

    index = 0
    while index < len(skill_text):
        character = skill_text[index]
        if character in closing_for:
            closing_stack.append(closing_for[character])
        elif closing_stack and character == closing_stack[-1]:
            closing_stack.pop()

        slash_separator = (
            character == "/"
            and index > 0
            and index + 1 < len(skill_text)
            and skill_text[index - 1].isspace()
            and skill_text[index + 1].isspace()
        )
        if not closing_stack and (
            character in {",", ";", "|", *_BULLET_CHARS}
            or slash_separator
        ):
            candidate = "".join(current).strip()
            if candidate:
                candidates.append(candidate)
            current = []
        else:
            current.append(character)
        index += 1

    candidate = "".join(current).strip()
    if candidate:
        candidates.append(candidate)
    return candidates


def clean_skill_candidate(candidate: str) -> str | None:
    """Clean one candidate and reject obvious metadata or prose."""
    cleaned = clean_skill_line(candidate).strip(" \t,;|")
    if not cleaned:
        return None

    cleaned = _EXPERIENCE_SUFFIX_RE.sub("", cleaned).strip()
    for pattern in (_PAREN_PROFICIENCY_RE, _SEPARATOR_PROFICIENCY_RE):
        match = pattern.search(cleaned)
        if match and match.group("label").strip().casefold() in PROFICIENCY_LABELS:
            cleaned = cleaned[: match.start()].strip()
            break

    if not cleaned or any(pattern.fullmatch(cleaned) for pattern in _METADATA_PATTERNS):
        return None

    lowered = cleaned.casefold()
    if lowered.startswith(_DESCRIPTIVE_PREFIXES) or (
        cleaned.endswith(".") and len(cleaned.split()) > 6
    ):
        return None
    return cleaned


def parse_skills(skill_lines: list[str]) -> ParsedSkills:
    """Parse explicit resume skills-section lines into structured records."""
    if skill_lines is None:
        raise TypeError("skill_lines must be a list of strings")

    current_category: str | None = None
    parsed_skills: list[SkillRecord] = []
    seen: set[str] = set()

    for raw_line in skill_lines:
        line = clean_skill_line(raw_line)
        if not line or is_skill_section_header(line):
            continue

        detected_category, skill_text = extract_skill_category(line)
        if detected_category is not None:
            current_category = detected_category

        if not skill_text:
            continue

        for raw_candidate in split_skill_candidates(skill_text):
            candidate = clean_skill_candidate(raw_candidate)
            if candidate is None:
                continue
            key = candidate.casefold()
            if key in seen:
                continue
            seen.add(key)
            parsed_skills.append(
                SkillRecord(
                    name=candidate,
                    category=current_category,
                    raw_text=raw_candidate.strip(),
                )
            )

    return ParsedSkills(skills=parsed_skills, raw_lines=skill_lines.copy())
