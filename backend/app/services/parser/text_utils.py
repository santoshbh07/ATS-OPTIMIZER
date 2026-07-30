import re


_BULLET_PATTERN = re.compile(
    r"^\s*(?:[•▪◦●○■□‣⁃*-]+)\s*"
)

_APOSTROPHE_REPLACEMENTS = {
    "\u2018": "'",   # left curly apostrophe
    "\u2019": "'",   # right curly apostrophe
    "\u02bc": "'",   # modifier-letter apostrophe
    "â€™": "'",       # common UTF-8 mojibake
    "â€˜": "'",       # common UTF-8 mojibake
}


def strip_bullet(text: str) -> str:
    return _BULLET_PATTERN.sub("", text, count=1)


_MOJIBAKE_REPLACEMENTS = {
    "â€¢": "•",
    "â–ª": "▪",
    "â—¦": "◦",
    "â—": "●",
    "â€“": "-",
    "â€”": "—",
    "â€™": "'",
    "Â·": "·",
}


def repair_common_mojibake(text: str) -> str:
    repaired = text

    for corrupted, correct in _MOJIBAKE_REPLACEMENTS.items():
        repaired = repaired.replace(corrupted, correct)

    return repaired

def normalize_text(text: str) -> str:
    normalized = repair_common_mojibake(text)

    for original, replacement in _APOSTROPHE_REPLACEMENTS.items():
        normalized = normalized.replace(original, replacement)

    return re.sub(r"\s+", " ", normalized).strip()