"""Extract duties and responsibilities from job-description sections."""

from collections.abc import Mapping, Sequence
import re

from .section_extractor import is_header


_LEADING_BULLET_RE = re.compile(
    r"^\s*(?:[-*•▪■◦‣]|\d+[.)])\s*"
)
_INLINE_BULLET_RE = re.compile(r"\s*[•▪■◦‣]\s*")
_RESPONSIBILITY_START_RE = re.compile(
    r"^(?:you will|build|collaborate|create|deliver|design|develop|drive|lead|"
    r"maintain|manage|monitor|own|partner|perform|provide|support|test|write)\b",
    re.I,
)


def _clean_responsibility(value: str) -> str:
    cleaned = _LEADING_BULLET_RE.sub("", value.strip())
    return re.sub(r"\s+", " ", cleaned).strip()


def _responsibility_lines(
    sections: Mapping[str, Sequence[str]] | Sequence[str],
) -> Sequence[str]:
    if isinstance(sections, str) or not isinstance(sections, (Mapping, Sequence)):
        raise TypeError("sections must be a section mapping or a sequence of strings")

    if not isinstance(sections, Mapping):
        return sections

    explicit_lines = sections.get("responsibilities", ())
    if isinstance(explicit_lines, str) or not isinstance(explicit_lines, Sequence):
        raise TypeError("section values must be sequences of strings")
    if explicit_lines:
        return explicit_lines

    # Some short postings put duties in the overview without a dedicated header.
    overview_lines = sections.get("job_overview", ())
    if isinstance(overview_lines, str) or not isinstance(overview_lines, Sequence):
        raise TypeError("section values must be sequences of strings")
    if any(not isinstance(line, str) for line in overview_lines):
        raise TypeError("responsibility lines must be strings")
    return [
        line
        for line in overview_lines
        if _RESPONSIBILITY_START_RE.search(_clean_responsibility(line))
    ]


def parse_responsibilities(
    sections: Mapping[str, Sequence[str]] | Sequence[str],
) -> list[str]:
    """Return cleaned, unique responsibility statements in source order."""
    responsibilities: list[str] = []
    seen: set[str] = set()

    for raw_line in _responsibility_lines(sections):
        if not isinstance(raw_line, str):
            raise TypeError("responsibility lines must be strings")

        for part in _INLINE_BULLET_RE.split(raw_line):
            responsibility = _clean_responsibility(part)
            if not responsibility or is_header(responsibility):
                continue

            key = responsibility.casefold().rstrip(".;")
            if key in seen:
                continue
            seen.add(key)
            responsibilities.append(responsibility)

    return responsibilities
