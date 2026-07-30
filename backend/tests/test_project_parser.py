from app.services.parser.project_parser import (
    group_project_entries,
    detect_project_name,
    detect_project_dates,
    extract_urls_from_line,
    detect_project_urls,
    detect_project_technologies,
    detect_standalone_technologies,
)

from app.services.parser.text_utils import normalize_text

from app.services.parser.date_parser import(
    NormalizedDate
)
def test_groups_one_project():
    lines = [
        "ATS Resume Optimizer | Python, FastAPI",
        "• Built a resume analysis API.",
    ]
    
    assert group_project_entries(lines) == [
        [
            "ATS Resume Optimizer | Python, FastAPI",
            "• Built a resume analysis API.",
        ]
    ]
    
def test_groups_multiple_projects_without_blank_lines():
    lines = [
        "ATS Resume Optimizer | Python, FastAPI",
        "• Built a resume parser.",
        "Weather Dashboard | JavaScript, React",
        "• Retrieved real-time weather data.",
    ]

    assert group_project_entries(lines) == [
        [
            "ATS Resume Optimizer | Python, FastAPI",
            "• Built a resume parser.",
        ],
        [
            "Weather Dashboard | JavaScript, React",
            "• Retrieved real-time weather data.",
        ],
    ]


def test_grouping_ignores_empty_lines_and_trims_whitespace():
    lines = [
        "  ATS Resume Optimizer | Python, FastAPI  ",
        "",
        "  • Built a resume parser.  ",
        "   ",
    ]

    assert group_project_entries(lines) == [
        [
            "ATS Resume Optimizer | Python, FastAPI",
            "• Built a resume parser.",
        ]
    ]
    
def test_keeps_metadata_before_first_bullet_in_same_entry():
    lines = [
        "ATS Resume Optimizer",
        "Technologies: Python, FastAPI",
        "January 2026 - Present",
        "GitHub: github.com/example/ats-optimizer",
        "• Built a resume parsing pipeline.",
    ]

    assert group_project_entries(lines) == [
        [
            "ATS Resume Optimizer",
            "Technologies: Python, FastAPI",
            "January 2026 - Present",
            "GitHub: github.com/example/ats-optimizer",
            "• Built a resume parsing pipeline.",
        ]
    ]
    
def test_detects_name_before_inline_separator():
    entry = [
        "ATS Resume Optimizer | Python, FastAPI",
        "• Built a resume parser.",
    ]

    assert detect_project_name(entry) == "ATS Resume Optimizer"


def test_detects_explicit_project_label():
    entry = [
        "Project: ATS Resume Optimizer",
        "Technologies: Python, FastAPI",
    ]

    assert detect_project_name(entry) == "ATS Resume Optimizer"


def test_uses_first_unlabeled_metadata_free_line():
    entry = [
        "ATS Resume Optimizer",
        "Technologies: Python, FastAPI",
        "• Built a resume parser.",
    ]

    assert detect_project_name(entry) == "ATS Resume Optimizer"


def test_returns_none_when_no_name_is_identifiable():
    entry = [
        "Technologies: Python, FastAPI",
        "GitHub: github.com/example/project",
        "• Built a resume parser.",
    ]

    assert detect_project_name(entry) is None

def test_preserves_hyphen_inside_name():
    assert detect_project_name(
        ["AI-Powered Resume Optimizer | Python"]
    ) == "AI-Powered Resume Optimizer"


def test_detects_plain_name():
    assert detect_project_name(
        [
            "ATS Resume Optimizer",
            "Technologies: Python, FastAPI",
            "• Built a parser.",
        ]
    ) == "ATS Resume Optimizer"

def test_detects_plain_name_removing_dates():
    assert detect_project_name(
        [
            "ATS Resume Optimizer may 2025",
            "Technologies: Python, FastAPI",
            "• Built a parser.",
        ]
    ) == "ATS Resume Optimizer"

def test_does_not_use_metadata_as_name():
    assert detect_project_name(
        [
            "Technologies: Python, FastAPI",
            "GitHub: github.com/example/project",
            "• Built a parser.",
        ]
    ) is None
    
def test_skips_empty_lines():
    entry = [
        "",
        "   ",
        "Weather Dashboard",
        "• Retrieved weather data.",
    ]

    assert detect_project_name(entry) == "Weather Dashboard"

def test_detects_project_date_range():
    entry = [
        "ATS Resume Optimizer | Python | Jan 2026 – Present",
        "• Built a resume parser.",
    ]
    
    result = detect_project_dates(entry)

    assert result is not None
    assert result.start_date == NormalizedDate(year=2026, month=1)
    assert result.end_date is None
    assert result.is_current is True

def test_detects_date_on_separate_line():
    entry = [
        "Weather Dashboard",
        "May 2025",
        "Technologies: JavaScript, React",
    ]

    result = detect_project_dates(entry)

    assert result is not None
    assert result.start_date == NormalizedDate(year=2025, month=5)
    assert result.end_date is None
    assert result.is_current is False


def test_returns_none_without_date():
    entry = [
        "ATS Resume Optimizer | Python, FastAPI",
        "• Built a resume parser.",
    ]

    assert detect_project_dates(entry) is None


def test_ignores_date_inside_description_bullet():
    entry = [
        "Historical Data Dashboard | Python",
        "• Compared economic records from 2022 to 2024.",
    ]

    assert detect_project_dates(entry) is None
    
def test_extracts_urls_from_line():
    entry = "GitHub: https://github.com/user/project | Demo: https://example.com"
    
    result = extract_urls_from_line(entry)
    assert result == [
      "https://github.com/user/project",
      "https://example.com",
     ]

def test_detects_github_url():
    result = detect_project_urls([
        "GitHub: github.com/user/project",
    ])

    assert result.github_url == "github.com/user/project"
    assert result.live_url is None
    assert result.other_urls == []


def test_detects_live_demo_url():
    result = detect_project_urls([
        "Live Demo: https://project.example.com",
    ])

    assert result.github_url is None
    assert result.live_url == "https://project.example.com"
    assert result.other_urls == []


def test_classifies_unlabeled_url_as_other():
    result = detect_project_urls([
        "Project Link: https://example.com/project",
    ])

    assert result.github_url is None
    assert result.live_url is None
    assert result.other_urls == [
        "https://example.com/project",
    ]


def test_detects_multiple_urls():
    result = detect_project_urls([
        (
            "GitHub: https://github.com/user/project | "
            "Demo: https://project.example.com"
        ),
    ])

    assert result.github_url == (
        "https://github.com/user/project"
    )
    assert result.live_url == (
        "https://project.example.com"
    )
    
def test_detects_explicit_technologies():
    entry = ["Technologies: Python, FastAPI, PostgreSQL"]
    result = detect_project_technologies(entry)

    assert result == ["Python", "FastAPI", "PostgreSQL"]

def test_detects_explicit_technologies_with_differnt_alias():
    entry = ["Tech Stack: React | TypeScript | NodeJS"]
    result = detect_project_technologies(entry)

    assert result == ["React", "TypeScript", "Node.js"]

def test_detects_inline_technologies_with_project_header_and_date():
    entry = ["ATS Resume Optimizer | Python, FastAPI | Jan 2026 – Present"]
    result = detect_project_technologies(entry)

    assert result == ["Python", "FastAPI"]

def test_detects_technologies_only():
    entry = ["Technologies: Python, Teamwork, FastAPI"]
    result = detect_project_technologies(entry)

    assert result == ["Python", "FastAPI"]

def test_detects_one_technology_if_multiple_word_exist():
    entry = ["Built With: Python, Postgres, sklearn, Python"]
    result = detect_project_technologies(entry)
    assert result == ["Python", "PostgreSQL", "scikit-learn"]

def test_detects_technologies_whitout_tech_header():
    entry = ["Python, Postgres, sklearn, Python"]
    result = detect_project_technologies(entry)
    assert result == ["Python", "PostgreSQL", "scikit-learn"]
    
def test_detects_pipe_separated_standalone_stack():
    result = detect_standalone_technologies(
        "React | TypeScript | Node.js"
    )

    assert result == [
        "React",
        "TypeScript",
        "Node.js",
    ]
    
def test_grouping_repairs_mojibake_bullet():
    lines = [
        "Project One | Python",
        "â€¢ Built feature one.",
        "Project Two | Java",
        "â€¢ Built feature two.",
    ]

    assert group_project_entries(lines) == [
        [
            "Project One | Python",
            "• Built feature one.",
        ],
        [
            "Project Two | Java",
            "• Built feature two.",
        ],
    ]
    
def test_normalize_text_repairs_mojibake():
    assert normalize_text(
        "â€¢ Project â€“ Python"
    ) == "• Project - Python"
    
def test_groups_projects_with_multiline_metadata():
    lines = [
        "ATS Resume Optimizer",
        "Technologies: Python, FastAPI",
        "January 2026 - Present",
        "GitHub: github.com/example/ats",
        "• Built a resume parser.",
        "Weather Dashboard",
        "Technologies: React, JavaScript",
        "May 2025",
        "• Displayed real-time weather information.",
    ]

    assert group_project_entries(lines) == [
        [
            "ATS Resume Optimizer",
            "Technologies: Python, FastAPI",
            "January 2026 - Present",
            "GitHub: github.com/example/ats",
            "• Built a resume parser.",
        ],
        [
            "Weather Dashboard",
            "Technologies: React, JavaScript",
            "May 2025",
            "• Displayed real-time weather information.",
        ],
    ]
    
def test_bullet_project_header():
    entry = ["• ATS Optimizer",
             "• ML Project"]
    
    result = group_project_entries(entry)
    assert result == [
        ["• ATS Optimizer"],
        ["• ML Project"]
    ]