from .date_parser import DateCandidate, detect_date_candidates, NormalizedDate, remove_date_candidates
from .text_utils import normalize_text, strip_bullet
from dataclasses import dataclass, field
import re

_EXPECTED_MARKER_RE = re.compile(
    r"\b(?:expected(?:\s+graduation)?|anticipated)\b",
    re.IGNORECASE,
)


@dataclass
class DegreeRecord:
    institution: str | None = None
    degree_name: str | None = None
    degree_level: str | None = None
    fields_of_study: list[str] = field(default_factory=list)
    specializations: list[str] = field(default_factory=list)
    
    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_expected: bool = False
    is_current: bool = False
    
    gpa: str | None = None
    honors: list[str] = field(default_factory=list)
    minors: list[str] = field(default_factory=list)
    coursework: list[str] = field(default_factory=list)

    raw_lines: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class DegreeDefinition:
    canonical_name: str
    level: str
    patterns: tuple[re.Pattern[str], ...]

_TOKEN_START = r"(?<![A-Za-z0-9])"
_TOKEN_END = r"(?![A-Za-z0-9])"

_ENGINEERING_WORD = r"[A-Za-z][A-Za-z/&'-]*"

_ENGINEERING_FIELD = (
    rf"(?P<engineering_field>"
    rf"{_ENGINEERING_WORD}"
    rf"(?:\s+(?:{_ENGINEERING_WORD}|&)){{0,5}}?"
    rf")"
)

_SPECIALIZATION_MARKERS = (
    r"speciali[sz]ation",
    r"speciali[sz]ed\s+in",
    r"concentration",
    r"focus",
    r"emphasis",
    r"track",
)


def _degree_patterns(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
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
        r"\b(?P<degree_name>Bachelor\s+of\s+Engineering)\b",
        (
            rf"\b(?P<degree_name>"
            rf"Bachelor\s+of\s+"
            rf"{_ENGINEERING_FIELD}\s+Engineering"
            rf")\b"
        ),
        rf"{_TOKEN_START}"
        rf"(?:B\.\s*E\.?|B\s+E\.?|(?-i:BE))"
        rf"{_TOKEN_END}",
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
        r"\b(?P<degree_name>Master\s+of\s+Engineering)\b",
        (
            rf"\b(?P<degree_name>"
            rf"Master\s+of\s+"
            rf"{_ENGINEERING_FIELD}\s+Engineering"
            rf")\b"
        ),
        rf"{_TOKEN_START}"
        rf"(?:M\.\s*E\.?|M\s+E\.?|(?-i:ME)|M\.?\s*Eng\.?)"
        rf"{_TOKEN_END}",
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

# ==============Study Field helpers start here=================
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

# Strong labels that explicitly introduce a field of study.
_FIELD_LABEL_RE = re.compile(
    r"""
    ^\s*
    (?P<label>
        double\s+major |
        majors? |
        field\s+of\s+study |
        area\s+of\s+study |
        programs? |
        concentrations? |
        speciali[sz]ations? |
        emphasis |
        focus
    )
    \s*(?::|\bin\b)\s*
    (?P<field>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_FIELD_METADATA_RE = re.compile(
    r"""
    (?:
        [,;|/]
        |
        \s+[-–—]\s+
    )
    \s*
    (?:
        gpa |
        grade\s+point\s+average |
        minors? |
        honors? |
        dean's\s+list |
        expected |
        anticipated |
        graduated |
        graduation |
        coursework |
        relevant\s+coursework
    )
    \b
    """,
    re.IGNORECASE | re.VERBOSE,
)

_INVALID_FIELD_CONTEXT_RE = re.compile(
    r"""
    \b(?:
        university |
        college |
        school |
        department |
        faculty |
        institute |
        academy |
        coursework |
        course |
        club |
        member |
        interested |
        interest
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

_FIELD_VALUE_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9&/'’+.-]*"
    r"(?:\s+[A-Za-z0-9][A-Za-z0-9&/'’+.-]*){0,11}"
)
# ==============Study feild helpers end here=============

GPA_PATTERN = re.compile(
    r"\b(?:gpa|grade\s+point\s+average)\b"
    r"(?:\s*[:=]\s*|\s+-\s+|\s+)"
    r"(?P<score>\d+(?:\.\d+)?)"
    r"(?:\s*/\s*(?P<scale>[45](?:\.0+)?))?"
    r"(?!\s*/|[\d.])",
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

_SPECIALIZATION_MARKER_PATTERN = (
    r"(?:"
    + "|".join(_SPECIALIZATION_MARKERS)
    + r")"
)

_SPECIALIZATION_RE = re.compile(
    rf"""
    \b
    {_SPECIALIZATION_MARKER_PATTERN}
    \b
    \s*
    (?:
        in
        \s+
        |
        :
        \s*
        |
        -
        \s*
    )?
    (?P<specialization>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

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


def extract_date_candidates(line: str) -> list[DateCandidate]:
    return detect_date_candidates(line)

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

        if degree_match is None:
            continue

        definition, match, _ = degree_match

        matched_degree_name = match.groupdict().get("degree_name")

        degree_name = (
            matched_degree_name.strip()
            if matched_degree_name
            else definition.canonical_name
        )

        return degree_name, definition.level

    return None


def _clean_field_candidate(candidate: str) -> str | None:
    candidate = remove_date_candidates(candidate)

    metadata_match = _FIELD_METADATA_RE.search(candidate)
    if metadata_match is not None:
        candidate = candidate[:metadata_match.start()]

    candidate = candidate.strip(" \t,;:|/()[]-–—.")

    if not candidate:
        return None

    # Avoid accepting academic units and unrelated descriptive text.
    if _INVALID_FIELD_CONTEXT_RE.search(candidate):
        return None

    if _looks_like_location(candidate):
        return None

    # Reject malformed or unusually long candidates.
    if _FIELD_VALUE_RE.fullmatch(candidate) is None:
        return None

    return candidate


def extract_study_field_candidates(line: str) -> list[str]:
    normalized_line = normalize_text(_clean_line(line))

    if not normalized_line:
        return []

    # Explicitly labeled fields:
    # "Major: Geology"
    # "Program in Game Design"
    explicit_match = _FIELD_LABEL_RE.fullmatch(normalized_line)

    if explicit_match is not None:
        candidate = _clean_field_candidate(
            explicit_match.group("field")
        )

        if candidate is None:
            return []

        label = explicit_match.group("label").casefold()

        if label.startswith("double major"):
            candidates = [
                _clean_field_candidate(value)
                for value in re.split(
                    r"\s*(?:,|;|\band\b)\s*",
                    candidate,
                    flags=re.IGNORECASE,
                )
            ]

            return [
                value
                for value in candidates
                if value is not None
            ]

        return [candidate]

    # Degree-adjacent fields:
    # "Bachelor of Science in Geology"
    # "Geology, Bachelor of Science"
    degree_match = _find_degree_match(normalized_line)

    if degree_match is None:
        return []

    _, match, matched_line = degree_match
    
    engineering_field = match.groupdict().get(
    "engineering_field"
    )

    if engineering_field:
        candidate = _clean_field_candidate(
            f"{engineering_field} Engineering"
        )      

        return [candidate] if candidate else []

    following_text = matched_line[match.end():]

    following_text = re.sub(
        r"""
        ^\s*
        (?:
            in\b |
            major(?:ing)?\s+in\b |
            with\s+(?:a\s+)?major\s+in\b |
            [,;:|/()\-–—]+
        )
        \s*
        """,
        "",
        following_text,
        count=1,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    following_candidate = _clean_field_candidate(following_text)

    if following_candidate:
        return [following_candidate]

    preceding_text = matched_line[:match.start()]
    preceding_candidate = _clean_field_candidate(preceding_text)

    return [preceding_candidate] if preceding_candidate else []


def _split_known_field_list(candidate: str) -> list[str]:
    parts = [
        part.strip()
        for part in re.split(
            r"\s*(?:,|;|\band\b)\s*",
            candidate,
            flags=re.IGNORECASE,
        )
        if part.strip()
    ]

    if len(parts) < 2:
        return [candidate]

    normalized_parts = [
        normalize_academic_field(part)
        for part in parts
    ]

    if all(value is not None for value in normalized_parts):
        return [
            value
            for value in normalized_parts
            if value is not None
        ]

    # Do not split unknown compound names:
    # "Peace and Conflict Studies"
    return [candidate]

def normalize_study_field_candidates(
    candidates: list[str],
) -> list[str]:
    normalized_fields: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        exact_match = normalize_academic_field(candidate)

        if exact_match is not None:
            values = [exact_match]
        else:
            values = _split_known_field_list(candidate)

        for value in values:
            key = value.casefold()

            if key not in seen:
                seen.add(key)
                normalized_fields.append(value)

    return normalized_fields

def normalize_academic_field(candidate: str) -> str | None:
    """Return a canonical field only when the complete candidate is a known alias."""
    normalized = normalize_text(candidate).casefold().strip()
    if normalized in STUDY_FIELD_ALIASES:
        return STUDY_FIELD_ALIASES[normalized]
    return SHORT_STUDY_FIELD_ALIASES.get(normalized)


def detect_specializations(
    entry: str | list[str],
) -> list[str]:
    lines = [entry] if isinstance(entry, str) else entry

    specializations: list[str] = []
    seen: set[str] = set()

    for line in lines:
        cleaned_line = remove_date_candidates(line)

        if not cleaned_line:
            continue

        match = _SPECIALIZATION_RE.search(cleaned_line)

        if match is None:
            continue

        specialization = match.group("specialization").strip(
            " \t,;:|-–—"
        )

        if not specialization:
            continue

        normalized = specialization.casefold()

        if normalized in seen:
            continue

        seen.add(normalized)
        specializations.append(specialization)

    return specializations

def detect_gpa(line: str) -> str | None:
    normalized_line = normalize_text(line).strip()
    if not normalized_line:
        return None

    for match in GPA_PATTERN.finditer(normalized_line):
        if re.search(r"\bmajor\s*$", normalized_line[:match.start()], re.IGNORECASE):
            continue

        score_text = match.group("score")
        scale_text = match.group("scale")

        score = float(score_text)
        maximum_score = float(scale_text) if scale_text is not None else 4.0

        if not 0.0 <= score <= maximum_score:
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
    """
    Detect fields of study only when the line provides strong academic context.

    Examples:
        Bachelor of Science in Geology
        Major: Marine Biology
        Field of Study: Urban Planning
        Program in Game Design
        Concentration: Computational Biology

    Unstructured mentions such as "Interested in Geology" return an empty list.
    """
    candidates = extract_study_field_candidates(line)

    return normalize_study_field_candidates(candidates)


def select_education_date(
    entry_lines: list[str],
) -> tuple[DateCandidate | None, bool]:
    located_candidates: list[tuple[int, str, DateCandidate]] = []

    for line_index, line in enumerate(entry_lines):
        for candidate in detect_date_candidates(line):
            located_candidates.append((line_index, line, candidate))

    if not located_candidates:
        return None, False

    _, selected_line, selected = min(
        located_candidates,
        key=lambda item: (
            not (
                item[2].end_date is not None
                or item[2].is_current
            ),
            item[0],
            item[2].start_index,
        ),
    )

    is_expected = _EXPECTED_MARKER_RE.search(selected_line) is not None

    if not is_expected and selected.end_date is not None:
        is_expected = any(
            _EXPECTED_MARKER_RE.search(line) is not None
            and candidate.end_date is None
            and candidate.start_date == selected.end_date
            for _, line, candidate in located_candidates
        )

    return selected, is_expected


def parse_degree_entry(entry_lines: list[str]) -> DegreeRecord:
    record = DegreeRecord(raw_lines=entry_lines.copy())

    # Dates
    candidate, is_expected = select_education_date(entry_lines)

    if candidate is not None:
        if candidate.is_current:
            record.start_date = candidate.start_date
            record.end_date = None
        elif candidate.end_date is None:
            record.start_date = None
            record.end_date = candidate.start_date
        else:
            record.start_date = candidate.start_date
            record.end_date = candidate.end_date

        record.is_expected = is_expected
        record.is_current = candidate.is_current

    # Institution
    institution = detect_institution(entry_lines)

    if institution is not None:
        cleaned_institution = remove_date_candidates(
            institution
        ).strip()

        if cleaned_institution:
            record.institution = cleaned_institution

    # Degree
    degree = detect_degree(entry_lines)

    if degree is not None:
        record.degree_name, record.degree_level = degree

    # Specializations
    record.specializations = detect_specializations(entry_lines)

    # Fields of study
    seen_fields: set[str] = set()

    for line in entry_lines:
        cleaned_line = remove_date_candidates(line).strip()

        if not cleaned_line:
            continue

        for field_name in detect_study_fields(cleaned_line):
            key = field_name.casefold()

            if key in seen_fields:
                continue

            seen_fields.add(key)
            record.fields_of_study.append(field_name)

    # GPA and minors
    seen_minors: set[str] = set()

    for line in entry_lines:
        if record.gpa is None:
            record.gpa = detect_gpa(line)

        for minor in detect_minors(line):
            key = minor.casefold()

            if key in seen_minors:
                continue

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
