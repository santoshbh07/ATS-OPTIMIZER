from app.services.parser.date_parser import NormalizedDate
from app.services.parser.experience_parser import (
    detect_company,
    detect_experience_dates,
    detect_location,
    detect_position,
    extract_experience_descriptions,
    group_experience_entries,
    parse_experience,
    split_company_and_location,
)


def test_groups_company_first_entries_with_wrapped_bullets():
    lines = [
        "PNC Financial Services Group, Pittsburgh, PA June 2025-August 2025",
        "Technology Intern",
        "\u2022 Wrote code for an Angular front end which",
        "displayed product and team information.",
        "University of Pittsburgh, Pittsburgh, PA August 2024-May 2025",
        "Peer Tutor",
        "\u2022 Held weekly office hours.",
    ]

    assert group_experience_entries(lines) == [
        lines[:4],
        lines[4:],
    ]


def test_groups_position_first_entries():
    lines = [
        "Construction Engineering Intern June - August 2039",
        "Aecon, Montreal, Quebec",
        "\u2022 Ensured building codes were followed.",
        "Engineering Intern Summer 2038",
        "NCK, Montreal, Quebec",
        "\u2022 Inspected and maintained boilers.",
    ]

    assert group_experience_entries(lines) == [
        lines[:3],
        lines[3:],
    ]


def test_grouping_repairs_mojibake_and_ignores_empty_lines():
    lines = [
        "  Software Engineer | Jan 2023 - Present  ",
        "",
        "Acme Corp | Remote",
        "".join(map(chr, [0x00E2, 0x20AC, 0x00A2])) + " Built APIs.",
    ]

    assert group_experience_entries(lines) == [[
        "Software Engineer | Jan 2023 - Present",
        "Acme Corp | Remote",
        "\u2022 Built APIs.",
    ]]


def test_groups_consecutive_entries_without_bullets():
    lines = [
        "Acme Corp, Austin, TX | Jan 2020 - Dec 2022",
        "Software Engineer",
        "Beta Labs, Dallas, TX | Jan 2023 - Present",
        "Senior Software Engineer",
    ]

    assert group_experience_entries(lines) == [lines[:2], lines[2:]]


def test_splits_company_and_us_location():
    assert split_company_and_location(
        "PNC Financial Services Group, Pittsburgh, PA | June 2025-August 2025"
    ) == ("PNC Financial Services Group", "Pittsburgh, PA")


def test_splits_company_and_international_location():
    assert split_company_and_location(
        "Aecon, Montreal, Quebec"
    ) == ("Aecon", "Montreal, Quebec")


def test_detects_company_first_fields():
    entry = [
        "PNC Financial Services Group, Pittsburgh, PA June 2025-August 2025",
        "Technology Intern",
    ]

    assert detect_company(entry) == "PNC Financial Services Group"
    assert detect_position(entry) == "Technology Intern"
    assert detect_location(entry) == "Pittsburgh, PA"


def test_detects_position_first_fields():
    entry = [
        "Construction Engineering Intern June - August 2039",
        "Aecon, Montreal, Quebec",
    ]

    assert detect_company(entry) == "Aecon"
    assert detect_position(entry) == "Construction Engineering Intern"
    assert detect_location(entry) == "Montreal, Quebec"


def test_position_can_contain_organization_words():
    assert detect_position([
        "Collaborative User Experience Group Intern",
    ]) == "Collaborative User Experience Group Intern"
    assert detect_position([
        "Computer Lab Assistant 2038 - 2040",
    ]) == "Computer Lab Assistant"


def test_detects_inline_position_company_and_location():
    entry = [
        "Software Engineer, Acme Corp, Austin, TX | Jan 2021 - Present",
    ]

    assert detect_position(entry) == "Software Engineer"
    assert detect_company(entry) == "Acme Corp"
    assert detect_location(entry) == "Austin, TX"


def test_detects_position_at_company():
    entry = [
        "Senior Developer at Example Labs | Remote | 2022 - Present",
    ]

    assert detect_position(entry) == "Senior Developer"
    assert detect_company(entry) == "Example Labs"
    assert detect_location(entry) == "Remote"


def test_detects_explicit_labels():
    entry = [
        "Company: Example Labs",
        "Job Title: Data Analyst",
        "Location: Chicago, IL",
        "Dates: Jan 2022 - Dec 2024",
    ]

    assert detect_company(entry) == "Example Labs"
    assert detect_position(entry) == "Data Analyst"
    assert detect_location(entry) == "Chicago, IL"


def test_detects_experience_date_range():
    result = detect_experience_dates([
        "Software Engineer | Jan 2021 - March 2024",
    ])

    assert result is not None
    assert result.start_date == NormalizedDate(year=2021, month=1)
    assert result.end_date == NormalizedDate(year=2024, month=3)
    assert result.is_current is False


def test_detects_current_experience():
    result = detect_experience_dates([
        "Example Labs | Feb 2024 - Present",
    ])

    assert result is not None
    assert result.start_date == NormalizedDate(year=2024, month=2)
    assert result.end_date is None
    assert result.is_current is True


def test_date_range_wins_over_an_isolated_header_year():
    result = detect_experience_dates([
        "Acme Corp 2020",
        "Software Engineer | Jan 2021 - Dec 2023",
    ])

    assert result is not None
    assert result.start_date == NormalizedDate(year=2021, month=1)
    assert result.end_date == NormalizedDate(year=2023, month=12)


def test_ignores_dates_inside_description_bullets():
    assert detect_experience_dates([
        "Data Analyst",
        "Acme Corp",
        "\u2022 Compared sales from 2022 to 2024.",
    ]) is None


def test_date_metadata_is_not_used_as_company():
    assert detect_company([
        "Dates: Jan 2022 - Dec 2024",
    ]) is None


def test_extracts_bullets_and_joins_pdf_wrapping():
    entry = [
        "Software Engineer | Jan 2023 - Present",
        "Acme Corp, Austin, TX",
        "\u2022 Built a service that processes millions of",
        "records per day with reliable retry handling.",
        "\u2022 Reduced request latency by 40%.",
    ]

    assert extract_experience_descriptions(entry) == [
        "Built a service that processes millions of records per day with reliable retry handling.",
        "Reduced request latency by 40%.",
    ]


def test_extracts_labeled_and_unbulleted_descriptions():
    entry = [
        "Data Analyst",
        "Example Labs",
        "Responsibilities: Automated weekly reporting.",
        "Improved dashboard load time by 30%.",
    ]

    assert extract_experience_descriptions(entry) == [
        "Automated weekly reporting.",
        "Improved dashboard load time by 30%.",
    ]


def test_deduplicates_descriptions_case_insensitively():
    assert extract_experience_descriptions([
        "\u2022 Built internal APIs.",
        "\u2022 built internal apis.",
    ]) == ["Built internal APIs."]


def test_parse_experience_builds_records():
    records = parse_experience([
        "Acme Corp, Austin, TX | Jan 2021 - Present",
        "Senior Software Engineer",
        "\u2022 Built reliable APIs.",
    ])

    assert len(records) == 1
    assert records[0].company == "Acme Corp"
    assert records[0].position == "Senior Software Engineer"
    assert records[0].location == "Austin, TX"
    assert records[0].start_date == NormalizedDate(year=2021, month=1)
    assert records[0].end_date is None
    assert records[0].is_current is True
    assert records[0].descriptions == ["Built reliable APIs."]


def test_parse_experience_supports_multiple_roles_at_one_company():
    records = parse_experience([
        "Acme Corp, Austin, TX",
        "Software Engineer | Jan 2020 - Dec 2022",
        "\u2022 Built internal tools.",
        "Senior Software Engineer | Jan 2023 - Present",
        "\u2022 Led the platform team.",
    ])

    assert [record.position for record in records] == [
        "Software Engineer",
        "Senior Software Engineer",
    ]
    assert [record.company for record in records] == ["Acme Corp", "Acme Corp"]
    assert [record.location for record in records] == ["Austin, TX", "Austin, TX"]


def test_template_dates_do_not_leak_into_location_or_company():
    records = parse_experience([
        "Student Webmaster, Towson University, Towson, MD 9/XX - present",
        "\u2022 Maintained the university website.",
    ])

    assert records[0].position == "Student Webmaster"
    assert records[0].company == "Towson University"
    assert records[0].location == "Towson, MD"
    assert records[0].start_date is None


def test_plural_season_date_prefix_does_not_leak_into_company():
    records = parse_experience([
        "Summers 2015 - 2018 YMCA, Huntsville, AL",
        "Computer Teacher",
    ])

    assert records[0].company == "YMCA"
    assert records[0].position == "Computer Teacher"


def test_empty_experience_section_returns_no_records():
    assert parse_experience([]) == []
