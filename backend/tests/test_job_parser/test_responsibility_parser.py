from app.services.job_parsing.responsibility_parser import parse_responsibilities


def test_parse_responsibilities_cleans_bullets_and_duplicates():
    result = parse_responsibilities(
        {
            "responsibilities": [
                "- Build reliable APIs",
                "• Collaborate with engineers",
                "Build reliable APIs.",
            ]
        }
    )

    assert result == ["Build reliable APIs", "Collaborate with engineers"]


def test_parse_responsibilities_uses_actionable_overview_lines_as_fallback():
    result = parse_responsibilities(
        {
            "job_overview": [
                "You will build reliable APIs.",
                "Our team values curiosity.",
            ]
        }
    )

    assert result == ["You will build reliable APIs."]
