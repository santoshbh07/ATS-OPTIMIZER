from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


DateKind = Literal[
    "month_year",
    "month_range",
    "open_range",
    "year_range",
    "season",
    "season_range",
    "year",
]


@dataclass(frozen=True)
class NormalizedDate:
    year: int
    month: int | None = None
    season: str | None = None


@dataclass(frozen=True)
class DateCandidate:
    raw_text: str
    start_index: int
    end_index: int
    kind: DateKind
    start_date: NormalizedDate
    end_date: NormalizedDate | None
    is_current: bool
    confidence: float

    @property
    def span(self) -> tuple[int, int]:
        return self.start_index, self.end_index


@dataclass(frozen=True)
class DetectorConfig:
    two_digit_year_pivot: int = 2049
    minimum_year: int = 1900
    maximum_year: int = 2100


@dataclass(frozen=True)
class PatternDefinition:
    kind: DateKind
    regex: re.Pattern[str]
    confidence: float


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

SEASONS = {
    "spring": "Spring",
    "summer": "Summer",
    "fall": "Fall",
    "autumn": "Autumn",
    "winter": "Winter",
}

# Used only to validate chronological range order. The season name itself
# remains preserved in NormalizedDate.
SEASON_ORDER = {
    "Winter": 1,
    "Spring": 2,
    "Summer": 3,
    "Fall": 4,
    "Autumn": 4,
}

MONTH_NAME = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t|tember)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
SEASON_NAME = r"(?:spring|summer|fall|autumn|winter)"
YEAR = r"(?:\d{2}|\d{4})"
FOUR_DIGIT_YEAR = r"\d{4}"
SEPARATOR = r"(?:-|\u2013|\u2014|\bto\b)"
CURRENT_VALUE = r"(?:present|current|now|ongoing)"

FLAGS = re.IGNORECASE
_WHITESPACE_RE = re.compile(r"\s+")


def compile_pattern(expression: str) -> re.Pattern[str]:
    """Add boundaries that prevent matches inside ordinary words."""
    return re.compile(rf"(?<!\w){expression}(?!\w)", FLAGS)


# Range patterns intentionally appear before single-date patterns.
PATTERNS = (
    PatternDefinition(
        kind="month_range",
        confidence=0.98,
        regex=compile_pattern(
            rf"(?P<start_month>{MONTH_NAME})\.?\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<end_month>{MONTH_NAME})\.?\s*"
            rf"(?P<shared_year>{YEAR})"
        ),
    ),
    PatternDefinition(
        kind="month_range",
        confidence=0.99,
        regex=compile_pattern(
            rf"(?P<start_month>{MONTH_NAME})\.?\s*"
            rf"(?P<start_year>{YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<end_month>{MONTH_NAME})\.?\s*"
            rf"(?P<end_year>{YEAR})"
        ),
    ),
    PatternDefinition(
        kind="month_range",
        confidence=0.86,
        regex=compile_pattern(
            rf"(?P<start_numeric_month>\d{{1,2}})/"
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<end_numeric_month>\d{{1,2}})/"
            rf"(?P<end_year>{FOUR_DIGIT_YEAR})"
        ),
    ),
    PatternDefinition(
        kind="season_range",
        confidence=0.96,
        regex=compile_pattern(
            rf"(?P<start_season>{SEASON_NAME})\s*"
            rf"(?P<start_year>{YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<end_season>{SEASON_NAME})\s*"
            rf"(?P<end_year>{YEAR})"
        ),
    ),
    PatternDefinition(
        kind="open_range",
        confidence=0.99,
        regex=compile_pattern(
            rf"(?P<start_month>{MONTH_NAME})\.?\s*"
            rf"(?P<start_year>{YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<current>{CURRENT_VALUE})"
        ),
    ),
    PatternDefinition(
        kind="open_range",
        confidence=0.86,
        regex=compile_pattern(
            rf"(?P<start_numeric_month>\d{{1,2}})/"
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<current>{CURRENT_VALUE})"
        ),
    ),
    PatternDefinition(
        kind="open_range",
        confidence=0.96,
        regex=compile_pattern(
            rf"(?P<start_season>{SEASON_NAME})\s*"
            rf"(?P<start_year>{YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<current>{CURRENT_VALUE})"
        ),
    ),
    PatternDefinition(
        kind="open_range",
        confidence=0.91,
        regex=compile_pattern(
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<current>{CURRENT_VALUE})"
        ),
    ),
    PatternDefinition(
        kind="year_range",
        confidence=0.94,
        regex=compile_pattern(
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})\s*"
            rf"{SEPARATOR}\s*"
            rf"(?P<end_year>{FOUR_DIGIT_YEAR})"
        ),
    ),
    PatternDefinition(
        kind="season",
        confidence=0.89,
        regex=compile_pattern(
            rf"(?P<start_season>{SEASON_NAME})\s*"
            rf"(?P<start_year>{YEAR})"
        ),
    ),
    PatternDefinition(
        kind="month_year",
        confidence=0.95,
        regex=compile_pattern(
            rf"(?P<start_month>{MONTH_NAME})\.?\s*"
            rf"(?P<start_year>{YEAR})"
        ),
    ),
    PatternDefinition(
        kind="month_year",
        confidence=0.80,
        regex=compile_pattern(
            rf"(?P<start_numeric_month>\d{{1,2}})/"
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})"
        ),
    ),
    PatternDefinition(
        kind="year",
        confidence=0.62,
        regex=compile_pattern(
            rf"(?P<start_year>{FOUR_DIGIT_YEAR})"
        ),
    ),
)


def normalize_year(value: str, pivot_year: int) -> int:
    """Expand a two-digit year relative to the configured pivot."""
    numeric_year = int(value)

    if len(value) == 4:
        return numeric_year

    pivot_suffix = pivot_year % 100
    pivot_century = pivot_year - pivot_suffix

    if numeric_year <= pivot_suffix:
        return pivot_century + numeric_year

    return pivot_century - 100 + numeric_year


def normalize_month(value: str) -> int:
    normalized_value = value.lower().rstrip(".")

    if normalized_value.isdigit():
        return int(normalized_value)

    return MONTHS.get(normalized_value, 0)


def normalize_season(value: str) -> str | None:
    return SEASONS.get(value.lower())


def normalize_match(
    match: re.Match[str],
    definition: PatternDefinition,
    config: DetectorConfig,
) -> DateCandidate:
    groups = match.groupdict()

    start_year_text = groups.get("start_year") or groups.get("shared_year")

    if start_year_text is None:
        raise ValueError("Matched date pattern did not provide a start year")

    start_year = normalize_year(
        start_year_text,
        config.two_digit_year_pivot,
    )

    start_month_text = (
        groups.get("start_month")
        or groups.get("start_numeric_month")
    )
    start_season_text = groups.get("start_season")

    start_date = NormalizedDate(
        year=start_year,
        month=normalize_month(start_month_text) if start_month_text else None,
        season=normalize_season(start_season_text) if start_season_text else None,
    )

    is_current = bool(groups.get("current"))
    end_date = None

    if not is_current:
        end_year_text = groups.get("end_year") or groups.get("shared_year")
        end_month_text = (
            groups.get("end_month")
            or groups.get("end_numeric_month")
        )
        end_season_text = groups.get("end_season")

        if end_year_text:
            end_date = NormalizedDate(
                year=normalize_year(
                    end_year_text,
                    config.two_digit_year_pivot,
                ),
                month=(
                    normalize_month(end_month_text)
                    if end_month_text
                    else None
                ),
                season=(
                    normalize_season(end_season_text)
                    if end_season_text
                    else None
                ),
            )

    return DateCandidate(
        raw_text=match.group(0),
        start_index=match.start(),
        end_index=match.end(),
        kind=definition.kind,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        confidence=definition.confidence,
    )


def chronological_key(value: NormalizedDate) -> tuple[int, int]:
    if value.month is not None:
        return value.year, value.month

    if value.season is not None:
        return value.year, SEASON_ORDER[value.season]

    return value.year, 0


def validate_date(
    value: NormalizedDate,
    config: DetectorConfig,
) -> bool:
    if not config.minimum_year <= value.year <= config.maximum_year:
        return False

    if value.month is not None and not 1 <= value.month <= 12:
        return False

    if value.season is not None and value.season not in SEASON_ORDER:
        return False

    return True


def validate_candidate(
    candidate: DateCandidate,
    config: DetectorConfig,
) -> bool:
    if not validate_date(candidate.start_date, config):
        return False

    if candidate.is_current:
        return candidate.end_date is None

    if candidate.end_date is None:
        return True

    if not validate_date(candidate.end_date, config):
        return False

    return (
        chronological_key(candidate.start_date)
        <= chronological_key(candidate.end_date)
    )


def spans_overlap(
    first: DateCandidate,
    second: DateCandidate,
) -> bool:
    return (
        first.start_index < second.end_index
        and second.start_index < first.end_index
    )


def select_longest_non_overlapping(
    candidates: list[DateCandidate],
) -> list[DateCandidate]:
    """
    Prefer the longest valid match at an overlapping location.

    Confidence is the secondary tie-breaker, followed by pattern order.
    """
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            -(candidate.end_index - candidate.start_index),
            -candidate.confidence,
            candidate.start_index,
        ),
    )

    selected: list[DateCandidate] = []

    for candidate in ranked:
        if any(spans_overlap(candidate, existing) for existing in selected):
            continue

        selected.append(candidate)

    return sorted(selected, key=lambda candidate: candidate.start_index)


def detect_date_candidates(
    line: str,
    config: DetectorConfig | None = None,
) -> list[DateCandidate]:
    """
    Detect valid date candidates in one resume line.

    This function does not attach candidates to any resume section or entry.
    """
    if not line:
        return []

    active_config = config or DetectorConfig()
    valid_candidates: list[DateCandidate] = []

    for definition in PATTERNS:
        for match in definition.regex.finditer(line):
            candidate = normalize_match(
                match,
                definition,
                active_config,
            )

            if validate_candidate(candidate, active_config):
                valid_candidates.append(candidate)

    return select_longest_non_overlapping(valid_candidates)


def remove_date_candidates(
    line: str,
    config: DetectorConfig | None = None,
) -> str:
    """Remove recognized date expressions from a line."""
    if not line:
        return ""

    candidates = detect_date_candidates(line, config)

    if not candidates:
        return line.strip()

    cleaned_line = line

    # Remove from right to left so match indexes stay valid.
    for candidate in reversed(candidates):
        cleaned_line = (
            cleaned_line[:candidate.start_index]
            + " "
            + cleaned_line[candidate.end_index:]
        )

    cleaned_line = _WHITESPACE_RE.sub(" ", cleaned_line)

    return cleaned_line.strip(" \t,;:|-–—")
