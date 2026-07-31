from app.services.parser.education_parser import detect_institution


def test_detects_university_as_institution():
    result = detect_institution("University of North Texas")

    assert result == "University of North Texas"


def test_detects_college_as_institution():
    result = detect_institution("Butler Community College")

    assert result == "Butler Community College"


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
    assert detect_institution(["  \u2022 University of North Texas  "]) == (
        "University of North Texas"
    )
