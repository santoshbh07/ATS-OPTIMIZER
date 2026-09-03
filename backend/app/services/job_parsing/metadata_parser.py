# Extracts general job metadata from a job description.
# Handles fields such as job title, company, location,
# employment type, salary, and other posting-level information.
from dataclasses import dataclass
import re

from .section_extractor import is_header


@dataclass
class MetaData:
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None


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

CANADIAN_PROVINCE_NAMES = {
    "alberta", "british columbia", "manitoba", "new brunswick",
    "newfoundland and labrador", "nova scotia", "ontario",
    "prince edward island", "quebec", "saskatchewan",
}

CANADIAN_PROVINCE_ABBREVIATIONS = {
    "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE",
    "QC", "SK", "YT",
}

COUNTRY_NAMES = {
    "australia", "canada", "china", "france", "germany", "india",
    "ireland", "italy", "japan", "mexico", "nepal", "new zealand",
    "singapore", "south korea", "spain", "united kingdom",
    "united states", "united states of america",
}

COUNTRY_ABBREVIATIONS = {"US", "USA", "UK"}

LOCATION_REGION_SUFFIXES = tuple(sorted(
    {
        *(region.casefold() for region in US_STATE_ABBREVIATIONS),
        *US_STATE_NAMES,
        *(region.casefold() for region in CANADIAN_PROVINCE_ABBREVIATIONS),
        *CANADIAN_PROVINCE_NAMES,
        *COUNTRY_NAMES,
        *(region.casefold() for region in COUNTRY_ABBREVIATIONS),
    },
    key=len,
    reverse=True,
))

EMPLOYMENT_TYPES = (
    (re.compile(r"\bfull[ -]?time\b", re.I), "Full-time"),
    (re.compile(r"\bpart[ -]?time\b", re.I), "Part-time"),
    (re.compile(r"\bintern(?:ship)?\b", re.I), "Internship"),
    (re.compile(r"\bcontract(?:or)?\b", re.I), "Contract"),
    (re.compile(r"\btemporary\b|\btemp\b", re.I), "Temporary"),
    (re.compile(r"\bfreelance\b", re.I), "Freelance"),
    (re.compile(r"\bseasonal\b", re.I), "Seasonal"),
    (re.compile(r"\bpermanent\b", re.I), "Permanent"),
)

FIELD_LABELS = {
    "job_title": (
        "job title", "position title", "role title", "title", "position", "role",
    ),
    "company": ("company", "organization", "organisation", "employer"),
    "location": ("location", "job location", "work location", "office location"),
    "employment_type": ("employment type", "job type", "position type"),
    "salary": ("salary", "salary range", "pay", "pay range", "compensation"),
}

FIELD_PATTERNS = {
    field_name: re.compile(
        rf"^(?:{'|'.join(re.escape(label) for label in labels)})"
        r"\s*(?::|[|]|[-–—])\s*(?P<value>.+)$",
        re.I,
    )
    for field_name, labels in FIELD_LABELS.items()
}

JOB_TITLE_TERMS = {
    "administrator", "analyst", "architect", "consultant", "designer",
    "developer", "director", "engineer", "intern", "manager", "officer",
    "product", "programmer", "scientist", "specialist", "technician",
}

COMPANY_SUFFIX_RE = re.compile(
    r"\b(?:company|co\.?|corp\.?|corporation|group|inc\.?|labs?|llc|ltd\.?|"
    r"solutions|systems|technologies)\b",
    re.I,
)

WORK_LOCATION_RE = re.compile(
    r"^(?:fully\s+)?(?:remote|hybrid|on[ -]?site)(?:\s+[-–—,(].*)?$",
    re.I,
)

# Unlabelled salary text must contain a strong pay signal. This avoids treating
# experience years or ordinary numbers in the description as compensation.
SALARY_RE = re.compile(
    r"(?:[$€£]\s*\d[\d,]*(?:\.\d+)?(?:\s*[kK])?"
    r"|\b(?:USD|CAD|EUR|GBP)\s*\d[\d,]*(?:\.\d+)?(?:\s*[kK])?"
    r"|\b\d+(?:\.\d+)?\s*[kK])"
    r"(?:\s*(?:-|–|—|to)\s*(?:[$€£]\s*)?\d[\d,]*(?:\.\d+)?(?:\s*[kK])?)?"
    r"(?:\s*(?:per\s+|/\s*)(?:hour|hr|year|yr|month|week))?",
    re.I,
)

def _looks_like_location(value: str) -> bool:
    """Return whether a complete value resembles ``City, Region``."""
    location = value.strip().rstrip(".")
    location = re.sub(r"\s+\d{5}(?:-\d{4})?$", "", location)
    normalized_location = location.casefold()

    # Validate from the right so "City, ST" and "City ST" share one rule.
    for region in LOCATION_REGION_SUFFIXES:
        if not normalized_location.endswith(region):
            continue

        # Two-letter region codes are too ambiguous when lower-cased (for
        # example, "in" can be a preposition), so require code-style casing.
        if len(region) == 2 and location[-2:] != location[-2:].upper():
            continue

        city_end = len(location) - len(region)
        if city_end <= 0 or location[city_end - 1] not in " ,":
            continue

        city = location[:city_end].rstrip(" ,")
        if "," in city and _looks_like_location(city):
            return True
        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", city):
            continue

        return True

    return False


def _clean_line(line: str) -> str:
    cleaned = re.sub(
        r"^\s*(?:[-*•▪■◦‣]|\d+[.)])\s*",
        "",
        line.strip(),
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def _employment_type(value: str) -> str | None:
    for pattern, canonical_name in EMPLOYMENT_TYPES:
        if pattern.search(value):
            return canonical_name
    return None


def _looks_like_title(value: str) -> bool:
    words = set(re.findall(r"[A-Za-z]+", value.casefold()))
    return bool(words & JOB_TITLE_TERMS) and len(value.split()) <= 12


def _is_metadata_value(value: str) -> bool:
    return bool(
        _looks_like_location(value)
        or WORK_LOCATION_RE.fullmatch(value)
        or _employment_type(value)
        or SALARY_RE.search(value)
    )


def _preamble_candidates(lines: list[str]) -> list[tuple[int, str]]:
    """Return short, unlabelled lines before the first section header."""
    candidates: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if is_header(line):
            break
        if any(pattern.fullmatch(line) for pattern in FIELD_PATTERNS.values()):
            continue
        if _is_metadata_value(line):
            continue
        if len(line) > 120 or len(line.split()) > 14 or line.endswith((".", "!", "?")):
            continue
        candidates.append((index, line))
    return candidates


def parse_metadata(
    jd_text: str,
    sections: dict[str, list[str]] | None = None,
) -> MetaData:
    """Extract common posting metadata from labelled fields and the preamble."""
    if not isinstance(jd_text, str):
        raise TypeError("jd_text must be a string")

    lines = [_clean_line(line) for line in jd_text.splitlines()]
    lines = [line for line in lines if line]
    metadata = MetaData()

    for line in lines:
        for field_name, pattern in FIELD_PATTERNS.items():
            if getattr(metadata, field_name) is not None:
                continue
            match = pattern.fullmatch(line)
            if match is None:
                continue

            value = match.group("value").strip()
            if field_name == "employment_type":
                value = _employment_type(value) or value
            setattr(metadata, field_name, value)

    # Dedicated sections are more reliable than scanning descriptive prose.
    if sections:
        if metadata.location is None and sections.get("location"):
            metadata.location = _clean_line(sections["location"][0])
        if metadata.salary is None and sections.get("compensation"):
            metadata.salary = _clean_line(sections["compensation"][0])

    for line in lines:
        if metadata.location is None and (
            _looks_like_location(line) or WORK_LOCATION_RE.fullmatch(line)
        ):
            metadata.location = line
        if metadata.employment_type is None:
            metadata.employment_type = _employment_type(line)
        if metadata.salary is None:
            salary_match = SALARY_RE.search(line)
            if salary_match is not None:
                metadata.salary = salary_match.group(0).strip()

    candidates = _preamble_candidates(lines)
    title_candidate: tuple[int, str] | None = None
    if metadata.job_title is None:
        title_candidate = next(
            ((index, value) for index, value in candidates if _looks_like_title(value)),
            candidates[0] if candidates else None,
        )
        if title_candidate is not None:
            metadata.job_title = title_candidate[1]

    if metadata.company is None and candidates:
        company_candidate = next(
            (
                (index, value)
                for index, value in candidates
                if COMPANY_SUFFIX_RE.search(value)
                and (title_candidate is None or index != title_candidate[0])
            ),
            None,
        )

        # Plain company names often sit directly beside the title and have no
        # legal suffix. Use that layout only when the candidate is not a title.
        if company_candidate is None:
            if title_candidate is None:
                company_candidate = candidates[0]
            else:
                neighbours = sorted(
                    (
                        candidate
                        for candidate in candidates
                        if candidate[0] != title_candidate[0]
                        and not _looks_like_title(candidate[1])
                    ),
                    key=lambda candidate: (
                        abs(candidate[0] - title_candidate[0]),
                        candidate[0] < title_candidate[0],
                    ),
                )
                company_candidate = neighbours[0] if neighbours else None

        if company_candidate is not None:
            metadata.company = company_candidate[1]

    return metadata
