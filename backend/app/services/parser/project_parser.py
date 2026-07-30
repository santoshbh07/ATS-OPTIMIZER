import re
from dataclasses import dataclass, field
from .date_parser import NormalizedDate, DateCandidate, remove_date_candidates, detect_date_candidates, DetectorConfig
from .text_utils import normalize_text

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

KNOWN_TECHNOLOGIES = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "react",
    "next.js",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "spring boot",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "docker",
    "aws",
    "git",
    "pandas",
    "numpy",
    "scikit-learn",
}

TECHNOLOGY_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
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
}

_HEADER_SEPARATOR_RE = re.compile(
    r"\s+(?:\||-|\u2013|\u2014)\s+"
)
_BULLET_RE = re.compile(
    r"^\s*(?:[\u2022\u25aa\u25e6\u25cf*]|-\s+)"
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
    r"duration|description"
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

def is_bullet_line(line: str) -> bool:
    return bool(_BULLET_RE.match(line))

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
    line = line.strip()

    for bullet in ("- ", "* ", "• ", "- ", "— "):
        if line.startswith(bullet):
            return line.removeprefix(bullet).strip()

    return line

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

    if is_url_line(content):
        return False

    if is_standalone_date_line(content):
        return False

    if is_standalone_technology_line(content):
        return False

    if starts_with_description_starter(content):
        return False

    if looks_like_inline_project_header(content):
        return True

    return looks_like_plain_project_header(line)
        
def group_project_entries(project_lines: list[str],) -> list[list[str]]:
    grouped_projects: list[list[str]] = []
    current_group: list[str] = []

    current_group_has_header = False
    current_group_has_body = False

    for raw_line in project_lines:
        line = normalize_text(raw_line).strip()

        if not line:
            continue

        is_header = looks_like_project_header(line)

        content = (
            remove_bullet(line).strip()
            if is_bullet_line(line)
            else line
        )

        is_bulleted_header = (is_bullet_line(line) and is_header)

        is_inline_header = (is_header and looks_like_inline_project_header(content))

        starts_new_project = (
            is_header and current_group_has_header and (
                current_group_has_body
                or is_bulleted_header
                or is_inline_header
            )
        )

        if starts_new_project:
            grouped_projects.append(current_group)

            current_group = []
            current_group_has_header = False
            current_group_has_body = False

        current_group.append(line)

        if is_header:
            current_group_has_header = True
        elif current_group_has_header:
            current_group_has_body = True

    if current_group:
        grouped_projects.append(current_group)

    return grouped_projects

def detect_explicit_project_name(line: str) -> str | None:
    match = _PROJECT_NAME_LABEL_RE.match(line)

    if match is None:
        return None

    name = match.group("name").strip()
    return name or None

def detect_name_from_header(line: str) -> str | None:
    if is_bullet_line(line):
        return None
    
    parts = _HEADER_SEPARATOR_RE.split(line.strip(), maxsplit=1)

    if len(parts) < 2:
        return None
    
    candidate = parts[0].strip()
    return candidate or None

# ----------------------project name detection complete function-------------------
def detect_project_name(entry_lines: list[str]) -> str | None:
    for line in entry_lines:
        name = detect_explicit_project_name(line)

        if name is not None:
            return name
        
    for line in entry_lines:
        name = detect_name_from_header(line)
        if name is not None:
            return name
        
    # this is for plain project name
    for raw_line in entry_lines:
        line = raw_line.strip()

        if not line:
            continue
        if is_bullet_line(line):
            continue
        if is_metadata_line(line):
            continue
        if is_url_line(line):
            continue
        line_without_date = remove_date_candidates(line)
        return line_without_date
    
    return None
# ---------------------------------------------------------------------------------

def detect_project_dates(entry_lines: list[str],) -> DateCandidate | None:
    candidates: list[DateCandidate] = []

    for raw_line in entry_lines:
        line = raw_line.strip()
        if not line:
            continue
        if is_bullet_line(line): #avaids interpreting years mentioned inside description bullets
            continue
        candidates.extend(detect_date_candidates(line))
    if not candidates:
        return None
    
    return max(
        candidates,
        key=lambda candidate: candidate.confidence,
    )

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
        lowered_line = line.casefold()
    
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

            elif any(
                label in lowered_line
                for label in ("live", "demo", "website")
            ):
                if links.live_url is None:
                    links.live_url = url
                else:
                    links.other_urls.append(url)

            else:
                links.other_urls.append(url)

    return links

def normalize_technology_name(technology: str,) -> str | None:
    cleaned = technology.strip()
    lookup = cleaned.casefold()
    
    if not cleaned:
        return None
    if lookup in TECHNOLOGY_ALIASES:
        return TECHNOLOGY_ALIASES[lookup]
    if lookup not in KNOWN_TECHNOLOGIES:
        return None
    return cleaned

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
        line = raw_line.strip()
        match = _TECHNOLOGY_LABEL_RE.match(line)
        if not match:
            continue
        
        technology_text = match.group("technologies")
        
        for technology in extract_technologies_from_text(technology_text):
            if technology not in technologies:
                technologies.append(technology)
                
    # technologies inline with project headers
    for line in entry_lines:
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