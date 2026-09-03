"""Extract and classify candidate requirements from job sections."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RequirementRecord:
    text: str
    category: str
    is_preferred: bool = False


REQUIREMENT_SECTIONS = (
    "requirements",
    "preferred_requirements",
    "education",
    "experience",
    "skills",
)

_LEADING_BULLET_RE = re.compile(
    r"^\s*(?:[-*•▪■◦‣]|\d+[.)])\s*"
)
_INLINE_BULLET_RE = re.compile(r"\s*[•▪■◦‣]\s*")
_PREFERRED_RE = re.compile(
    r"\b(?:preferred|desired|ideally|nice[ -]to[ -]have|bonus|a plus)\b",
    re.I,
)
_EDUCATION_RE = re.compile(
    r"\b(?:degree|bachelor'?s?|master'?s?|ph\.?d\.?|doctorate|diploma|GED)\b",
    re.I,
)
_EXPERIENCE_RE = re.compile(
    r"\b(?:experience|\d+(?:\.\d+)?\+?\s*(?:years?|yrs?))\b",
    re.I,
)
_CERTIFICATION_RE = re.compile(
    r"\b(?:certification|certified|certificate|licen[cs]e[sd]?)\b",
    re.I,
)
_SOFT_SKILL_RE = re.compile(
    r"\b(?:communication|collaboration|leadership|interpersonal|organized|"
    r"problem[ -]solving|teamwork|detail[ -]oriented|time management)\b",
    re.I,
)
_DOMAIN_RE = re.compile(
    r"\b(?:domain knowledge|industry knowledge|understanding of|knowledge of)\b",
    re.I,
)
_SKILL_RE = re.compile(
    r"\b(?:proficien(?:t|cy)|skilled in|ability to use|experience (?:using|with)|"
    r"familiar(?:ity)? with)\b",
    re.I,
)
_FALLBACK_REQUIREMENT_RE = re.compile(
    r"\b(?:must|required|requires?|requirements?|minimum|preferred|degree|certified|"
    r"proficien(?:t|cy)|\d+(?:\.\d+)?\+?\s*(?:years?|yrs?))\b",
    re.I,
)


def _clean_requirement(value: str) -> str:
    cleaned = _LEADING_BULLET_RE.sub("", value.strip())
    return re.sub(r"\s+", " ", cleaned).strip()


def _split_requirement_line(line: str, section_name: str) -> list[str]:
    """Split explicit bullets and compact skill lists without splitting prose."""
    bullet_parts = _INLINE_BULLET_RE.split(line)
    if section_name == "skills" and len(bullet_parts) == 1:
        bullet_parts = re.split(r"\s*[,;|]\s*", line)
    return [part for part in bullet_parts if part.strip()]


def _category_for(text: str, section_name: str) -> str:
    if section_name == "education" or _EDUCATION_RE.search(text):
        return "education"
    if section_name == "experience" or _EXPERIENCE_RE.search(text):
        return "experience"
    if _CERTIFICATION_RE.search(text):
        return "certification"
    if _SOFT_SKILL_RE.search(text):
        return "soft_skill"
    if _DOMAIN_RE.search(text):
        return "domain_knowledge"
    if section_name == "skills" or _SKILL_RE.search(text) or len(text.split()) <= 5:
        return "skill"
    return "other"


def _section_lines(
    sections: Mapping[str, Sequence[str]] | Sequence[str],
) -> list[tuple[str, str]]:
    if isinstance(sections, str) or not isinstance(sections, (Mapping, Sequence)):
        raise TypeError("sections must be a section mapping or a sequence of strings")

    if isinstance(sections, Mapping):
        explicit_lines: list[tuple[str, str]] = []
        for section_name, lines in sections.items():
            if section_name not in REQUIREMENT_SECTIONS:
                continue
            if isinstance(lines, str) or not isinstance(lines, Sequence):
                raise TypeError("section values must be sequences of strings")
            explicit_lines.extend((section_name, line) for line in lines)
        if explicit_lines:
            return explicit_lines

        overview_lines = sections.get("job_overview", ())
        if isinstance(overview_lines, str) or not isinstance(overview_lines, Sequence):
            raise TypeError("section values must be sequences of strings")
        if any(not isinstance(line, str) for line in overview_lines):
            raise TypeError("requirement lines must be strings")
        return [
            ("requirements", line)
            for line in overview_lines
            if _FALLBACK_REQUIREMENT_RE.search(_clean_requirement(line))
        ]

    return [("requirements", line) for line in sections]


def parse_requirements(
    sections: Mapping[str, Sequence[str]] | Sequence[str],
) -> list[RequirementRecord]:
    """Return unique required and preferred requirements in source order."""
    records: list[RequirementRecord] = []
    record_indexes: dict[str, int] = {}

    for section_name, raw_line in _section_lines(sections):
        if not isinstance(raw_line, str):
            raise TypeError("requirement lines must be strings")

        for part in _split_requirement_line(raw_line, section_name):
            text = _clean_requirement(part)
            if not text:
                continue

            is_preferred = (
                section_name == "preferred_requirements"
                or bool(_PREFERRED_RE.search(text))
            )
            record = RequirementRecord(
                text=text,
                category=_category_for(text, section_name),
                is_preferred=is_preferred,
            )
            key = text.casefold().rstrip(".;")
            existing_index = record_indexes.get(key)
            if existing_index is None:
                record_indexes[key] = len(records)
                records.append(record)
            elif records[existing_index].is_preferred and not is_preferred:
                # The required occurrence wins when the same text appears twice.
                records[existing_index] = record

    return records
