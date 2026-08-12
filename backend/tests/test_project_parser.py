from app.services.parser.project_parser import (
    group_project_entries,
    detect_project_name,
    detect_project_dates,
    extract_urls_from_line,
    detect_project_urls,
    detect_project_technologies,
    detect_standalone_technologies,
    parse_projects,
    split_project_description_label,
    is_project_description_boundary,
    is_explicit_description_line,
    is_project_description_bullet,
    is_unbulleted_description_start,
    detect_project_description_blocks,
    split_inline_project_description,
    clean_project_description_line,
    extract_project_descriptions,
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


def test_does_not_treat_delivered_as_a_live_url_label():
    result = detect_project_urls([
        "Delivered at https://project.example.com",
    ])

    assert result.live_url is None
    assert result.other_urls == [
        "https://project.example.com",
    ]


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


def test_canonicalizes_and_deduplicates_technology_casing():
    entry = [
        "Technologies: Python, python, PYTHON, Postgres, POSTGRESQL",
    ]

    assert detect_project_technologies(entry) == [
        "Python",
        "PostgreSQL",
    ]

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

def test_does_not_split_unpunctuated_description_bullets():
    lines = [
        "Inventory App | Python",
        "• Led backend development",
        "• Collaborated with frontend team",
    ]

    assert group_project_entries(lines) == [lines]


def test_metadata_after_description_does_not_start_project():
    lines = [
        "Inventory App",
        "• Built core API.",
        "Technologies: Python, FastAPI",
        "• Added tests.",
    ]

    assert group_project_entries(lines) == [lines]


def test_extracts_fields_from_bulleted_inline_project_header():
    entry = [
        "• ATS Resume Optimizer | Python, FastAPI | Jan 2026 – Present",
        "• Built a resume parser.",
    ]

    assert detect_project_name(entry) == "ATS Resume Optimizer"

    date = detect_project_dates(entry)
    assert date is not None
    assert date.start_date == NormalizedDate(year=2026, month=1)
    assert date.end_date is None
    assert date.is_current is True

    assert detect_project_technologies(entry) == ["Python", "FastAPI"]


def test_detects_name_from_bulleted_plain_project_header():
    assert detect_project_name([
        "• ATS Optimizer",
        "• Built a resume parser.",
    ]) == "ATS Optimizer"


def test_returns_none_when_project_name_line_contains_only_a_date():
    assert detect_project_name(["May 2025"]) is None


def test_splits_project_description_labels_and_content():
    assert split_project_description_label(
        "Description: Built an ATS parser"
    ) == ("description", "Built an ATS parser")
    assert split_project_description_label(
        "Project Overview: Resume analysis platform"
    ) == ("project overview", "Resume analysis platform")
    assert split_project_description_label(
        "Highlights:"
    ) == ("highlights", "")
    assert split_project_description_label(
        "Technologies: Python, FastAPI"
    ) == (None, "Technologies: Python, FastAPI")


def test_splits_inline_project_name_and_description():
    assert split_inline_project_description(
        "Food website: Developed website for serving and ordering food"
    ) == (
        "Food website",
        "Developed website for serving and ordering food",
    )
    assert split_inline_project_description(
        "Technologies: Python, FastAPI"
    ) == (None, "Technologies: Python, FastAPI")
    assert split_inline_project_description(
        "Description: Developed a food-ordering website"
    ) == (None, "Description: Developed a food-ordering website")
    assert split_inline_project_description(
        "Note: Developed a food-ordering website"
    ) == (None, "Note: Developed a food-ordering website")


def test_detects_standalone_project_description_boundaries():
    assert is_project_description_boundary("ATS Optimizer | Python")
    assert is_project_description_boundary("Technologies: Python, FastAPI")
    assert is_project_description_boundary("May 2025")
    assert is_project_description_boundary("https://example.com")

    assert not is_project_description_boundary(
        "Description: Built an ATS parser"
    )
    assert not is_project_description_boundary(
        "Project Overview: Resume analysis platform"
    )
    assert not is_project_description_boundary(
        "Deployed a demo at https://example.com"
    )
    assert not is_project_description_boundary(
        "Used Python and FastAPI to build the API"
    )


def test_detects_explicit_project_description_lines():
    assert is_explicit_description_line(
        "Description: Built an ATS parser"
    )
    assert is_explicit_description_line("Project Highlights:")
    assert not is_explicit_description_line(
        "Technologies: Python, FastAPI"
    )
    assert not is_explicit_description_line("Built an ATS parser")


def test_detects_project_description_bullets_only():
    assert is_project_description_bullet(
        "• Built an ATS parser using Python and FastAPI"
    )
    assert is_project_description_bullet(
        "• Deployed a demo at https://example.com"
    )
    assert is_project_description_bullet(
        "• Description: Reduced processing time by 40%"
    )

    assert not is_project_description_bullet(
        "• ATS Optimizer | Python"
    )
    assert not is_project_description_bullet(
        "• Technologies: Python, FastAPI"
    )
    assert not is_project_description_bullet("• May 2025")
    assert not is_project_description_bullet(
        "• https://example.com"
    )
    assert not is_project_description_bullet("Built an ATS parser")


def test_detects_unbulleted_project_description_starts():
    assert is_unbulleted_description_start(
        "Developed a FastAPI backend"
    )
    assert is_unbulleted_description_start(
        "A web application for small retailers"
    )
    assert is_unbulleted_description_start(
        "Description: Built an ATS parser"
    )

    assert not is_unbulleted_description_start(
        "ATS Optimizer | Python"
    )
    assert not is_unbulleted_description_start(
        "Technologies: Python, FastAPI"
    )
    assert not is_unbulleted_description_start("May 2025")
    assert not is_unbulleted_description_start(
        "• Built an ATS parser"
    )
    assert not is_unbulleted_description_start("Python API")


def test_detects_wrapped_project_description_blocks():
    entry = [
        "ATS Optimizer | Python",
        "• Built a resume parsing pipeline that processes PDF and",
        "DOCX documents using FastAPI and pdfplumber,",
        "improving extraction accuracy across varied formats.",
        "• Added comprehensive automated tests.",
    ]

    assert detect_project_description_blocks(entry) == [
        [1, 2, 3],
        [4],
    ]


def test_keeps_pdf_wrapped_description_in_one_project():
    records = parse_projects([
        "ATS Optimizer | Python",
        "• Built a resume pipeline that processes PDF and",
        "DOCX documents using FastAPI and pdfplumber,",
        "improving extraction accuracy across formats.",
    ])

    assert len(records) == 1
    assert records[0].name == "ATS Optimizer"
    assert records[0].descriptions == [
        (
            "Built a resume pipeline that processes PDF and "
            "DOCX documents using FastAPI and pdfplumber, "
            "improving extraction accuracy across formats."
        ),
    ]


def test_does_not_extract_long_project_title_as_description():
    records = parse_projects([
        "Machine Learning Resume Recommendation System",
        "• Built a recommendation model.",
    ])

    assert len(records) == 1
    assert records[0].name == (
        "Machine Learning Resume Recommendation System"
    )
    assert records[0].descriptions == [
        "Built a recommendation model.",
    ]


def test_description_blocks_respect_labels_and_boundaries():
    entry = [
        "Inventory App",
        "Description:",
        "Created inventory tools for small retailers",
        "using PostgreSQL for persistent storage.",
        "Technologies: Python, PostgreSQL",
        "Deployed a demo at https://example.com in May 2025.",
    ]

    assert detect_project_description_blocks(entry) == [
        [2, 3],
        [5],
    ]


def test_labeled_description_content_starts_its_own_block():
    entry = [
        "Project Overview: A web application for small retailers",
        "with real-time inventory reporting.",
        "GitHub: https://github.com/example/inventory",
    ]

    assert detect_project_description_blocks(entry) == [[0, 1]]


def test_description_label_aliases_stay_in_one_project():
    records = parse_projects([
        "ATS Optimizer",
        "Project Overview: Developed a resume parser",
        "Highlights: Built a FastAPI backend",
        "Impact: Reduced processing time by 40%",
    ])

    assert len(records) == 1
    assert records[0].name == "ATS Optimizer"
    assert records[0].descriptions == [
        "Developed a resume parser",
        "Built a FastAPI backend",
        "Reduced processing time by 40%",
    ]


def test_inline_project_description_provides_name_and_description_block():
    entry = [
        "Food website: Developed website for serving and ordering food",
        "with online payment and delivery tracking.",
        "Technologies: Python, Django",
    ]

    assert detect_project_name(entry) == "Food website"
    assert detect_project_description_blocks(entry) == [[0, 1]]


def test_groups_punctuated_inline_project_descriptions():
    records = parse_projects([
        "Food website: Developed an ordering website.",
        "Weather dashboard: Built a forecast interface.",
    ])

    assert [record.name for record in records] == [
        "Food website",
        "Weather dashboard",
    ]
    assert [record.descriptions for record in records] == [
        ["Developed an ordering website."],
        ["Built a forecast interface."],
    ]


def test_cleans_each_kind_of_project_description_line():
    assert clean_project_description_line(
        "• Built an ATS parser using Python",
        first_line=True,
    ) == "Built an ATS parser using Python"
    assert clean_project_description_line(
        "Description: Built an ATS parser",
        first_line=True,
    ) == "Built an ATS parser"
    assert clean_project_description_line(
        "Food website: Developed website for ordering food",
        first_line=True,
    ) == "Developed website for ordering food"
    assert clean_project_description_line(
        "DOCX documents using FastAPI and pdfplumber,",
        first_line=False,
    ) == "DOCX documents using FastAPI and pdfplumber,"
    assert clean_project_description_line(
        "Deployed at https://example.com in May 2025.",
        first_line=True,
    ) == "Deployed at https://example.com in May 2025."


def test_extracts_and_joins_project_description_blocks():
    entry = [
        "ATS Optimizer | Python",
        "• Built a resume parsing pipeline that processes PDF and",
        "DOCX documents using FastAPI and pdfplumber.",
        "• Deployed a demo at https://example.com in May 2025.",
        "Technologies: Python, FastAPI",
    ]

    assert extract_project_descriptions(entry) == [
        (
            "Built a resume parsing pipeline that processes PDF and "
            "DOCX documents using FastAPI and pdfplumber."
        ),
        "Deployed a demo at https://example.com in May 2025.",
    ]


def test_extracts_inline_project_description_without_project_name():
    entry = [
        "Food website: Developed website for serving and ordering food",
        "with online payment and delivery tracking.",
    ]

    assert extract_project_descriptions(entry) == [
        (
            "Developed website for serving and ordering food "
            "with online payment and delivery tracking."
        ),
    ]


def test_deduplicates_identical_project_descriptions():
    assert extract_project_descriptions([
        "• Built an ATS parser.",
        "• built an ats parser.",
    ]) == ["Built an ATS parser."]


def test_does_not_split_plain_description_lines():
    lines = [
        "Inventory App | Python",
        "• Built core API.",
        "A web application for small retailers",
        "• Added tests.",
    ]

    assert group_project_entries(lines) == [lines]


def test_does_not_split_title_case_description_bullets():
    lines = [
        "Inventory App | Python",
        "• Built core API.",
        "• Worked With Product Managers",
        "• Added tests.",
    ]

    assert group_project_entries(lines) == [lines]


def test_groups_consecutive_plain_project_titles():
    assert group_project_entries([
        "Project One",
        "Project Two",
    ]) == [
        ["Project One"],
        ["Project Two"],
    ]


def test_strips_supported_bullet_from_project_name():
    assert detect_project_name([
        "▪ ATS Optimizer",
        "▪ Built a parser.",
    ]) == "ATS Optimizer"


def test_does_not_use_plain_description_as_name_or_date():
    entry = [
        "Technologies: Python",
        "Built a resume parser using data from Jan 2022 - Dec 2024.",
    ]

    assert detect_project_name(entry) is None
    assert detect_project_dates(entry) is None


def test_cleans_explicit_name_with_inline_metadata():
    assert detect_project_name([
        "Project: ATS Optimizer | Python | Jan 2026 - Present",
    ]) == "ATS Optimizer"


def test_detects_common_labeled_technologies():
    assert detect_project_technologies([
        "Technologies: SQL, Vue.js, Tailwind CSS, Kubernetes",
    ]) == ["SQL", "Vue.js", "Tailwind CSS", "Kubernetes"]


def test_builds_project_records():
    records = parse_projects([
        "ATS Optimizer | Python | Jan 2026 - Present",
        "GitHub: https://github.com/user/ats-optimizer",
        "• Built a resume parser.",
    ])

    assert len(records) == 1
    assert records[0].name == "ATS Optimizer"
    assert records[0].technologies == ["Python"]
    assert records[0].start_date == NormalizedDate(year=2026, month=1)
    assert records[0].is_current is True
    assert records[0].github_url == "https://github.com/user/ats-optimizer"
    assert records[0].descriptions == ["Built a resume parser."]
