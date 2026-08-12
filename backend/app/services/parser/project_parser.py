import re
from dataclasses import dataclass, field
from .date_parser import NormalizedDate, DateCandidate, remove_date_candidates, detect_date_candidates, DetectorConfig
from .text_utils import normalize_text, strip_bullet

@dataclass
class ProjectRecord:
    name: str | None = None
    technologies: list[str] = field(default_factory=list)

    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_current: bool = False

    github_url: str | None = None
    live_url: str | None = None
    other_urls: list[str] = field(default_factory=list)

    descriptions: list[str] = field(default_factory=list)

    raw_lines: list[str] = field(default_factory=list)

@dataclass
class ProjectLinks:
    github_url: str | None = None
    live_url: str | None = None
    other_urls: list[str] = field(default_factory=list)

PROJECT_NAME_LABELS = {
    "project",
    "project name",
    "title",
    "project title",
}

TECHNOLOGY_LABELS = {
    "technologies",
    "technology",
    "tech",
    "tech stack",
    "technology stack",
    "stack",
    "stacks",
    "tools",
    "tools used",
    "built with",
    "developed with",
}

TECHNOLOGY_CANONICAL_NAMES = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "aws": "AWS",
    "git": "Git",
    "pandas": "pandas",
    "numpy": "NumPy",
    "scikit-learn": "scikit-learn",
    "sql": "SQL",
    "vue.js": "Vue.js",
    "tailwind css": "Tailwind CSS",
    "kubernetes": "Kubernetes",
    "excel": "Excel",
    "microsoft excel": "Microsoft Excel"
}

TECHNOLOGY_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "microsoft excel": "Microsoft Excel"

}

DESCRIPTION_LABELS = {
    "description",
    "project description",
    "details",
    "project details",
    "summary",
    "project summary",
    "overview",
    "project overview",
    "highlights",
    "project highlights",
    "key contributions",
    "contributions",
    "responsibilities",
    "achievements",
    "accomplishments",
    "impact",
}

DESCRIPTION_STARTERS = {
    "analyzed",
    "architected",
    "automated",
    "built",
    "configured",
    "created",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "integrated",
    "optimized",
    "tested",
    "trained",
    "used",
    "achieved",
    "collaborated",
    "delivered",
    "enhanced",
    "increased",
    "launched",
    "led",
    "maintained",
    "managed",
    "migrated",
    "reduced",
    "refactored",
    "resolved",
    "scaled",
    "streamlined",
    "supported",
    "validated",
    "worked",
}

_HEADER_SEPARATOR_RE = re.compile(
    r"\s+(?:\||-|\u2013|\u2014)\s+"
)
_PROJECT_NAME_LABEL_RE = re.compile(
    rf"^\s*(?:{'|'.join(re.escape(label) for label in PROJECT_NAME_LABELS)})"
    rf"\s*:\s*(?P<name>.+?)\s*$",
    re.IGNORECASE,
)

_METADATA_LABEL_RE = re.compile(
    r"^\s*(?:"
    r"technologies?|tech stack|stack|tools|built with|"
    r"github|repository|repo|source code|"
    r"live|demo|live demo|website|project link|"
    r"dates?|duration|description"
    r")\s*:",
    re.IGNORECASE,
)
_TECHNOLOGY_LABEL_PATTERN = "|".join(
    re.escape(label)
    for label in sorted(
        TECHNOLOGY_LABELS,
        key=len,
        reverse=True,
    )
)

_TECHNOLOGY_SEPARATOR_RE = re.compile(
    r"\s*(?:,|\||/|;)\s*"
)
_TECHNOLOGY_LABEL_RE = re.compile(
    rf"^\s*(?:{_TECHNOLOGY_LABEL_PATTERN})"
    rf"\s*:\s*(?P<technologies>.+?)\s*$",
    re.IGNORECASE,
)
_URL_RE = re.compile(
    r"(?:https?://|www\.|github\.com/)[^\s|<>\[\]]+",
    re.IGNORECASE,
)
_LIVE_URL_LABEL_RE = re.compile(
    r"\b(?:live(?:\s+demo)?|demo|website)\b\s*:",
    re.IGNORECASE,
)
_DATE_LABEL_RE = re.compile(
    r"^\s*(?:dates?|duration)\s*:",
    re.IGNORECASE,
)

_DESCRIPTION_LABEL_PATTERN = "|".join(
    re.escape(label)
    for label in sorted(
        DESCRIPTION_LABELS,
        key=len,
        reverse=True,
    )
)

_DESCRIPTION_LABEL_RE = re.compile(
    rf"^\s*(?P<label>{_DESCRIPTION_LABEL_PATTERN})"
    rf"\s*:\s*(?P<description>.*)$",
    re.IGNORECASE,
)

def is_bullet_line(line: str) -> bool:

    stripped = line.strip()
    return bool(stripped and strip_bullet(stripped) != stripped)

def is_url_line(line:str) -> bool:
    lowered = line.casefold()
    return (
        "http://" in lowered
        or "https://" in lowered
        or "github.com/" in lowered
        or "www." in lowered
    )

def is_metadata_line(line: str) -> bool:
    return bool(_METADATA_LABEL_RE.match(line))


def is_standalone_date_line(
    line: str,
    config: DetectorConfig | None = None,
) -> bool:
    """Return True when the line contains only one recognized date expression."""
    stripped_line = line.strip()

    if not stripped_line:
        return False

    candidates = detect_date_candidates(stripped_line, config)

    return (
        len(candidates) == 1
        and candidates[0].start_index == 0
        and candidates[0].end_index == len(stripped_line)
    )

def looks_like_inline_project_header(line: str) -> bool:
    cleaned = line.strip()

    if not cleaned:
        return False
    
    if is_bullet_line(cleaned):
        return False
    
    return bool(_HEADER_SEPARATOR_RE.search(cleaned))

def remove_bullet(line: str) -> str:
    return strip_bullet(line.strip()).strip()

def starts_with_description_starter(line: str) -> bool:
    words = line.split()

    if not words:
        return False

    first_word = words[0].casefold().rstrip(".,:;")
    return first_word in DESCRIPTION_STARTERS

def is_standalone_technology_line(line: str) -> bool:
    technologies = detect_standalone_technologies(line)
    return bool(technologies)

def looks_like_plain_project_header(line: str) -> bool:
    words = line.split()

    if not 1 <= len(words) <= 12:
        return False

    if line.endswith((".", ";")):
        return False

    return True

def looks_like_project_title(line: str) -> bool:
    """Identify a title-like line without treating résumé prose as a title."""
    if not looks_like_plain_project_header(line):
        return False

    if starts_with_description_starter(line):
        return False

    words = re.findall(
        r"[A-Za-z0-9][A-Za-z0-9+.#'-]*",
        line,
    )

    if not words:
        return False

    if len(words) == 1:
        return words[0][:1].isupper()

    title_like_words = sum(
        word.isupper()
        or word[:1].isupper()
        or any(character.isupper() for character in word[1:])
        for word in words
    )

    return title_like_words >= 2

def looks_like_project_header(raw_line: str) -> bool:
    line = normalize_text(raw_line).strip()

    if not line:
        return False

    content = (
        remove_bullet(line).strip()
        if is_bullet_line(line)
        else line
    )

    if not content:
        return False

    description_label, _ = split_project_description_label(content)

    if description_label is not None:
        return False

    if (
        is_metadata_line(content)
        or is_url_line(content)
        or is_standalone_date_line(content)
        or is_standalone_technology_line(content)
        or starts_with_description_starter(content)
    ):
        return False

    if detect_explicit_project_name(content) is not None:
        return True

    inline_name, _ = split_inline_project_description(content)

    if inline_name is not None:
        return True

    if looks_like_inline_project_header(content):
        title = _HEADER_SEPARATOR_RE.split(content, maxsplit=1)[0]
        return looks_like_project_title(title)

    if not looks_like_plain_project_header(content):
        return False

    return looks_like_project_title(content)

def project_header_content(raw_line: str) -> str | None:
    """Return normalized content only for a project header."""
    line = normalize_text(raw_line).strip()

    if not line or not looks_like_project_header(line):
        return None

    content = remove_bullet(line) if is_bullet_line(line) else line
    return content or None


def group_project_entries(project_lines: list[str],) -> list[list[str]]:
    grouped_projects: list[list[str]] = []
    current_group: list[str] = []

    current_group_has_header = False
    description_wrap_open = False

    for raw_line in project_lines:
        line = normalize_text(raw_line).strip()

        if not line:
            continue

        content = remove_bullet(line) if is_bullet_line(line) else line
        is_structural_line = (
            is_metadata_line(content)
            or is_standalone_date_line(content)
            or is_standalone_technology_line(content)
            or _URL_RE.fullmatch(content) is not None
        )
        is_wrapped_description = (
            description_wrap_open
            and not is_bullet_line(line)
            and not is_structural_line
        )
        is_header = (
            not is_wrapped_description
            and looks_like_project_header(line)
        )

        starts_new_project = is_header and current_group_has_header

        if starts_new_project:
            grouped_projects.append(current_group)

            current_group = []
            current_group_has_header = False
            description_wrap_open = False

        current_group.append(line)

        if is_header:
            current_group_has_header = True

        # PDF extraction can split one bullet across several physical lines.
        if is_project_description_bullet(line) or is_wrapped_description:
            description_wrap_open = not content.endswith((".", "!", "?"))
        else:
            description_wrap_open = False

    if current_group:
        grouped_projects.append(current_group)

    return grouped_projects

def detect_explicit_project_name(line: str) -> str | None:
    match = _PROJECT_NAME_LABEL_RE.match(line)

    if match is None:
        return None

    name = _HEADER_SEPARATOR_RE.split(
        match.group("name"),
        maxsplit=1,
    )[0]
    name = remove_date_candidates(name).strip()
    return name or None

def detect_name_from_header(line: str) -> str | None:
    parts = _HEADER_SEPARATOR_RE.split(line.strip(), maxsplit=1)

    if len(parts) < 2:
        return None
    
    candidate = parts[0].strip()
    return candidate or None

# ----------------------project name detection complete function-------------------
def detect_project_name(entry_lines: list[str]) -> str | None:
    normalized_lines = [
        line
        for raw_line in entry_lines
        if (line := project_header_content(raw_line)) is not None
    ]

    for line in normalized_lines:
        name = detect_explicit_project_name(line)

        if name is not None:
            return name

    for raw_line in entry_lines:
        name, _ = split_inline_project_description(raw_line)

        if name is not None:
            return name
        
    for line in normalized_lines:
        name = detect_name_from_header(line)
        if name is not None:
            return name
        
    # this is for plain project name
    for line in normalized_lines:
        if is_metadata_line(line):
            continue
        if is_url_line(line):
            continue
        line_without_date = remove_date_candidates(line)
        if line_without_date:
            return line_without_date
    
    return None
# ---------------------------------------------------------------------------------

def detect_project_dates(entry_lines: list[str],) -> DateCandidate | None:
    candidates: list[DateCandidate] = []

    for raw_line in entry_lines:
        line = project_header_content(raw_line)

        if line is None:
            normalized = normalize_text(raw_line).strip()
            line = (
                remove_bullet(normalized)
                if is_bullet_line(normalized)
                else normalized
            )

            if not (
                is_standalone_date_line(line)
                or _DATE_LABEL_RE.match(line)
            ):
                continue

        candidates.extend(detect_date_candidates(line))
    if not candidates:
        return None
    
    return max(
        candidates,
        key=lambda candidate: candidate.confidence,
    )

# ---------------------------Project URL detection-----------------------------
def extract_urls_from_line(line: str) -> list[str]:
    if not line:
        return []
    
    urls: list[str] = []
    
    for match in _URL_RE.finditer(line):
        url = match.group(0).rstrip(",.;:)]}")
        if url:
            urls.append(url)
    
    return urls

def detect_project_urls(entry_lines: list[str]) -> ProjectLinks:
    links = ProjectLinks()
    seen_urls: set[str] = set()

    for line in entry_lines:
        urls = extract_urls_from_line(line)
    
        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            lowered_url = url.casefold()
            if "github.com/" in lowered_url:
                if links.github_url is None:
                    links.github_url = url
                else:
                    links.other_urls.append(url)

            elif _LIVE_URL_LABEL_RE.search(line):
                if links.live_url is None:
                    links.live_url = url
                else:
                    links.other_urls.append(url)

            else:
                links.other_urls.append(url)

    return links

# ---------------------technology detection----------------------
def normalize_technology_name(technology: str,) -> str | None:
    cleaned = technology.strip()
    lookup = cleaned.casefold()
    
    if not cleaned:
        return None
    if lookup in TECHNOLOGY_ALIASES:
        return TECHNOLOGY_ALIASES[lookup]
    return TECHNOLOGY_CANONICAL_NAMES.get(lookup)

def extract_technologies_from_text(
    technology_text: str,
) -> list[str]:
    technologies: list[str] = []
    for candidate in _TECHNOLOGY_SEPARATOR_RE.split(
        technology_text
    ):
        technology = normalize_technology_name(candidate)
        if (
            technology is not None and technology not in technologies
        ):
            technologies.append(technology)
    return technologies

def detect_standalone_technologies(
    line: str,
) -> list[str]:
    cleaned = line.strip()

    if not cleaned:
        return []

    if is_bullet_line(cleaned):
        return []

    if is_url_line(cleaned):
        return []

    if detect_date_candidates(cleaned):
        return []

    candidates = _TECHNOLOGY_SEPARATOR_RE.split(cleaned)

    # A single unlabeled word such as "Python" is too ambiguous.
    if len(candidates) < 2:
        return []

    technologies: list[str] = []

    for candidate in candidates:
        technology = normalize_technology_name(candidate)

        # If any item is unknown, do not classify the whole line
        # as a standalone technology stack.
        if technology is None:
            return []

        if technology not in technologies:
            technologies.append(technology)

    return technologies

def detect_project_technologies(entry_lines: list[str]) -> list[str]:
    technologies: list[str] = []
    
    # explicitly labeled technology lines
    for raw_line in entry_lines:
        line = normalize_text(raw_line).strip()

        if is_bullet_line(line):
            line = remove_bullet(line).strip()

        match = _TECHNOLOGY_LABEL_RE.match(line)
        if not match:
            continue
        
        technology_text = match.group("technologies")
        
        for technology in extract_technologies_from_text(technology_text):
            if technology not in technologies:
                technologies.append(technology)
                
    # technologies inline with project headers
    for raw_line in entry_lines:
        line = project_header_content(raw_line)

        if line is None:
            continue

        if not looks_like_inline_project_header(line):
            continue
        line_without_dates = remove_date_candidates(line)
        parts = _HEADER_SEPARATOR_RE.split(line_without_dates)

        # part[0] is normally the project name itself
        for part in parts[1:]:
            for technology in extract_technologies_from_text(part):
                if technology not in technologies:
                    technologies.append(technology)
                    
    for line in entry_lines:
        standalone = detect_standalone_technologies(line)

        for technology in standalone:
            if technology not in technologies:
                technologies.append(technology)
    return technologies

# ---------------------project description detection-------------------------------
def split_project_description_label(
    line: str,
) -> tuple[str | None, str]:
    """Return a recognized description label and its remaining text."""
    cleaned = normalize_text(line)
    match = _DESCRIPTION_LABEL_RE.match(cleaned)

    if match is None:
        return None, cleaned

    label = match.group("label").casefold()
    description = match.group("description").strip()

    return label, description


def split_inline_project_description(
    line: str,
) -> tuple[str | None, str]:
    """Split a project title and action-led description sharing one line."""
    cleaned = normalize_text(line)
    content = remove_bullet(cleaned) if is_bullet_line(cleaned) else cleaned

    if ":" not in content:
        return None, cleaned

    description_label, _ = split_project_description_label(content)

    if description_label is not None or is_metadata_line(content):
        return None, cleaned

    title, description = (
        part.strip()
        for part in content.split(":", maxsplit=1)
    )

    title_words = title.split()
    first_letter = re.search(r"[A-Za-z]", title)

    if (
        not 2 <= len(title_words) <= 8
        or first_letter is None
        or not first_letter.group().isupper()
        or not looks_like_plain_project_header(title)
        or starts_with_description_starter(title)
        or is_standalone_date_line(title)
        or is_standalone_technology_line(title)
        or _URL_RE.search(title) is not None
    ):
        return None, cleaned

    if not description or not starts_with_description_starter(description):
        return None, cleaned

    return title, description

def is_explicit_description_line(line: str) -> bool:
    """Return whether a line begins with a recognized description label."""
    label, _ = split_project_description_label(line)
    return label is not None

def is_project_description_boundary(line: str) -> bool:
    """Return whether a standalone structural line ends a description block."""
    normalized = normalize_text(line).strip()

    if not normalized:
        return False

    content = (
        remove_bullet(normalized)
        if is_bullet_line(normalized)
        else normalized
    )
    description_label, _ = split_project_description_label(content)

    if description_label is not None:
        return False

    inline_name, _ = split_inline_project_description(content)

    if inline_name is not None:
        return False

    is_header_boundary = looks_like_project_header(normalized) and (
        detect_explicit_project_name(content) is not None
        or looks_like_inline_project_header(content)
        or len(content.split()) <= 4
    )

    return bool(
        is_metadata_line(content)
        or is_standalone_date_line(content)
        or is_standalone_technology_line(content)
        or _URL_RE.fullmatch(content) is not None
        or is_header_boundary
    )

def is_project_description_bullet(line: str) -> bool:
    """Return whether a bullet contains project-description content."""
    normalized = normalize_text(line).strip()

    if not normalized or not is_bullet_line(normalized):
        return False

    content = remove_bullet(normalized)

    if not content:
        return False

    return not is_project_description_boundary(normalized)

def is_unbulleted_description_start(line: str) -> bool:
    """Return whether an unbulleted line can start a description block."""
    normalized = normalize_text(line).strip()

    if not normalized or is_bullet_line(normalized):
        return False

    if is_explicit_description_line(normalized):
        return True

    inline_name, _ = split_inline_project_description(normalized)

    if inline_name is not None:
        return True

    if is_project_description_boundary(normalized):
        return False

    if starts_with_description_starter(normalized):
        return True

    return len(normalized.split()) >= 4

def detect_project_description_blocks(entry_lines: list[str],) -> list[list[int]]:
    """Group indices belonging to each project-description block."""
    blocks: list[list[int]] = []
    current_block: list[int] = []
    description_section_open = False
    header_index = next(
        (
            index
            for index, line in enumerate(entry_lines)
            if project_header_content(line) is not None
            and split_inline_project_description(line)[0] is None
        ),
        None,
    )

    for index, raw_line in enumerate(entry_lines):
        line = normalize_text(raw_line).strip()

        if not line:
            continue

        if index == header_index:
            continue

        content = remove_bullet(line) if is_bullet_line(line) else line
        description_label, labeled_text = split_project_description_label(
            content
        )

        if description_label is not None:
            if current_block:
                blocks.append(current_block)
                current_block = []

            description_section_open = True

            if labeled_text:
                current_block = [index]

            continue

        inline_name, _ = split_inline_project_description(content)

        if inline_name is not None:
            if current_block:
                blocks.append(current_block)

            current_block = [index]
            description_section_open = True
            continue

        if is_project_description_boundary(line):
            if current_block:
                blocks.append(current_block)
                current_block = []

            description_section_open = False
            continue

        if is_project_description_bullet(line):
            if current_block:
                blocks.append(current_block)

            current_block = [index]
            description_section_open = True
            continue

        if current_block:
            current_block.append(index)
            continue

        if description_section_open or is_unbulleted_description_start(line):
            current_block = [index]

    if current_block:
        blocks.append(current_block)

    return blocks

def clean_project_description_line(
    line: str,
    *,
    first_line: bool,
) -> str:
    """Clean one detected description line without altering its content."""
    cleaned = normalize_text(line)

    if not cleaned or not first_line:
        return cleaned

    if is_bullet_line(cleaned):
        cleaned = remove_bullet(cleaned)

    description_label, description = split_project_description_label(
        cleaned
    )

    if description_label is not None:
        return description

    inline_name, description = split_inline_project_description(cleaned)

    if inline_name is not None:
        return description

    return cleaned

def extract_project_descriptions(entry_lines: list[str],) -> list[str]:
    """Extract one cleaned description string from each detected block."""
    descriptions: list[str] = []
    seen: set[str] = set()

    for block in detect_project_description_blocks(entry_lines):
        parts = [
            clean_project_description_line(
                entry_lines[line_index],
                first_line=position == 0,
            )
            for position, line_index in enumerate(block)
        ]
        description = normalize_text(
            " ".join(part for part in parts if part)
        )

        if not description:
            continue

        key = description.casefold()

        if key in seen:
            continue

        seen.add(key)
        descriptions.append(description)

    return descriptions

# --------------------Project Parsing----------------------
def parse_project_entry(entry_lines: list[str]) -> ProjectRecord:
    record = ProjectRecord(
        name=detect_project_name(entry_lines),
        technologies=detect_project_technologies(entry_lines),
        descriptions=extract_project_descriptions(entry_lines),
        raw_lines=entry_lines.copy(),
    )

    date = detect_project_dates(entry_lines)
    if date is not None:
        record.start_date = date.start_date
        record.end_date = date.end_date
        record.is_current = date.is_current

    links = detect_project_urls(entry_lines)
    record.github_url = links.github_url
    record.live_url = links.live_url
    record.other_urls = links.other_urls
    return record


def parse_projects(project_lines: list[str]) -> list[ProjectRecord]:
    return [
        parse_project_entry(entry_lines)
        for entry_lines in group_project_entries(project_lines)
    ]
