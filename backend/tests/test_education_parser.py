from app.services.parser.education_parser import (
    detect_degree,
    detect_gpa,
    detect_institution,
    detect_location,
    detect_minors,
    detect_study_fields,
    group_education_entries,
    parse_degree_entry,
    split_institution_and_location,
    parse_education
)

from app.services.parser.date_parser import NormalizedDate
import pytest


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("", None),
        ("   ", None),
        ("Bachelor of Science in Computer Science", ("Bachelor of Science", "bachelor")),
        ("associate OF arts", ("Associate of Arts", "associate")),
        ("B.S. Computer Science, May 2026", ("Bachelor of Science", "bachelor")),
        ("University of North Texas | BS Computer Science | May 2026", ("Bachelor of Science", "bachelor")),
        ("M S in Mathematics, GPA: 3.9", ("Master of Science", "master")),
        ("B.Sc. Information Technology", ("Bachelor of Science", "bachelor")),
        ("MSc Data Science", ("Master of Science", "master")),
        ("Ph.D. in Computer Science", ("Doctor of Philosophy", "doctorate")),
        ("EdD Education Leadership", ("Doctor of Education", "doctorate")),
        ("High School Diploma, 2022", ("High School Diploma", "high_school")),
        ("GED", ("GED", "high_school")),
        ("Bachelor's Degree in Information Technology", ("Bachelor's Degree", "bachelor")),
        ("Bachelors Degree", ("Bachelor's Degree", "bachelor")),
        ("Masters Degree", ("Master's Degree", "master")),
        ("Associate Degree", ("Associate Degree", "associate")),
        ("Expected Bachelor of Arts, May 2027", ("Bachelor of Arts", "bachelor")),
        ("Pursuing a Bachelor of Engineering", ("Bachelor of Engineering", "bachelor")),
        ("Candidate for a Master of Business Administration", ("Master of Business Administration", "master")),
        ("Bachelor of Business Administration / Bachelor's Degree", ("Bachelor of Business Administration", "bachelor")),
    ],
)
def test_detect_degree_supported_formats(line, expected):
    assert detect_degree(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "Business management experience",
        "Mastered Python and SQL",
        "Worked as a teaching assistant",
        "Mathematics Department",
        "Basic programming knowledge",
        "University of North Texas",
        "Computer Science Department",
    ],
)
def test_detect_degree_avoids_false_positives(line):
    assert detect_degree(line) is None

# testing multiple education entry
def test_groups_multiple_institution_first_entries():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Expected May 2028",
        "Butler Community College",
        "Associate of Science",
        "May 2026",
    ]
    
    result = group_education_entries(education_lines)

    assert result == [
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "Expected May 2028",
        ],
        [
            "Butler Community College",
            "Associate of Science",
            "May 2026",
        ],
    ]


# testing single education entry  
def test_groups_single_education_entry():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Expected May 2028",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "Expected May 2028",
        ]
    ]
    
# testing empty input
def test_return_empty_list_for_empty_input():
    result = group_education_entries([])

    assert result == []
    
# testing degree before insituiton
def test_keep_degree_before_institution_in_same_entry():
    education_lines = [
        "Bachelor of Science in Computer Science",
        "University of North Texas",
        "Expected May 2028",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "Bachelor of Science in Computer Science",
            "University of North Texas",
            "Expected May 2028",
        ]
    ]
    
# testing whitespace handeling
def test_removes_surrounding_whitespace():
    education_lines = [
        "  University of North Texas  ",
        " Bachelor of Science in Computer Science ",
        "",
        "   ",
        " Expected May 2028 ",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "Expected May 2028",
        ]
    ]

# testing institution detection
def test_detects_university_as_institution():
    result = detect_institution("University of North Texas")

    assert result == "University of North Texas"


def test_detects_college_as_institution():
    result = detect_institution("Butler Community College")

    assert result == "Butler Community College"

# testing non institution lines
def test_returns_none_for_non_institution_line():
    result = detect_institution(
        "Bachelor of Science in Computer Science"
    )

    assert result is None


def test_detects_named_community_college():
    assert detect_institution(["Butler Community College"]) == "Butler Community College"


def test_detects_university_of_name_format():
    assert detect_institution(["University of North Texas"]) == "University of North Texas"


def test_rejects_standalone_college_of_engineering():
    assert detect_institution(["College of Engineering"]) is None


def test_prefers_university_over_college_of_engineering():
    entry = [
        "College of Engineering",
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Expected May 2028",
    ]
    assert detect_institution(entry) == "University of North Texas"


def test_selection_does_not_depend_on_line_order():
    first = ["College of Engineering", "University of North Texas"]
    second = list(reversed(first))
    assert detect_institution(first) == detect_institution(second)


def test_rejects_department_as_institution():
    assert detect_institution(["Department of Computer Science"]) is None


def test_detects_institute_of_technology():
    entry = ["Massachusetts Institute of Technology"]
    assert detect_institution(entry) == "Massachusetts Institute of Technology"


def test_supports_real_institution_starting_with_college_of():
    assert detect_institution(["College of William & Mary"]) == "College of William & Mary"


def test_supports_distinctive_institution_starting_with_school_of():
    entry = ["School of the Art Institute of Chicago"]
    assert detect_institution(entry) == "School of the Art Institute of Chicago"


def test_returns_none_when_entry_has_no_institution():
    entry = [
        "Bachelor of Science in Mechanical Engineering",
        "May 2026",
    ]
    assert detect_institution(entry) is None


def test_removes_surrounding_whitespace_and_bullet():
    assert detect_institution(["  • University of North Texas  "]) == (
        "University of North Texas"
    )


def test_detects_separate_city_and_state_location():
    entry = [
        "University of North Texas",
        "Denton, TX",
        "Bachelor of Science in Computer Science",
    ]
    assert detect_location(entry) == "Denton, TX"


def test_splits_institution_and_location_separated_by_comma():
    result = split_institution_and_location(
        "University of North Texas, Denton, TX"
    )
    assert result == ("University of North Texas", "Denton, TX")


def test_splits_institution_and_location_separated_by_pipe():
    result = split_institution_and_location(
        "Butler Community College | El Dorado, KS"
    )
    assert result == ("Butler Community College", "El Dorado, KS")


def test_splits_institution_and_location_separated_by_dash():
    result = split_institution_and_location(
        "Texas A&M University — College Station, Texas"
    )
    assert result == ("Texas A&M University", "College Station, Texas")


def test_detects_international_location():
    entry = ["Kathmandu University, Dhulikhel, Nepal"]
    assert detect_location(entry) == "Dhulikhel, Nepal"


def test_does_not_treat_degree_and_major_as_location():
    assert detect_location(["Bachelor of Science, Computer Science"]) is None


def test_does_not_treat_college_of_engineering_as_location():
    assert detect_location(["College of Engineering"]) is None


def test_preserves_line_when_location_split_is_uncertain():
    line = "University of North Texas, School of Engineering"
    assert split_institution_and_location(line) == (line, None)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "Bachelor of Science in Computer Science",
            ["Computer Science"],
        ),
        (
            "Bachelor of Arts in Psychology",
            ["Psychology"],
        ),
        (
            "Master of Science in Data Science",
            ["Data Science"],
        ),
        (
            "B.S. in Software Engineering",
            ["Software Engineering"],
        ),
        (
            "B.S., Computer Science",
            ["Computer Science"],
        ),
        (
            "MBA in Finance",
            ["Finance"],
        ),
        (
            "Computer Science, Bachelor of Science",
            ["Computer Science"],
        ),
        (
            "Mechanical Engineering (B.S.)",
            ["Mechanical Engineering"],
        ),
        (
            "Major: Computer Science",
            ["Computer Science"],
        ),
        (
            "Major in Mathematics",
            ["Mathematics"],
        ),
        (
            "Field of Study: Information Technology",
            ["Information Technology"],
        ),
        (
            "Program: Data Analytics",
            ["Data Analytics"],
        ),
        (
            "B.S. in Computer Science, Minor in Mathematics",
            ["Computer Science"],
        ),
        (
            "Bachelor of Arts in Psychology, GPA: 3.80",
            ["Psychology"],
        ),
        (
            "B.S., Data Science, Expected May 2027",
            ["Data Science"],
        ),
        (
            "Major: Comp Sci",
            ["Computer Science"],
        ),
        (
            "B.S. in Computer Sciences",
            ["Computer Science"],
        ),
        (
            "Field of Study: Business Admin",
            ["Business Administration"],
        ),
        (
            "Major: CS",
            ["Computer Science"],
        ),
        (
            "B.S. in CS",
            ["Computer Science"],
        ),
        (
            "Field of Study: IT",
            ["Information Technology"],
        ),
    ],
)
def test_detect_study_fields_supported_formats(line, expected):
    assert detect_study_fields(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "University of North Texas",
        "Denton, TX",
        "May 2027",
        "Expected Graduation: May 2027",
        "GPA: 3.85",
        "Dean's List",
        "College of Engineering",
        "School of Computer Science",
        "Department of Mathematics",
        "Relevant Coursework: Algorithms and Databases",
        "Bachelor of Science",
        "Master of Science",
        "Associate of Arts",
        "IT Support Assistant",
        "Worked with IS systems",
        "Business management experience",
    ],
)
def test_detect_study_fields_avoids_false_positives(line):
    assert detect_study_fields(line) == []


def test_parse_degree_entry_populates_field_without_changing_other_fields():
    lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Expected May 2027",
    ]

    record = parse_degree_entry(lines)

    assert record.institution == "University of North Texas"
    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]

    assert record.start_date is None
    
    assert record.end_date is not None
    assert record.end_date.year == 2027
    assert record.end_date.month == 5
    
    assert record.gpa is None
    assert record.raw_lines == lines
    
    assert record.is_expected is True
    assert record.is_current is False


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("GPA: 3.85", "3.85"),
        ("gpa 3.8", "3.8"),
        ("Overall GPA - 3.72", "3.72"),
        ("Cumulative GPA: 3.850", "3.850"),
        ("GPA: 3.85/4.00", "3.85"),
        ("GPA: 4.5/5.0", "4.5"),
        ("GPA: 5.0/5.00", "5.0"),
        ("GPA: 0.0/4.0", "0.0"),
        ("GPA: 8.6 / 10", None),
        ("", None),
        ("Graduated in 2024", None),
        ("3.85 years of experience", None),
        ("GPA: N/A", None),
        ("Major GPA: 3.90", None),
        ("GPA: 4.5/4.0", None),
        ("GPA: 4.1", None),
        ("GPA: 5.1/5.0", None),
        ("GPA: 3.8/10", None),
        ("GPA: -1.0", None),
    ],
)
def test_detect_gpa_supported_and_invalid_formats(line, expected):
    assert detect_gpa(line) == expected


def test_detect_gpa_prefers_cumulative_over_later_major_gpa():
    assert detect_gpa("Cumulative GPA: 3.72 | Major GPA: 3.91") == "3.72"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Minor in Mathematics", ["Mathematics"]),
        ("Minor: Psychology", ["Psychology"]),
        ("Mathematics Minor", ["Mathematics"]),
        ("B.S. in Computer Science, Minor in Statistics", ["Statistics"]),
        ("Minors in Mathematics and Physics", ["Mathematics", "Physics"]),
        ("Minors: Finance, Economics", ["Finance", "Economics"]),
        ("Double Minor: Mathematics; Statistics", ["Mathematics", "Statistics"]),
        ("Minor in Comp Sci", ["Computer Science"]),
        ("Minor: Business Admin", ["Business Administration"]),
        ("Minor in Humanitarian Studies", ["Humanitarian Studies"]),
        ("Minor in Mathematics, GPA: 3.85", ["Mathematics"]),
        (
            "Minors in Mathematics and Physics | Expected May 2027",
            ["Mathematics", "Physics"],
        ),
        ("Minors: Mathematics, Math", ["Mathematics"]),
    ],
)
def test_detect_minors_supported_formats(line, expected):
    assert detect_minors(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "University of North Texas",
        "Mathematics and Physics",
        "Relevant Coursework: Mathematics and Physics",
        "Played a minor role in the project",
        "Minor formatting changes",
        "Students who are minors",
        "No Minor Declared",
        "Minor: None",
    ],
)
def test_detect_minors_rejects_invalid_lines(line):
    assert detect_minors(line) == []


def test_parse_degree_entry_populates_gpa_and_minors():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "Minor in Mathematics",
        "GPA: 3.82/4.00",
        "Expected May 2027",
    ]

    record = parse_degree_entry(education_lines)

    assert record.institution == "University of North Texas"
    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]
    assert record.minors == ["Mathematics"]
    assert record.gpa == "3.82"
    assert record.raw_lines == education_lines
    
    
def test_starts_new_entry_when_second_degree_belongs_to_next_institution():
    education_lines = [
        "Bachelor of Science in Computer Science",
        "University of North Texas, Denton, TX",
        "Associate of Science in Mathematics",
        "Butler Community College, El Dorado, KS",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "Bachelor of Science in Computer Science",
            "University of North Texas, Denton, TX",
        ],
        [
            "Associate of Science in Mathematics",
            "Butler Community College, El Dorado, KS",
        ],
    ]


def test_starts_new_entry_when_second_institution_is_found():
    education_lines = [
        "University of North Texas, Denton, TX",
        "Bachelor of Science in Computer Science",
        "Butler Community College, El Dorado, KS",
        "Associate of Science in Mathematics",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "University of North Texas, Denton, TX",
            "Bachelor of Science in Computer Science",
        ],
        [
            "Butler Community College, El Dorado, KS",
            "Associate of Science in Mathematics",
        ],
    ]


def test_keeps_degree_before_institution_in_same_entry():
    education_lines = [
        "Bachelor of Science in Computer Science",
        "University of North Texas, Denton, TX",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "Bachelor of Science in Computer Science",
            "University of North Texas, Denton, TX",
        ],
    ]


def test_splits_multiple_degrees_under_same_institution():
    education_lines = [
        "University of North Texas, Denton, TX",
        "Bachelor of Science in Computer Science",
        "Bachelor of Arts in Mathematics",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            "University of North Texas, Denton, TX",
            "Bachelor of Science in Computer Science",
        ],
        [
            "Bachelor of Arts in Mathematics",
        ],
    ]

def test_detect_study_fields_returns_both_double_majors():
    result = detect_study_fields(
        "Double Major: Computer Science and Mathematics"
    )

    assert result == [
        "Computer Science",
        "Mathematics",
    ]


def test_detect_study_fields_returns_multiple_degree_adjacent_fields():
    result = detect_study_fields(
        "Bachelor of Science in Computer Science and Mathematics"
    )

    assert result == [
        "Computer Science",
        "Mathematics",
    ]


def test_detect_study_fields_prefers_longest_alias():
    result = detect_study_fields(
        "Major: Management Information Systems"
    )

    assert result == [
        "Management Information Systems",
    ]


def test_detect_study_fields_deduplicates_fields():
    result = detect_study_fields(
        "Double Major: Computer Science and Computer Science"
    )

    assert result == [
        "Computer Science",
    ]


def test_parse_degree_entry_stores_multiple_fields():
    lines = [
        "University of North Texas",
        "Bachelor of Science",
        "Double Major: Computer Science and Mathematics",
    ]

    record = parse_degree_entry(lines)

    assert record.fields_of_study == [
        "Computer Science",
        "Mathematics",
    ]
    
def test_parse_education_returns_degree_records():
    education_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "GPA: 3.82",
    ]

    records = parse_education(education_lines)

    assert len(records) == 1
    assert records[0].institution == "University of North Texas"
    assert records[0].degree_name == "Bachelor of Science"
    assert records[0].fields_of_study == ["Computer Science"]
    assert records[0].gpa == "3.82"
    
def test_groups_named_engineering_degrees_even_when_not_canonicalized():
    education_lines = [
        (
            "Master of Building Engineering – "
            "Specialization in Construction Management 2040"
        ),
        "Concordia University, Montreal, Quebec",
        "Grade Point Average: 4.0/4.3",
        "Bachelor of Civil and Environmental Engineering 2038",
        "Seoul National University, Seoul, South Korea",
    ]

    result = group_education_entries(education_lines)

    assert result == [
        [
            (
                "Master of Building Engineering – "
                "Specialization in Construction Management 2040"
            ),
            "Concordia University, Montreal, Quebec",
            "Grade Point Average: 4.0/4.3",
        ],
        [
            "Bachelor of Civil and Environmental Engineering 2038",
            "Seoul National University, Seoul, South Korea",
        ],
    ]
    
def test_parse_degree_entry_without_date_keeps_date_fields_empty():
    entry_lines = [
        "University of North Texas",
        "Bachelor of Science in Computer Science",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.start_date is None
    assert record.end_date is None
    assert record.is_expected is False
    assert record.is_current is False

def test_parse_degree_entry_without_institution_keeps_institution_none():
    entry_lines = [
        "Bachelor of Science in Computer Science",
        "Expected Graduation: May 2026",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.institution is None
    
def test_parse_degree_entry_without_institution_parses_remaining_fields():
    entry_lines = [
        "Bachelor of Science in Computer Science",
        "Expected Graduation: May 2026",
        "GPA: 3.66",
    ]

    record = parse_degree_entry(entry_lines)

    assert record.institution is None

    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == ["Computer Science"]

    assert record.end_date is not None
    assert record.end_date.year == 2026
    assert record.end_date.month == 5
    assert record.is_expected is True

    assert record.gpa == "3.66"
    
@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # Unknown fields in strong academic contexts
        (
            "Bachelor of Science in Geology",
            ["Geology"],
        ),
        (
            "Major: Marine Biology",
            ["Marine Biology"],
        ),
        (
            "Field of Study: Urban Planning",
            ["Urban Planning"],
        ),
        (
            "Program in Game Design",
            ["Game Design"],
        ),
        (
            "Concentration: Computational Biology",
            ["Computational Biology"],
        ),
        (
            "Bachelor of Arts in Peace and Conflict Studies",
            ["Peace and Conflict Studies"],
        ),

        # Known aliases and abbreviations
        (
            "B.S., Computer Science",
            ["Computer Science"],
        ),
        (
            "Major: CS",
            ["Computer Science"],
        ),
        (
            "Field of Study: Business Admin",
            ["Business Administration"],
        ),

        # Multiple fields
        (
            "Double Major: Computer Science and Mathematics",
            ["Computer Science", "Mathematics"],
        ),
        (
            "Double Major: Geology and Anthropology",
            ["Geology", "Anthropology"],
        ),

        # Embedded engineering fields
        (
            "Bachelor of Civil and Environmental Engineering",
            ["Civil and Environmental Engineering"],
        ),
        (
            "Master of Building Engineering",
            ["Building Engineering"],
        ),

        # Metadata trimming
        (
            "Bachelor of Science in Geology, GPA: 3.8",
            ["Geology"],
        ),
        (
            "Bachelor of Science in Geology, Minor in Mathematics",
            ["Geology"],
        ),

        # No field
        (
            "Bachelor of Science",
            [],
        ),
    ],
)
def test_detect_study_fields(line, expected):
    assert detect_study_fields(line) == expected

@pytest.mark.parametrize(
    "line",
    [
        "",
        "Geology Club Member",
        "Interested in Geology",
        "Department of Geology",
        "Coursework: Geology",
        "Relevant Coursework: Geology",
        "School of Environmental Science",
        "University Department of Anthropology",
    ],
)
def test_study_fields_require_strong_academic_context(line):
    assert detect_study_fields(line) == []

def test_parse_degree_entry_collects_field_and_specialization():
    record = parse_degree_entry(
        [
            "Example University",
            "Bachelor of Science in Geology",
            "Concentration: Computational Biology",
        ]
    )

    assert record.degree_name == "Bachelor of Science"
    assert record.degree_level == "bachelor"
    assert record.fields_of_study == [
        "Geology",
        "Computational Biology",
    ]
    assert record.specializations == [
        "Computational Biology",
    ]
    
def test_expected_marker_modifies_attached_education_range():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            "Sep 2022 - May 2026 (Expected)",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True
    assert record.is_current is False


def test_education_range_wins_over_isolated_graduation_date():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Expected May 2026",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True


def test_expected_marker_does_not_modify_unrelated_range():
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Expected May 2027",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is False


@pytest.mark.parametrize(
    "line",
    [
        "Expected May 2026",
        "Expected Graduation: May 2026",
        "Anticipated May 2026",
        "May 2026 (Expected)",
    ],
)
def test_expected_marker_applies_to_isolated_graduation_date(line):
    record = parse_degree_entry(
        [
            "University of North Texas",
            "Bachelor of Science in Computer Science",
            line,
        ]
    )

    assert record.start_date is None
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )
    assert record.is_expected is True


def test_education_prefers_range_even_when_single_date_appears_first():
    record = parse_degree_entry(
        [
            "May 2026",
            "Sep 2022 - May 2026",
        ]
    )

    assert record.start_date == NormalizedDate(
        year=2022,
        month=9,
    )
    assert record.end_date == NormalizedDate(
        year=2026,
        month=5,
    )

@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # Valid unscaled GPA values: 0.0–4.0
        ("GPA: 0", "0"),
        ("GPA: 0.0", "0.0"),
        ("GPA: 2.75", "2.75"),
        ("gpa 3.8", "3.8"),
        ("GPA=3.85", "3.85"),
        ("Overall GPA - 3.72", "3.72"),
        ("Cumulative GPA: 3.850", "3.850"),
        ("Grade Point Average: 4.0", "4.0"),

        # Valid 4-point scale
        ("GPA: 0.0/4.0", "0.0"),
        ("GPA: 3.85/4", "3.85"),
        ("GPA: 3.85 / 4.00", "3.85"),
        ("GPA: 4.0/4.0", "4.0"),

        # Valid 5-point scale
        ("GPA: 0.0/5.0", "0.0"),
        ("GPA: 4.0/5", "4.0"),
        ("GPA: 4.5/5.0", "4.5"),
        ("GPA: 5.0/5.00", "5.0"),

        # Score exceeds allowed range
        ("GPA: 4.01", None),
        ("GPA: 5.0", None),
        ("GPA: 4.1/4.0", None),
        ("GPA: 4.5/4.0", None),
        ("GPA: 5.1/5.0", None),
        ("GPA: 8.6/10", None),

        # Unsupported scales
        ("GPA: 3.8/4.5", None),
        ("GPA: 3.8/6.0", None),
        ("GPA: 3.8/10", None),

        # Invalid or missing values
        ("GPA: -1.0", None),
        ("GPA: N/A", None),
        ("GPA:", None),
        ("GPA: five", None),
        ("", None),

        # Missing or excluded GPA context
        ("3.85", None),
        ("3.85 years of experience", None),
        ("Graduated in 2024", None),
        ("Major GPA: 3.90", None),
    ],
)
def test_detect_gpa_ranges_and_scales(line, expected):
    assert detect_gpa(line) == expected