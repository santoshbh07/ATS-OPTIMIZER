from app.services.resume_parsing.education_parser import group_education_entries


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


def test_return_empty_list_for_empty_input():
    result = group_education_entries([])

    assert result == []


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


def test_splits_abbreviated_degrees_under_same_institution():
    education_lines = [
        "Example University",
        "MBA in Finance",
        "MBA in Marketing",
    ]

    assert group_education_entries(education_lines) == [
        ["Example University", "MBA in Finance"],
        ["MBA in Marketing"],
    ]


def test_splits_field_first_degrees_under_same_institution():
    education_lines = [
        "Example University",
        "Computer Science, Bachelor of Science",
        "Mathematics, Bachelor of Arts",
    ]

    assert group_education_entries(education_lines) == [
        ["Example University", "Computer Science, Bachelor of Science"],
        ["Mathematics, Bachelor of Arts"],
    ]


def test_groups_named_engineering_degrees_even_when_not_canonicalized():
    education_lines = [
        (
            "Master of Building Engineering \u2013 "
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
                "Master of Building Engineering \u2013 "
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
