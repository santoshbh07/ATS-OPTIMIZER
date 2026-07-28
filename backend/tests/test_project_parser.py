from app.services.parser.project_parser import (
    group_project_entries,
    detect_project_name,
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
    
def test_detects_name_before_pipe():
    assert detect_project_name(
        ["ATS Resume Optimizer | Python, FastAPI"]
    ) == "ATS Resume Optimizer"


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