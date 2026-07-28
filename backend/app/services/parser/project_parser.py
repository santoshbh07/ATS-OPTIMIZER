import re
from dataclasses import dataclass, field
from .date_parser import NormalizedDate, DateCandidate, remove_date_candidates

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

_HEADER_SEPARATOR_RE = re.compile(r"\s+(?:\||-|–|—)\s+")
_BULLET_RE = re.compile(r"^\s*(?:[•▪◦●*]|-\s+)")
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

_TECHNOLOGY_LABEL_RE = re.compile(
    rf"^\s*(?:{_TECHNOLOGY_LABEL_PATTERN})"
    rf"\s*:\s*(?P<technologies>.+?)\s*$",
    re.IGNORECASE,
)


def is_bullet_line(line: str) -> bool:
    return bool(_BULLET_RE.match(line))

def looks_like_inline_project_header(line: str) -> bool:
    cleaned = line.strip()

    if not cleaned:
        return False
    
    if is_bullet_line(cleaned):
        return False
    
    return bool(_HEADER_SEPARATOR_RE.search(cleaned))

def group_project_entries(project_lines: list[str],) -> list[list[str]]:
    entries: list[list[str]] = []
    current_entry: list[str] = []
    description_started = False
    
    for raw_line in project_lines:
        line = raw_line.strip()
         
        if not line:
            continue
        
        if is_bullet_line(line):
            current_entry.append(line)
            description_started = True
            continue
        
        is_new_header = looks_like_inline_project_header(line)

        if current_entry and description_started and is_new_header:
            entries.append(current_entry)
            current_entry = [line]
            description_started = False
        else:
            current_entry.append(line)
        
    if current_entry:
        entries.append(current_entry)


    return entries

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

def is_metadata_line(line: str) -> bool:
    return bool(_METADATA_LABEL_RE.match(line))

def is_url_line(line:str) -> bool:
    lowered = line.casefold()
    return (
        "http://" in lowered
        or "https://" in lowered
        or "github.com/" in lowered
        or "www." in lowered
    )

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
        
        
        return line
    
    return None
# ---------------------------------------------------------------------------------



