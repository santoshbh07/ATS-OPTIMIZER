from .date_parser import DateCandidate, detect_date_candidates, NormalizedDate
from .text_utils import normalize_text, strip_bullet
from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class DegreeDefinition:
    canonical_name: str
    level: str
    patterns: tuple[re.Pattern[str], ...]


def _degree_patterns(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)


_TOKEN_START = r"(?<![A-Za-z0-9])"
_TOKEN_END = r"(?![A-Za-z0-9])"

DEGREE_DEFINITIONS = (
    DegreeDefinition(
        "Bachelor of Business Administration", "bachelor",
        _degree_patterns(
            r"\bBachelor\s+of\s+Business\s+Administration\b",
            rf"{_TOKEN_START}B\.?\s*B\.?\s*A\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Master of Business Administration", "master",
        _degree_patterns(
            r"\bMaster\s+of\s+Business\s+Administration\b",
            rf"{_TOKEN_START}M\.?\s*B\.?\s*A\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Associate of Applied Science", "associate",
        _degree_patterns(
            r"\bAssociate\s+of\s+Applied\s+Science\b",
            rf"{_TOKEN_START}A\.?\s*A\.?\s*S\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
    "Bachelor of Engineering",
    "bachelor",
    _degree_patterns(
        r"\bBachelor\s+of\s+Engineering\b",
        (
            r"\bBachelor\s+of\s+"
            r"(?:[A-Za-z]+\s+and\s+)?"
            r"[A-Za-z]+\s+Engineering\b"
        ),
        rf"{_TOKEN_START}(?:B\.\s*E\.?|B\s+E\.?|(?-i:BE)){_TOKEN_END}",
    ),
    ),
    DegreeDefinition(
        "Bachelor of Technology", "bachelor",
        _degree_patterns(
            r"\bBachelor\s+of\s+Technology\b",
            rf"{_TOKEN_START}B\.?\s*Tech\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
    "Master of Engineering",
    "master",
    _degree_patterns(
        r"\bMaster\s+of\s+Engineering\b",
        r"\bMaster\s+of\s+[A-Za-z]+\s+Engineering\b",
        rf"{_TOKEN_START}(?:M\.\s*E\.?|M\s+E\.?|(?-i:ME)|M\.?\s*Eng\.?){_TOKEN_END}",
    ),
    ),
    DegreeDefinition(
        "Doctor of Philosophy", "doctorate",
        _degree_patterns(
            r"\bDoctor\s+of\s+Philosophy\b",
            rf"{_TOKEN_START}Ph\.?\s*D\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Doctor of Education", "doctorate",
        _degree_patterns(
            r"\bDoctor\s+of\s+Education\b",
            rf"{_TOKEN_START}Ed\.?\s*D\.?{_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Bachelor of Science", "bachelor",
        _degree_patterns(
            r"\bBachelor\s+of\s+Science\b",
            rf"{_TOKEN_START}(?:B\.\s*S\.?|B\s+S\.?|(?-i:BS)|B\.?\s*Sc\.?){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Bachelor of Arts", "bachelor",
        _degree_patterns(
            r"\bBachelor\s+of\s+Arts\b",
            rf"{_TOKEN_START}(?:B\.\s*A\.?|B\s+A\.?|(?-i:BA)){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Master of Science", "master",
        _degree_patterns(
            r"\bMaster\s+of\s+Science\b",
            rf"{_TOKEN_START}(?:M\.\s*S\.?|M\s+S\.?|(?-i:MS)|M\.?\s*Sc\.?){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Master of Arts", "master",
        _degree_patterns(
            r"\bMaster\s+of\s+Arts\b",
            rf"{_TOKEN_START}(?:M\.\s*A\.?|M\s+A\.?|(?-i:MA)){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Associate of Science", "associate",
        _degree_patterns(
            r"\bAssociate\s+of\s+Science\b",
            rf"{_TOKEN_START}(?:A\.\s*S\.?|A\s+S\.?|(?-i:AS)){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "Associate of Arts", "associate",
        _degree_patterns(
            r"\bAssociate\s+of\s+Arts\b",
            rf"{_TOKEN_START}(?:A\.\s*A\.?|A\s+A\.?|(?-i:AA)){_TOKEN_END}",
        ),
    ),
    DegreeDefinition(
        "High School Diploma", "high_school",
        _degree_patterns(r"\bHigh\s+School\s+Diploma\b"),
    ),
    DegreeDefinition(
        "GED", "high_school",
        _degree_patterns(rf"{_TOKEN_START}G\.?\s*E\.?\s*D\.?{_TOKEN_END}"),
    ),
    DegreeDefinition(
        "Doctoral Degree", "doctorate",
        _degree_patterns(r"\bDoctoral\s+Degree\b"),
    ),
    DegreeDefinition(
        "Doctorate", "doctorate",
        _degree_patterns(r"\bDoctorate\b"),
    ),
    DegreeDefinition(
        "Associate Degree", "associate",
        _degree_patterns(r"\bAssociate(?:'s)?\s+Degree\b"),
    ),
    DegreeDefinition(
        "Bachelor's Degree", "bachelor",
        _degree_patterns(r"\bBachelor(?:'s|s)\s+Degree\b"),
    ),
    DegreeDefinition(
        "Master's Degree", "master",
        _degree_patterns(r"\bMaster(?:'s|s)\s+Degree\b"),
    ),
)

STUDY_FIELD_ALIASES: dict[str, str] = {
    "civil and environmental engineering": "Civil and Environmental Engineering",
    "management information systems": "Management Information Systems",
    "business administration": "Business Administration",
    "artificial intelligence": "Artificial Intelligence",
    "electrical engineering": "Electrical Engineering",
    "mechanical engineering": "Mechanical Engineering",
    "software engineering": "Software Engineering",
    "computer engineering": "Computer Engineering",
    "chemical engineering": "Chemical Engineering",
    "information technology": "Information Technology",
    "information systems": "Information Systems",
    "civil engineering": "Civil Engineering",
    "political science": "Political Science",
    "computer sciences": "Computer Science",
    "computer science": "Computer Science",
    "business admin": "Business Administration",
    "data analytics": "Data Analytics",
    "cybersecurity": "Cybersecurity",
    "machine learning": "Machine Learning",
    "data science": "Data Science",
    "communications": "Communications",
    "mathematics": "Mathematics",
    "math": "Mathematics",
    "statistics": "Statistics",
    "psychology": "Psychology",
    "sociology": "Sociology",
    "accounting": "Accounting",
    "economics": "Economics",
    "marketing": "Marketing",
    "management": "Management",
    "chemistry": "Chemistry",
    "comp sci": "Computer Science",
    "finance": "Finance",
    "physics": "Physics",
    "biology": "Biology",
    "history": "History",
    "english": "English",
    "nursing": "Nursing",
    "building engineering": "Building Engineering",
    "environmental engineering": "Environmental Engineering",
    "construction management": "Construction Management",
}

SHORT_STUDY_FIELD_ALIASES: dict[str, str] = {
    "cs": "Computer Science",
    "it": "Information Technology",
    "is": "Information Systems",
    "mis": "Management Information Systems",
    "ee": "Electrical Engineering",
    "me": "Mechanical Engineering",
}

_EXPLICIT_FIELD_PATTERN = re.compile(
    r"\b(?:"
    r"double\s+major|"
    r"major|"
    r"field\s+of\s+study|"
    r"area\s+of\s+study|"
    r"program|"
    r"specialization|"
    r"concentration|"
    r"emphasis|"
    r"focus"
    r")"
    r"\s*(?::|\bin\b)\s*(?P<field>.+)",
    re.IGNORECASE,
)
_CANDIDATE_STOP_PATTERN = re.compile(
    r"(?:[,|;/]|\s+[-—–]\s+)\s*"
    r"(?:gpa|minor(?:s)?|concentration|specialization|emphasis|focus|"
    r"honors?|expected|graduated|graduation|coursework|relevant\s+coursework)\b",
    re.IGNORECASE,
)
_ACADEMIC_UNIT_PATTERN = re.compile(
    r"\b(?:university|college|school|department|faculty|institute|academy)\b",
    re.IGNORECASE,
)
GPA_PATTERN = re.compile(
    r"\b(?:gpa|grade\s+point\s+average)\b"
    r"\s*[:=\-]?\s*"
    r"(?P<score>\d+(?:\.\d+)?)"
    r"(?:\s*/\s*(?P<scale>\d+(?:\.\d+)?))?",
    re.IGNORECASE,
)
_MINOR_PREFIX_PATTERN = re.compile(
    r"\b(?:double\s+)?minors?\s*(?:\bin\b|[:=\-–—])\s*(?P<fields>.+)",
    re.IGNORECASE,
)
_MINOR_SUFFIX_PATTERN = re.compile(
    r"(?P<field>[A-Za-z][A-Za-z &'-]*?)\s+minor\b",
    re.IGNORECASE,
)
_MINOR_METADATA_PATTERN = re.compile(
    r"(?:[,|]|\s+[-–—]\s+)\s*"
    r"(?:gpa|honors?|dean's\s+list|coursework|relevant\s+coursework|"
    r"expected|graduated|graduation|certificate|certification)\b",
    re.IGNORECASE,
)


def extract_date_candidates(line: str) -> list[DateCandidate]:
    return detect_date_candidates(line)


@dataclass
class DegreeRecord:
    institution: str | None = None
    degree_name: str | None = None
    degree_level: str | None = None
    fields_of_study: list[str] = field(default_factory=list)
    
    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_expected: bool = False
    is_current: bool = False
    
    gpa: str | None = None
    honors: list[str] = field(default_factory=list)
    minors: list[str] = field(default_factory=list)
    coursework: list[str] = field(default_factory=list)

    raw_lines: list[str] = field(default_factory=list)

INSTITUTION_KEYWORDS = {
    "university",
    "college",
    "institute",
    "academy",
    "polytechnic",
    "school",
}

US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

US_STATE_NAMES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming", "district of columbia",
}

COUNTRY_NAMES = {
    "australia", "canada", "china", "france", "germany", "india",
    "ireland", "italy", "japan", "mexico", "nepal", "new zealand",
    "singapore", "south korea", "spain", "united kingdom",
    "united states", "united states of america",
}

ACADEMIC_UNIT_TERMS = {
    "arts and sciences", "business", "computer science", "education",
    "electrical engineering", "engineering", "graduate studies",
    "information technology", "law", "medicine", "nursing", "science",
}

NON_INSTITUTION_PREFIXES = (
    "department of ", "faculty of ", "division of ",
)

DEGREE_LINE_PATTERN = re.compile(
    r"^(?:associate|bachelor|master|doctor|ph\.?d\.?|b\.?[as]\.?|"
    r"m\.?[as]\.?)\b",
    re.IGNORECASE,
)

def looks_like_degree_line(line: str) -> bool:
    cleaned_line = normalize_text(_clean_line(line))
    return DEGREE_LINE_PATTERN.match(cleaned_line) is not None

def _clean_line(line: str) -> str:
    return strip_bullet(line).strip()


def _looks_like_location(value: str) -> bool:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) < 2 or any(not part for part in parts):
        return False

    city = parts[0]
    region = parts[-1]
    normalized_region = region.casefold()
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", city):
        return False
    if any(term in city.casefold() for term in ACADEMIC_UNIT_TERMS):
        return False

    return (
        region.upper() in US_STATE_ABBREVIATIONS
        or normalized_region in US_STATE_NAMES
        or normalized_region in COUNTRY_NAMES
    )


def split_institution_and_location(line: str) -> tuple[str, str | None]:
    """Split a line only when its trailing text confidently resembles a location."""
    cleaned_line = _clean_line(line)
    if not cleaned_line:
        return "", None

    for match in re.finditer(r"\s+(?:\||-|–|—)\s+", cleaned_line):
        location = cleaned_line[match.end():].strip()
        if _looks_like_location(location):
            return cleaned_line[:match.start()].strip(), location

    comma_positions = [
        index for index, character in enumerate(cleaned_line)
        if character == ","
    ]
    for comma_index in comma_positions:
        location = cleaned_line[comma_index + 1:].strip()
        if _looks_like_location(location):
            return cleaned_line[:comma_index].strip(), location

    return cleaned_line, None


def _score_institution_candidate(line: str) -> int:
    normalized = line.casefold()
    if not normalized or normalized == "education":
        return 0
    if normalized.startswith(NON_INSTITUTION_PREFIXES):
        return 0
    if DEGREE_LINE_PATTERN.match(normalized):
        return 0
    if re.match(r"^(?:gpa|coursework|relevant coursework|honors?|minor)\b", normalized):
        return 0
    if detect_date_candidates(line):
        date_text = " ".join(
            line[candidate.start_index:candidate.end_index]
            for candidate in detect_date_candidates(line)
        )
        if normalize_text(date_text).casefold() == normalized:
            return 0

    subunit_match = re.match(r"^(college|school) of (.+)$", normalized)
    if subunit_match and subunit_match.group(2) in ACADEMIC_UNIT_TERMS:
        return 0

    if re.search(r"\bcommunity college\b", normalized):
        return 8
    if re.search(r"\binstitute of technology\b", normalized):
        return 8
    if re.search(r"\bpolytechnic\b", normalized):
        return 7
    if re.match(r"^university of \S+", normalized):
        return 8
    if re.search(r"\b(?:state )?university\b", normalized):
        return 7
    if re.match(r"^college of .+", normalized):
        return 6
    if re.match(r"^school of .+", normalized):
        return 5
    if re.search(r"\S+\s+college$", normalized):
        return 6
    if re.search(r"\S+\s+(?:institute|academy)$", normalized):
        return 5
    return 0


def detect_institution(entry: str | list[str]) -> str | None:
    """Return the cleaned, highest-confidence institution line, or ``None``."""
    lines = [entry] if isinstance(entry, str) else entry
    candidates: list[tuple[int, str]] = []

    for raw_line in lines:
        institution_line, _ = split_institution_and_location(raw_line)
        score = _score_institution_candidate(institution_line)
        if score > 0:
            candidates.append((score, institution_line))

    if not candidates:
        return None

    return max(candidates, key=lambda candidate: candidate[0])[1]


def detect_location(entry: list[str]) -> str | None:
    """Return a confident education location from a combined or separate line."""
    for raw_line in entry:
        _, location = split_institution_and_location(raw_line)
        if location is not None:
            return location

    for raw_line in entry:
        cleaned_line = _clean_line(raw_line)
        if _looks_like_location(cleaned_line):
            return cleaned_line

    return None

def group_education_entries(
    education_lines: list[str],
) -> list[list[str]]:
    grouped_entries: list[list[str]] = []
    current_group: list[str] = []

    current_group_has_institution = False
    current_group_has_degree_line = False

    for line in education_lines:
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        institution = detect_institution(cleaned_line)
        has_degree_line = looks_like_degree_line(cleaned_line)

        starts_new_entry = (
            institution is not None
            and current_group_has_institution
        ) or (
            has_degree_line
            and current_group_has_degree_line
        )

        if starts_new_entry and current_group:
            grouped_entries.append(current_group)
            current_group = []
            current_group_has_institution = False
            current_group_has_degree_line = False

        current_group.append(cleaned_line)

        if institution is not None:
            current_group_has_institution = True

        if has_degree_line:
            current_group_has_degree_line = True

    if current_group:
        grouped_entries.append(current_group)

    return grouped_entries

def _find_degree_match(
    line: str,
) -> tuple[DegreeDefinition, re.Match[str], str] | None:
    normalized_line = normalize_text(line)
    for definition in DEGREE_DEFINITIONS:
        for pattern in definition.patterns:
            match = pattern.search(normalized_line)
            if match is not None:
                return definition, match, normalized_line
    return None


def detect_degree(entry: str | list[str]) -> tuple[str, str] | None:
    lines = [entry] if isinstance(entry, str) else entry
    for line in lines:
        degree_match = _find_degree_match(line)
        if degree_match is not None:
            definition, _, _ = degree_match
            return definition.canonical_name, definition.level

    return None


def _trim_study_field_candidate(candidate: str) -> str:
    stop_match = _CANDIDATE_STOP_PATTERN.search(candidate)
    if stop_match is not None:
        candidate = candidate[:stop_match.start()]

    dates = detect_date_candidates(candidate)
    if dates:
        candidate = candidate[:dates[0].start_index]

    return candidate.strip(" \t,;:|/()[]-—–")


def _extract_degree_adjacent_candidate(line: str) -> str | None:
    degree_match = _find_degree_match(line)
    if degree_match is None:
        return None

    _, match, normalized_line = degree_match
    after = re.sub(
        r"^\s*(?:[,;:|/()\-—–]|\bin\b)*\s*",
        "",
        normalized_line[match.end():],
        flags=re.IGNORECASE,
    )
    after = _trim_study_field_candidate(after)
    if after:
        return after

    before = _trim_study_field_candidate(normalized_line[:match.start()])
    before = re.sub(
        r"^(?:expected|pursuing|candidate\s+for)\b.*?[,;:|/()\-—–]\s*",
        "",
        before,
        flags=re.IGNORECASE,
    )
    return before or None


def _normalize_study_fields(
    candidate: str,
    *,
    strong_context: bool,
) -> list[str]:
    normalized = normalize_text(candidate).casefold().strip()
    if not normalized:
        return []

    aliases: dict[str, str] = dict(STUDY_FIELD_ALIASES)

    if strong_context:
        aliases.update(SHORT_STUDY_FIELD_ALIASES)

    matches: list[tuple[int, int, str]] = []

    for alias, canonical in aliases.items():
        pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"

        for match in re.finditer(pattern, normalized):
            matches.append(
                (
                    match.start(),
                    match.end(),
                    canonical,
                )
            )

    # Earlier matches come first. When two aliases begin at the same
    # position, prefer the longer alias.
    matches.sort(
        key=lambda item: (
            item[0],
            -(item[1] - item[0]),
        )
    )

    selected_fields: list[str] = []
    seen_fields: set[str] = set()
    occupied_until = -1

    for start, end, canonical in matches:
        # Ignore aliases contained inside a longer selected alias.
        if start < occupied_until:
            continue

        occupied_until = end
        key = canonical.casefold()

        if key not in seen_fields:
            seen_fields.add(key)
            selected_fields.append(canonical)

    return selected_fields


def normalize_academic_field(candidate: str) -> str | None:
    """Return a canonical field only when the complete candidate is a known alias."""
    normalized = normalize_text(candidate).casefold().strip()
    if normalized in STUDY_FIELD_ALIASES:
        return STUDY_FIELD_ALIASES[normalized]
    return SHORT_STUDY_FIELD_ALIASES.get(normalized)


def detect_gpa(line: str) -> str | None:
    normalized_line = normalize_text(line).strip()
    if not normalized_line:
        return None

    for match in GPA_PATTERN.finditer(normalized_line):
        if re.search(r"\bmajor\s*$", normalized_line[:match.start()], re.IGNORECASE):
            continue

        score_text = match.group("score")
        scale_text = match.group("scale")
        if scale_text is not None and float(score_text) > float(scale_text):
            continue
        return score_text

    return None


def _trim_minor_candidate(candidate: str) -> str:
    stop_positions: list[int] = []
    metadata_match = _MINOR_METADATA_PATTERN.search(candidate)
    if metadata_match is not None:
        stop_positions.append(metadata_match.start())

    dates = detect_date_candidates(candidate)
    if dates:
        stop_positions.append(dates[0].start_index)
    if stop_positions:
        candidate = candidate[:min(stop_positions)]

    return candidate.strip(" \t,;:|/()[]-–—")


def _minor_values(candidate: str) -> list[str]:
    values: list[str] = []
    for part in re.split(r"\s*[,;]\s*", candidate):
        cleaned = part.strip()
        if not cleaned:
            continue

        and_parts = [
            value.strip() for value in re.split(r"\s+\band\b\s+", cleaned, flags=re.IGNORECASE)
        ]
        normalized_and_parts = [normalize_academic_field(value) for value in and_parts]
        if len(and_parts) > 1 and all(normalized_and_parts):
            values.extend(value for value in normalized_and_parts if value is not None)
        else:
            values.append(normalize_academic_field(cleaned) or cleaned)

    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            unique_values.append(value)
    return unique_values


def detect_minors(line: str) -> list[str]:
    normalized_line = normalize_text(_clean_line(line))
    if not normalized_line:
        return []

    prefix_match = _MINOR_PREFIX_PATTERN.search(normalized_line)
    if prefix_match is not None:
        candidate = _trim_minor_candidate(prefix_match.group("fields"))
        if candidate.casefold() in {"none", "n/a", "not declared", "undeclared"}:
            return []
        return _minor_values(candidate) if candidate else []

    suffix_match = _MINOR_SUFFIX_PATTERN.fullmatch(normalized_line)
    if suffix_match is None:
        return []
    canonical = normalize_academic_field(suffix_match.group("field"))
    return [canonical] if canonical is not None else []


def detect_study_fields(line: str) -> list[str]:
    normalized_line = normalize_text(_clean_line(line))

    if not normalized_line:
        return []

    candidates: list[str] = []

    explicit_match = _EXPLICIT_FIELD_PATTERN.search(normalized_line)
    if explicit_match is not None:
        explicit_candidate = _trim_study_field_candidate(
            explicit_match.group("field")
        )

        if explicit_candidate:
            candidates.append(explicit_candidate)

    degree_candidate = _extract_degree_adjacent_candidate(
        normalized_line
    )

    if degree_candidate:
        candidates.append(degree_candidate)

    detected_fields: list[str] = []
    seen_fields: set[str] = set()

    for candidate in candidates:
        if _ACADEMIC_UNIT_PATTERN.search(candidate):
            continue

        if _looks_like_location(candidate):
            continue

        for field_name in _normalize_study_fields(
            candidate,
            strong_context=True,
        ):
            key = field_name.casefold()

            if key not in seen_fields:
                seen_fields.add(key)
                detected_fields.append(field_name)

    return detected_fields

def parse_degree_entry(entry_lines: list[str]) -> DegreeRecord:
    record = DegreeRecord(raw_lines=entry_lines.copy())

    record.institution = detect_institution(entry_lines)

    degree = detect_degree(entry_lines)
    if degree is not None:
        record.degree_name, record.degree_level = degree

    explicit_lines = [
        line
        for line in entry_lines
        if _EXPLICIT_FIELD_PATTERN.search(normalize_text(line))
    ]

    non_explicit_lines = [
        line
        for line in entry_lines
        if not _EXPLICIT_FIELD_PATTERN.search(normalize_text(line))
    ]

    seen_fields: set[str] = set()

    for line in [*explicit_lines, *non_explicit_lines]:
        for field_name in detect_study_fields(line):
            key = field_name.casefold()

            if key not in seen_fields:
                seen_fields.add(key)
                record.fields_of_study.append(field_name)

    seen_minors: set[str] = set()

    for line in entry_lines:
        if record.gpa is None:
            record.gpa = detect_gpa(line)

        for minor in detect_minors(line):
            key = minor.casefold()

            if key not in seen_minors:
                seen_minors.add(key)
                record.minors.append(minor)

    return record

def parse_education(
    education_lines: list[str],
) -> list[DegreeRecord]:
    grouped_entries = group_education_entries(education_lines)

    return [
        parse_degree_entry(entry_lines)
        for entry_lines in grouped_entries
    ]