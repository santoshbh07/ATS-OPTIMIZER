"""Extract structured certifications from resume sections."""

from dataclasses import dataclass, field
import re

from .date_parser import NormalizedDate, detect_date_candidates, remove_date_candidates
from .text_utils import normalize_text, strip_bullet


@dataclass
class CertificationRecord:
    name: str
    issuer: str | None = None
    issue_date: NormalizedDate | None = None
    expiration_date: NormalizedDate | None = None
    credential_id: str | None = None
    credential_url: str | None = None
    raw_lines: list[str] = field(default_factory=list)


_CERTIFICATION_LABEL_RE = re.compile(
    r"^(?:certification|certificate|credential|license)\s*:\s*",
    re.IGNORECASE,
)
_CERTIFICATION_MARKER_RE = re.compile(
    r"\b(?:certif(?:icate|ication|ied)|credential|licen[cs]e[sd]?)\b",
    re.IGNORECASE,
)
_KNOWN_CREDENTIAL_RE = re.compile(
    r"\b(?:AWS|Azure|CCNA|CISSP|CompTIA|Google Cloud|ITIL|Oracle|PMP|"
    r"Salesforce|Scrum(?:Master)?)\b|\bSecurity\+\b",
    re.IGNORECASE,
)
_ISSUER_NAME_RE = re.compile(
    r"^(?:Amazon Web Services|AWS|Cisco|CompTIA|Google|Google Cloud|"
    r"Microsoft|Oracle|Project Management Institute|Salesforce|"
    r"Scrum Alliance|Scrum\.org)$",
    re.IGNORECASE,
)
_EDUCATION_ONLY_RE = re.compile(
    r"\b(?:associate(?:'s)?|bachelor(?:'s)?|master(?:'s)?|doctorate|Ph\.?D\.?|"
    r"university|college|GPA|coursework|major|minor)\b",
    re.IGNORECASE,
)
_ISSUER_RE = re.compile(
    r"^(?:issued by|issuer|issuing organization)\s*:?\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_CREDENTIAL_ID_RE = re.compile(
    r"^(?:credential\s+)?(?:id|number|no\.?)\s*:?\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_DATE_LABEL_RE = re.compile(
    r"^(?:issued|earned|completed|expires?|expiration|valid until)\s*:?\s*",
    re.IGNORECASE,
)
_TRAILING_DATE_LABEL_RE = re.compile(
    r"\s*[-|·]\s*(?:issued|earned|completed|expires?|expiration|valid until)\s*$",
    re.IGNORECASE,
)
_EXPIRATION_RE = re.compile(r"\b(?:expires?|expiration|valid until)\b", re.I)
_SEPARATOR_RE = re.compile(r"\s+(?:\||·|•)\s+")


def _clean_line(line: str) -> str:
    return normalize_text(strip_bullet(line)).strip(" \t,;|")


def _is_metadata_line(line: str) -> bool:
    date_candidates = detect_date_candidates(line)
    only_contains_dates = bool(
        date_candidates
        and not remove_date_candidates(_DATE_LABEL_RE.sub("", line))
    )
    return bool(
        _ISSUER_RE.match(line)
        or _CREDENTIAL_ID_RE.match(line)
        or _URL_RE.fullmatch(line)
        or _ISSUER_NAME_RE.fullmatch(line)
        or (_DATE_LABEL_RE.match(line) and date_candidates)
        or only_contains_dates
    )


def _looks_like_certification(line: str, *, require_marker: bool) -> bool:
    if not line or _is_metadata_line(line):
        return False

    if require_marker:
        return bool(
            _CERTIFICATION_MARKER_RE.search(line)
            or _KNOWN_CREDENTIAL_RE.search(line)
        )

    return not (
        _EDUCATION_ONLY_RE.search(line)
        and not _CERTIFICATION_MARKER_RE.search(line)
    )


def _split_entries(
    certification_lines: list[str],
    *,
    require_marker: bool,
) -> list[list[str]]:
    entries: list[list[str]] = []
    current: list[str] = []

    for raw_line in certification_lines:
        if not isinstance(raw_line, str):
            raise TypeError("certification lines must be strings")

        line = _clean_line(raw_line)
        if not line:
            continue

        if _looks_like_certification(line, require_marker=require_marker):
            if current:
                entries.append(current)
            current = [raw_line]
        elif current and _is_metadata_line(line):
            current.append(raw_line)

    if current:
        entries.append(current)

    return entries


def _dates_from_lines(
    lines: list[str],
) -> tuple[NormalizedDate | None, NormalizedDate | None]:
    issue_date: NormalizedDate | None = None
    expiration_date: NormalizedDate | None = None

    for line in lines:
        candidates = detect_date_candidates(line)
        if not candidates:
            continue

        if _EXPIRATION_RE.search(line):
            expiration_date = (
                candidates[-1].end_date
                or candidates[-1].start_date
            )
            if len(candidates) > 1 and issue_date is None:
                issue_date = candidates[0].start_date
        elif issue_date is None:
            issue_date = candidates[0].start_date
            if candidates[0].end_date is not None:
                expiration_date = candidates[0].end_date
            elif len(candidates) > 1:
                expiration_date = candidates[-1].start_date

    return issue_date, expiration_date


def parse_certification_entry(entry_lines: list[str]) -> CertificationRecord:
    if isinstance(entry_lines, str) or not isinstance(entry_lines, list):
        raise TypeError("entry_lines must be a list of strings")
    if not entry_lines:
        raise ValueError("entry_lines cannot be empty")

    if any(not isinstance(line, str) for line in entry_lines):
        raise TypeError("entry_lines must be a list of strings")

    lines = [cleaned for line in entry_lines if (cleaned := _clean_line(line))]
    if not lines:
        raise ValueError("entry_lines must contain certification text")

    name_parts = _SEPARATOR_RE.split(lines[0])
    name = _CERTIFICATION_LABEL_RE.sub("", name_parts[0]).strip()
    issuer: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None

    for part in [*name_parts[1:], *lines[1:]]:
        issuer_match = _ISSUER_RE.match(part)
        credential_match = _CREDENTIAL_ID_RE.match(part)
        url_match = _URL_RE.search(part)

        if issuer_match:
            issuer = issuer_match.group("value").strip()
        elif credential_match:
            credential_id = credential_match.group("value").strip()
        elif url_match:
            credential_url = url_match.group(0).rstrip(".,;)")
        elif not detect_date_candidates(part) and issuer is None:
            issuer = part.strip()

    name = remove_date_candidates(name)
    name = _TRAILING_DATE_LABEL_RE.sub("", name)
    name = _DATE_LABEL_RE.sub("", name).strip(" \t,;|-")
    if not name:
        raise ValueError("certification name cannot be empty")

    issue_date, expiration_date = _dates_from_lines(lines)

    return CertificationRecord(
        name=name,
        issuer=issuer,
        issue_date=issue_date,
        expiration_date=expiration_date,
        credential_id=credential_id,
        credential_url=credential_url,
        raw_lines=entry_lines.copy(),
    )


def parse_certifications(
    certification_lines: list[str],
    *,
    require_marker: bool = False,
) -> list[CertificationRecord]:
    """Return unique certifications in source order.

    ``require_marker`` is used when scanning a mixed education section so
    ordinary degree and institution lines are not treated as certifications.
    """
    if isinstance(certification_lines, str) or not isinstance(
        certification_lines,
        list,
    ):
        raise TypeError("certification_lines must be a list of strings")

    records: list[CertificationRecord] = []
    seen: set[str] = set()

    for entry in _split_entries(
        certification_lines,
        require_marker=require_marker,
    ):
        record = parse_certification_entry(entry)
        key = record.name.casefold()
        if key in seen:
            continue
        seen.add(key)
        records.append(record)

    return records
