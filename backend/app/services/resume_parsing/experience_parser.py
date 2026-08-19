from __future__ import annotations

import re
from dataclasses import dataclass, field

from .date_parser import (
    DateCandidate,
    NormalizedDate,
    detect_date_candidates,
    remove_date_candidates,
)
from .text_utils import normalize_text, strip_bullet


@dataclass
class ExperienceRecord:
    company: str | None = None
    position: str | None = None
    location: str | None = None

    start_date: NormalizedDate | None = None
    end_date: NormalizedDate | None = None
    is_current: bool = False

    descriptions: list[str] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)


POSITION_LABELS = {
    "position",
    "job title",
    "role",
    "title",
}

COMPANY_LABELS = {
    "company",
    "employer",
    "organization",
    "organisation",
}

LOCATION_LABELS = {
    "location",
}

DATE_LABELS = {
    "date",
    "dates",
    "duration",
    "tenure",
}

DESCRIPTION_LABELS = {
    "accomplishments",
    "achievements",
    "description",
    "highlights",
    "impact",
    "key achievements",
    "key responsibilities",
    "responsibilities",
    "summary",
}

DESCRIPTION_STARTERS = {
    "achieved",
    "administered",
    "analyzed",
    "architected",
    "automated",
    "built",
    "collaborated",
    "configured",
    "created",
    "decreased",
    "delivered",
    "deployed",
    "designed",
    "developed",
    "directed",
    "drove",
    "enabled",
    "engineered",
    "established",
    "evaluated",
    "executed",
    "generated",
    "grew",
    "implemented",
    "improved",
    "increased",
    "installed",
    "integrated",
    "launched",
    "led",
    "maintained",
    "managed",
    "mentored",
    "migrated",
    "monitored",
    "optimized",
    "organized",
    "participated",
    "performed",
    "produced",
    "reduced",
    "refactored",
    "resolved",
    "scaled",
    "secured",
    "spearheaded",
    "streamlined",
    "supported",
    "tested",
    "trained",
    "tutored",
    "validated",
    "worked",
    "wrote",
}


_LABEL_VALUE_RE = re.compile(
    r"^\s*(?P<label>[A-Za-z ]+?)\s*:\s*(?P<value>.*)$"
)

_HEADER_SEPARATOR_RE = re.compile(
    r"\s+(?:\||\u2013|\u2014)\s+"
)

_POSITION_TERM_RE = re.compile(
    r"\b(?:"
    r"accountant|administrator|adviser|advisor|analyst|architect|"
    r"assistant|associate|cashier|chief|co-?op|consultant|coordinator|"
    r"designer|developer|director|engineer|executive|fellow|founder|"
    r"grader|head|instructor|intern|lead|manager|member|officer|operator|"
    r"owner|president|professor|programmer|researcher|scientist|server|"
    r"specialist|strategist|supervisor|teacher|technician|tester|tutor|"
    r"vice president|vp|webmaster|writer"
    r")\b",
    re.IGNORECASE,
)

_COMPANY_INDICATOR_RE = re.compile(
    r"\b(?:"
    r"agency|association|bank|college|company|co\.?|corp\.?|corporation|"
    r"council|department|foundation|group|hospital|inc\.?|institute|"
    r"laboratory|labs?|llc|llp|ltd\.?|partners|school|services|solutions|"
    r"studios?|systems|technologies|university"
    r")\b",
    re.IGNORECASE,
)

_POSITION_AT_COMPANY_RE = re.compile(
    r"^\s*(?P<position>.+?)\s+(?:at|@)\s+(?P<company>.+?)\s*$",
    re.IGNORECASE,
)

_PLACEHOLDER_DATE_RE = re.compile(
    r"(?<!\w)\d{1,2}/(?:xx|yyyy)\s*"
    r"(?:-|\u2013|\u2014|to)\s*"
    r"(?:\d{1,2}/(?:xx|yyyy)|present|current|now)(?!\w)",
    re.IGNORECASE,
)

_US_REGION_CODES = {
    "ak", "al", "ar", "az", "ca", "co", "ct", "dc", "de", "fl",
    "ga", "hi", "ia", "id", "il", "in", "ks", "ky", "la", "ma",
    "md", "me", "mi", "mn", "mo", "ms", "mt", "nc", "nd", "ne",
    "nh", "nj", "nm", "nv", "ny", "oh", "ok", "or", "pa", "ri",
    "sc", "sd", "tn", "tx", "ut", "va", "vt", "wa", "wi", "wv",
    "wy",
}

_REGION_NAMES = {
    "alberta", "british columbia", "manitoba", "new brunswick",
    "newfoundland and labrador", "northwest territories", "nova scotia",
    "nunavut", "ontario", "prince edward island", "quebec",
    "saskatchewan", "yukon",
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming",
}

_COUNTRY_NAMES = {
    "australia", "brazil", "canada", "china", "france", "germany",
    "india", "ireland", "italy", "japan", "mexico", "netherlands",
    "singapore", "south korea", "spain", "sweden", "switzerland",
    "uk", "united kingdom", "us", "usa", "united states",
    "united states of america",
}

_WORK_MODES = {
    "hybrid",
    "on-site",
    "onsite",
    "remote",
}


def is_bullet_line(line: str) -> bool:
    cleaned = normalize_text(line)
    return bool(cleaned and strip_bullet(cleaned) != cleaned)


def remove_bullet(line: str) -> str:
    return strip_bullet(normalize_text(line)).strip()


def _split_label(line: str) -> tuple[str | None, str]:
    match = _LABEL_VALUE_RE.match(normalize_text(line))

    if match is None:
        return None, normalize_text(line)

    return match.group("label").casefold().strip(), match.group("value").strip()


def _remove_placeholder_date(line: str) -> str:
    return _PLACEHOLDER_DATE_RE.sub(" ", line).strip(" \t,;:|-\u2013\u2014")


def _clean_header_text(line: str) -> str:
    cleaned = remove_bullet(line) if is_bullet_line(line) else normalize_text(line)
    had_date = bool(detect_date_candidates(cleaned))
    cleaned = remove_date_candidates(cleaned)
    cleaned = _remove_placeholder_date(cleaned)

    if had_date:
        cleaned = re.sub(
            r"^(?:spring|summer|fall|autumn|winter)s?\s+",
            "",
            cleaned,
            count=1,
            flags=re.IGNORECASE,
        )

    return cleaned.strip(" \t,;:|-\u2013\u2014")


def _normalized_location_token(value: str) -> str:
    value = _remove_placeholder_date(value)
    value = re.sub(r"\s+\d{5}(?:-\d{4})?$", "", value)
    return value.strip(" .").casefold()


def _is_region(value: str) -> bool:
    normalized = _normalized_location_token(value)
    return normalized in _US_REGION_CODES or normalized in _REGION_NAMES


def _is_country(value: str) -> bool:
    return _normalized_location_token(value) in _COUNTRY_NAMES


def _is_work_mode(value: str) -> bool:
    return _normalized_location_token(value) in _WORK_MODES


def split_company_and_location(line: str) -> tuple[str, str | None]:
    """Split a trailing resume location from the preceding header text."""
    cleaned = _clean_header_text(line)
    label, value = _split_label(cleaned)

    if label in LOCATION_LABELS:
        return "", value or None

    if label in COMPANY_LABELS | POSITION_LABELS:
        cleaned = value

    if not cleaned:
        return "", None

    if _is_work_mode(cleaned):
        return "", cleaned.title()

    parts = [part.strip() for part in cleaned.split(",") if part.strip()]

    if len(parts) >= 2 and _is_work_mode(parts[-1]):
        return ", ".join(parts[:-1]), parts[-1].title()

    if len(parts) >= 2 and _is_region(parts[-1]):
        location = f"{parts[-2]}, {_remove_placeholder_date(parts[-1])}"
        return ", ".join(parts[:-2]), location

    if len(parts) >= 2 and _is_country(parts[-1]):
        if len(parts) >= 4 and _is_region(parts[-2]):
            location_start = len(parts) - 3
        elif len(parts) >= 3:
            location_start = len(parts) - 2
        else:
            location_start = len(parts) - 1

        return (
            ", ".join(parts[:location_start]),
            ", ".join(parts[location_start:]),
        )

    separator_parts = [
        part.strip()
        for part in _HEADER_SEPARATOR_RE.split(cleaned)
        if part.strip()
    ]

    if len(separator_parts) > 1:
        possible_location = separator_parts[-1]
        _, nested_location = split_company_and_location(possible_location)

        if nested_location is not None:
            return " | ".join(separator_parts[:-1]), nested_location

        if _is_work_mode(possible_location):
            return " | ".join(separator_parts[:-1]), possible_location.title()

    return cleaned, None


def _looks_like_standalone_location(line: str) -> bool:
    cleaned = _clean_header_text(line)

    if not cleaned:
        return False

    if _is_work_mode(cleaned):
        return True

    prefix, location = split_company_and_location(cleaned)

    if location is None:
        return False

    if not prefix:
        return True

    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    return (
        len(parts) == 2
        and (_is_region(parts[-1]) or _is_country(parts[-1]))
        and _COMPANY_INDICATOR_RE.search(parts[0]) is None
    )


def _header_parts(line: str) -> list[str]:
    cleaned, _ = split_company_and_location(line)
    label, value = _split_label(cleaned)

    if label in POSITION_LABELS | COMPANY_LABELS:
        cleaned = value

    return [
        part.strip(" \t,;:|-\u2013\u2014")
        for part in re.split(r"\s+(?:\||\u2013|\u2014)\s+|\s*,\s*", cleaned)
        if part.strip(" \t,;:|-\u2013\u2014")
    ]


def _first_word(line: str) -> str:
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", line)
    return words[0].casefold() if words else ""


def _starts_description(line: str) -> bool:
    label, _ = _split_label(remove_bullet(line))

    if label in DESCRIPTION_LABELS:
        return True

    lowered = remove_bullet(line).casefold()
    return (
        _first_word(lowered) in DESCRIPTION_STARTERS
        or lowered.startswith("responsible for ")
    )


def _looks_title_like(value: str) -> bool:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9+.#'/-]*", value)

    if not words:
        return False

    title_like = sum(
        word.isupper()
        or word[:1].isupper()
        or any(character.isupper() for character in word[1:])
        for word in words
    )
    return title_like >= max(1, len(words) // 2)


def _is_position_candidate(value: str) -> bool:
    cleaned = value.strip(" \t,;:|-\u2013\u2014")

    if not cleaned or len(cleaned.split()) > 14:
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    if _POSITION_TERM_RE.search(cleaned) is None:
        return False

    if _starts_description(cleaned) and not _looks_title_like(cleaned):
        return False

    return True


def _position_at_company(line: str) -> tuple[str, str] | None:
    cleaned = _clean_header_text(line)
    match = _POSITION_AT_COMPANY_RE.match(cleaned)

    if match is None:
        return None

    position = match.group("position").strip()
    company, _ = split_company_and_location(match.group("company"))

    if not _is_position_candidate(position) or not company:
        return None

    return position, company


def _candidate_header_lines(entry_lines: list[str]) -> list[str]:
    header_lines: list[str] = []

    for raw_line in entry_lines:
        line = normalize_text(raw_line)

        if not line or is_bullet_line(line):
            continue

        label, _ = _split_label(line)

        if label in DESCRIPTION_LABELS or _starts_description(line):
            continue

        header_lines.append(line)

    return header_lines


def detect_position(entry_lines: list[str]) -> str | None:
    for line in _candidate_header_lines(entry_lines):
        label, value = _split_label(_clean_header_text(line))

        if label in POSITION_LABELS and value:
            return value

    for line in _candidate_header_lines(entry_lines):
        combined = _position_at_company(line)

        if combined is not None:
            return combined[0]

    for line in _candidate_header_lines(entry_lines):
        for part in _header_parts(line):
            if _is_position_candidate(part):
                return part

    return None


def _is_company_candidate(value: str) -> bool:
    cleaned = value.strip(" \t,;:|-\u2013\u2014")

    if not cleaned or len(cleaned.split()) > 16:
        return False

    if cleaned.endswith((".", "!", "?")):
        return False

    if detect_date_candidates(cleaned) or _looks_like_standalone_location(cleaned):
        return False

    if _is_position_candidate(cleaned) or _starts_description(cleaned):
        return False

    label, _ = _split_label(cleaned)
    return label not in DESCRIPTION_LABELS | LOCATION_LABELS | DATE_LABELS


def detect_company(entry_lines: list[str]) -> str | None:
    header_lines = _candidate_header_lines(entry_lines)

    for line in header_lines:
        label, value = _split_label(_clean_header_text(line))

        if label in COMPANY_LABELS and value:
            return value

    for line in header_lines:
        combined = _position_at_company(line)

        if combined is not None:
            return combined[1]

    candidates: list[tuple[int, int, str]] = []

    for line_index, line in enumerate(header_lines):
        if _split_label(line)[0] in DATE_LABELS:
            continue

        prefix, location = split_company_and_location(line)
        parts = _header_parts(prefix)

        for part in parts:
            if not _is_company_candidate(part):
                continue

            score = 1

            if _COMPANY_INDICATOR_RE.search(part):
                score += 6

            if location is not None:
                score += 4

            candidates.append((score, -line_index, part))

    if not candidates:
        return None

    return max(candidates, key=lambda candidate: candidate[:2])[2]


def detect_location(entry_lines: list[str]) -> str | None:
    for line in _candidate_header_lines(entry_lines):
        label, value = _split_label(_clean_header_text(line))

        if label in LOCATION_LABELS and value:
            return value

        _, location = split_company_and_location(line)

        if location is not None:
            return location

    return None


def detect_experience_dates(entry_lines: list[str]) -> DateCandidate | None:
    candidates: list[tuple[int, DateCandidate]] = []

    for line_index, line in enumerate(_candidate_header_lines(entry_lines)):
        for candidate in detect_date_candidates(line):
            candidates.append((line_index, candidate))

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda item: (
            item[1].is_current or item[1].end_date is not None,
            item[1].confidence,
            -item[0],
            -item[1].start_index,
        ),
    )[1]


def _looks_like_plain_header(line: str) -> bool:
    cleaned = _clean_header_text(line)
    words = cleaned.split()

    if not 1 <= len(words) <= 14:
        return False

    if cleaned.endswith((".", "!", "?", ";")):
        return False

    if _starts_description(cleaned):
        return False

    return _looks_title_like(cleaned)


def looks_like_experience_header(
    line: str,
    next_line: str | None = None,
) -> bool:
    cleaned = normalize_text(line)

    if not cleaned or is_bullet_line(cleaned) or _starts_description(cleaned):
        return False

    label, value = _split_label(cleaned)

    if label in POSITION_LABELS | COMPANY_LABELS | LOCATION_LABELS | DATE_LABELS:
        return bool(value)

    if detect_position([cleaned]) is not None:
        return True

    prefix, location = split_company_and_location(cleaned)

    if location is not None and bool(prefix):
        return True

    if _COMPANY_INDICATOR_RE.search(prefix):
        return True

    if detect_date_candidates(cleaned) and _looks_like_plain_header(cleaned):
        return True

    if _PLACEHOLDER_DATE_RE.search(cleaned) and _looks_like_plain_header(cleaned):
        return True

    if not _looks_like_plain_header(cleaned) or next_line is None:
        return False

    next_cleaned = normalize_text(next_line)

    return (
        detect_position([next_cleaned]) is not None
        or bool(detect_date_candidates(next_cleaned))
        or _COMPANY_INDICATOR_RE.search(next_cleaned) is not None
    )


def _starts_new_metadata_entry(
    current_group: list[str],
    line: str,
    next_line: str | None,
) -> bool:
    current_position = detect_position(current_group)
    current_company = detect_company(current_group)
    current_date = detect_experience_dates(current_group)

    new_position = detect_position([line])
    new_prefix, new_location = split_company_and_location(line)
    new_company_is_strong = (
        _split_label(line)[0] in COMPANY_LABELS
        or (
            new_position is None
            and _COMPANY_INDICATOR_RE.search(new_prefix) is not None
        )
        or (new_location is not None and bool(new_prefix) and new_position is None)
    )
    new_date = bool(detect_date_candidates(line) or _PLACEHOLDER_DATE_RE.search(line))

    if current_position is not None and new_position is not None:
        return True

    if (
        current_company is not None
        and new_company_is_strong
        and (current_position is not None or current_date is not None)
    ):
        return True

    if (
        current_date is not None
        and new_date
        and (new_position is not None or new_company_is_strong)
    ):
        return True

    current_fields = sum(
        value is not None
        for value in (current_position, current_company, current_date)
    )

    return (
        current_fields >= 2
        and current_position is not None
        and new_position is None
        and _looks_like_plain_header(line)
        and next_line is not None
        and looks_like_experience_header(next_line)
    )


def group_experience_entries(
    experience_lines: list[str],
) -> list[list[str]]:
    lines = [
        normalized
        for raw_line in experience_lines
        if (normalized := normalize_text(raw_line))
    ]
    grouped_entries: list[list[str]] = []
    current_group: list[str] = []
    description_started = False
    description_wrap_open = False

    for index, line in enumerate(lines):
        next_line = lines[index + 1] if index + 1 < len(lines) else None

        if is_bullet_line(line):
            current_group.append(line)
            description_started = True
            description_wrap_open = not remove_bullet(line).endswith((".", "!", "?"))
            continue

        label, _ = _split_label(line)

        if label in DESCRIPTION_LABELS or _starts_description(line):
            current_group.append(line)
            description_started = True
            description_wrap_open = not line.endswith((".", "!", "?"))
            continue

        is_header = looks_like_experience_header(line, next_line)

        if description_started and is_header:
            if current_group:
                grouped_entries.append(current_group)
            current_group = [line]
            description_started = False
            description_wrap_open = False
            continue

        if description_started and description_wrap_open and not is_header:
            current_group.append(line)
            description_wrap_open = not line.endswith((".", "!", "?"))
            continue

        if (
            current_group
            and not description_started
            and _starts_new_metadata_entry(current_group, line, next_line)
        ):
            grouped_entries.append(current_group)
            current_group = []

        current_group.append(line)

    if current_group:
        grouped_entries.append(current_group)

    return grouped_entries


def _description_label_value(line: str) -> tuple[bool, str]:
    label, value = _split_label(remove_bullet(line))
    return label in DESCRIPTION_LABELS, value


def detect_experience_description_blocks(
    entry_lines: list[str],
) -> list[list[int]]:
    blocks: list[list[int]] = []
    current_block: list[int] | None = None
    wrap_open = False
    description_label_open = False

    for index, raw_line in enumerate(entry_lines):
        line = normalize_text(raw_line)

        if not line:
            continue

        if is_bullet_line(line):
            current_block = [index]
            blocks.append(current_block)
            wrap_open = not remove_bullet(line).endswith((".", "!", "?"))
            description_label_open = False
            continue

        has_label, label_value = _description_label_value(line)

        if has_label:
            description_label_open = not bool(label_value)

            if label_value:
                current_block = [index]
                blocks.append(current_block)
                wrap_open = not label_value.endswith((".", "!", "?"))
            else:
                current_block = None
                wrap_open = False
            continue

        if wrap_open and current_block is not None and not looks_like_experience_header(line):
            if _starts_description(line):
                current_block = [index]
                blocks.append(current_block)
            else:
                current_block.append(index)
            wrap_open = not line.endswith((".", "!", "?"))
            continue

        if description_label_open and not looks_like_experience_header(line):
            current_block = [index]
            blocks.append(current_block)
            wrap_open = not line.endswith((".", "!", "?"))
            description_label_open = False
            continue

        if _starts_description(line) and not looks_like_experience_header(line):
            current_block = [index]
            blocks.append(current_block)
            wrap_open = not line.endswith((".", "!", "?"))
            description_label_open = False
            continue

        current_block = None
        wrap_open = False
        description_label_open = False

    return blocks


def clean_experience_description_line(
    line: str,
    *,
    first_line: bool,
) -> str:
    cleaned = remove_bullet(line) if first_line else normalize_text(line)

    if first_line:
        has_label, value = _description_label_value(cleaned)

        if has_label:
            cleaned = value

    return cleaned.strip()


def extract_experience_descriptions(
    entry_lines: list[str],
) -> list[str]:
    descriptions: list[str] = []
    seen: set[str] = set()

    for block in detect_experience_description_blocks(entry_lines):
        parts = [
            clean_experience_description_line(
                entry_lines[line_index],
                first_line=position == 0,
            )
            for position, line_index in enumerate(block)
        ]
        description = normalize_text(" ".join(part for part in parts if part))

        if not description:
            continue

        key = description.casefold()

        if key in seen:
            continue

        seen.add(key)
        descriptions.append(description)

    return descriptions


def parse_experience_entry(entry_lines: list[str]) -> ExperienceRecord:
    record = ExperienceRecord(
        company=detect_company(entry_lines),
        position=detect_position(entry_lines),
        location=detect_location(entry_lines),
        descriptions=extract_experience_descriptions(entry_lines),
        raw_lines=entry_lines.copy(),
    )

    date = detect_experience_dates(entry_lines)

    if date is not None:
        record.start_date = date.start_date
        record.end_date = date.end_date
        record.is_current = date.is_current

    return record


def parse_experience(
    experience_lines: list[str],
) -> list[ExperienceRecord]:
    records = [
        parse_experience_entry(entry_lines)
        for entry_lines in group_experience_entries(experience_lines)
    ]

    # Some resumes print a company once and list several dated roles beneath it.
    for index in range(1, len(records)):
        record = records[index]
        previous = records[index - 1]

        if record.company is None and record.position is not None:
            record.company = previous.company

            if record.location is None:
                record.location = previous.location

    return records
